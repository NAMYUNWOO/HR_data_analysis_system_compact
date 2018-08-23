#-*- coding: utf-8 -*-
from django.shortcuts import render
from dataIO.forms import *
from functools import reduce
import django_excel as excel
import pandas as pd
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from index.models import *
from .fillData import  FillData,PreprocessData
import datetime
from django.db.models import Q
from urllib import parse
from .models import *
from django import db
import subprocess,re
import xgboost as xgb



def getDatelist(Model):
    if Model.__name__.endswith('log'):
        dt_= Model.objects.order_by("-eval_date")
        if dt_.count() == 0:
            return ["0개의 업데이트"]
        return [dt_.first().eval_date,dt_.last().eval_date]
    elif Model.__name__.endswith('EmailLog'):
        if EmailLog.objects.count() == 0:
            return [datetime.datetime(1,1,1),"0개의 업데이트"]
        return [EmailDateBeginEnd.objects.last().eval_date,"total " + str(EmailLog.objects.count())+" 개의 로그"]
    return list(Model.objects.order_by("-eval_date").values_list('eval_date', flat=True).distinct())


def lastUpdateDates(ModelList):
    zeroLenprocess = lambda x: ["0개의 업데이트"] if len(x) == 0 else x


    updateMat = [list(
                    map(lambda x: x if type(x) == str else str(x)[:10],
                        zeroLenprocess(
                            getDatelist2(Model)
                        )
                    )
                )for Model in ModelList
    ]
    # maximum length of element
    maxL = max(map(lambda x: len(x),updateMat))
    updateMatRslt = list(map(lambda x: x + ["-" for _ in range(maxL - len(x))] ,updateMat))
    return updateMatRslt

def getRecentUpdateDates():


    updateMat = lastUpdateDates(modelList())


    modelName = list(map(lambda x:x.__name__, modelList()))

    return [(name_i,date_i) for name_i,date_i in zip(modelName,updateMat)]





def getSingleModelFields(model,empObj,start_date, eval_date):

    if model == Employee:
        modelObj = empObj
    else:
        modelObj = model.objects.filter(Q(employeeID=empObj)& Q(start_date=start_date) & Q(eval_date=eval_date)).order_by("-eval_date").first()
    fieldNotUsing = ['id', 'employeeID', 'employeeID_confirm', 'eval_date','start_date', 'created_at']
    fieldNames = [mf.name for mf in model._meta.fields if mf.name not in fieldNotUsing]
    field_val_dic = {i:None for i in fieldNames}
    if modelObj == None:
        return field_val_dic
    for name_i in fieldNames:
        field_val_dic[name_i] = eval("modelObj."+name_i)
    """
    if model == EmployeeBiography:
        field_val_dic.update({"rewardyn":modelObj.rewardyn})
    """
    return field_val_dic

def getAllModelFields(models,empObj,start_date, eval_date):
    allModelFieldValue = list(map(lambda x: getSingleModelFields(x,empObj,start_date, eval_date),models))
    baseDic = {}
    for dic_i in allModelFieldValue:
        baseDic.update(dic_i)
    return {empObj.id:baseDic}

def getTable(models,start_date, eval_date,target=False):
    if target:
        employeeObject = Employee.objects.filter(istarget=True)
    else:
        employeeObject = Employee.objects.all()
    allEmployeeModelFieldValue = list(map(lambda x:getAllModelFields(models,x,start_date, eval_date),employeeObject))
    baseDic = {}
    for dic_i in allEmployeeModelFieldValue:
        baseDic.update(dic_i)
    empId = baseDic.keys()
    empId_values = list(baseDic.values())

    header = list(empId_values[0].keys())
    dfmat = [[row[col] for col in header ] for row in empId_values]
    df = pd.DataFrame(dfmat)
    df.columns = header
    df["id"] = list(empId)
    return df


def get_Bu_buUrl():
    bu = [list(i.values())[0] for i in list(EmployeeBiography.objects.values("bu").distinct()) if
          list(i.values())[0] != None]
    buUrl = [parse.quote(i) for i in bu]
    bu_buUrl = [(i, j) for i, j in zip(bu, buUrl)]
    return bu_buUrl

def placeencode(x):
    if x == "판교":
        return "pangyo"
    elif x == "포항":
        return "pohang"
    elif x == "광양":
        return "gwangyang"
    elif x == "센터":
        return "center"
    else:
        return "etc"

def _fillScoreData(df,start_date,eval_date):
    return True

def vacuumDB():
    from django.db import connection, transaction
    cursor = connection.cursor()
    cursor.execute("vacuum")
    transaction.commit()

def updateEmailDateBeginEnd(Model):
    ModelOrderby = Model.objects.order_by("eval_date")
    if ModelOrderby.count() == 0:
        try:
            LogFirstLast.objects.get(pk=Model.__name__).delete()
            return
        except:
            return
    logFirstLast= LogFirstLast.objects.filter(pk=Model.__name__)
    if logFirstLast.count() == 0:
        logFirstLast_i = LogFirstLast(modelName=Model.__name__,start_date = ModelOrderby.first().eval_date,end_date=ModelOrderby.last().eval_date)
        logFirstLast_i.save()
    else:
        logFirstLast.update(start_date = ModelOrderby.first().eval_date,end_date=ModelOrderby.last().eval_date)
    return

def dateRangeStr2datetime(dateRangeStr):
    start_date, eval_date = [datetime.datetime.strptime(dt, "%Y-%m-%d") for dt in map(lambda x: x.strip(), dateRangeStr.split("~"))]
    return [start_date, eval_date]

def getModelInstanceWithDateRange(Model,dateRangeStr=None,dateRange=None):
    if dateRangeStr:
        start_date, eval_date = dateRangeStr2datetime(dateRangeStr)
        modelInstances = Model.objects.filter(Q(start_date=start_date) & Q(eval_date=eval_date))
    if dateRange:
        start_date, eval_date = dateRange
        print(start_date,eval_date)
        print(Model)
        modelInstances = Model.objects.filter(Q(eval_date__gte=start_date) & Q(eval_date__lte=eval_date))

    return modelInstances


def dataIO(request):
    processedModels = [EmailData,Token_Data,VDI_Data,M_EPData,GatePassData]

    hrModels = [EmployeeBiography, EmployeeGrade, Education]

    logModels = [ EmailLog,Token_log ,VDI_log ,M_EP_log,GatePass_log]

    normalModels = [Target,Leadership]

    if request.method == 'GET':
        search_query = request.GET.get('search_box', None)
        if search_query != None:
            return HttpResponseRedirect(reverse('employee', args=[search_query]))

    if request.method == "POST":
        reqDict = dict(request.POST)
        reqKeyString = "&".join(list(reqDict.keys()))


        if 'input_' in reqKeyString:
            modelname = re.findall(r"input_([A-Z|a-z|_]*)",reqKeyString)[0]
            files = request.FILES.getlist('file')
            print(modelname+str(files))
            for idx, filehandle in enumerate(files):
                print(str(filehandle))
                fd = FillData(modelname, filePathName=filehandle)
                try:
                    fd.fillDB()
                except:
                    return render(request,"inputFail.html",{})
            return HttpResponseRedirect(reverse('dataIO'))
        elif 'inputWithDatetime_' in reqKeyString:
            modelname = re.findall(r"inputWithDatetime_([A-Z|a-z|_]*)", reqKeyString)[0]
            files = request.FILES.getlist('file')
            start_date = datetime.datetime(int(reqDict["start_date_year"][0]),int(reqDict["start_date_month"][0]),int(reqDict["start_date_day"][0]))
            end_date = datetime.datetime(int(reqDict["end_date_year"][0]),int(reqDict["end_date_month"][0]),int(reqDict["end_date_day"][0]))
            #print(modelname + str(files))
            for idx, filehandle in enumerate(files):
                print(str(filehandle))
                fd = FillData(modelname, filePathName=filehandle, start_date=start_date, end_date=end_date)
                fd.fillDB()
            return HttpResponseRedirect(reverse('dataIO'))

        elif 'output_' in reqKeyString:
            from poscoictsystem.settings import STATICFILES_DIRS
            outputPath = STATICFILES_DIRS[0] + "/excels/"
            modelname = re.findall(r"output_([A-Z|a-z|_]*)",reqKeyString)[0]
            updateList = getDatelist2(eval(modelname))
            selectedDate = int(reqDict['prefix'][0])
            dateRangeStr = updateList[selectedDate]
            start_date, eval_date = [datetime.datetime.strptime(dt, "%Y-%m-%d") for dt in
                                     map(lambda x: x.strip(), dateRangeStr.split("~"))]
            df = getTable([eval(modelname)],start_date,eval_date)
            df = df.fillna("NA")
            filename = modelname+"_"+dateRangeStr
            df.reindex_axis(sorted(df.columns), axis=1).to_csv(outputPath+filename,encoding='cp949')
            filetosend = open(outputPath+filename, 'r', encoding='cp949')
            response = HttpResponse(filetosend, content_type="text/csv", charset='cp949')
            response['Content-Disposition'] = "attachment; filename=%s.csv" % (filename)
            return response


        elif 'remove_' in reqKeyString:
            modelname = re.findall(r"remove_([A-Z|a-z|_]*)", reqKeyString)[0]
            updateList = getDatelist2(eval(modelname))
            selectedDate = int(reqDict['prefix'][0])
            if modelname == "EmployeeBiography":
                for hrmodel in hrModels:
                    modelname_i = hrmodel.__name__
                    modelInstances = getModelInstanceWithDateRange(eval(modelname_i), dateRangeStr=updateList[selectedDate])
                    modelInstances.delete()
            else:
                modelInstances = getModelInstanceWithDateRange(eval(modelname),dateRangeStr=updateList[selectedDate])
                modelInstances.delete()
            vacuumDB()


        elif 'removeWithDatetime_' in reqKeyString:
            modelname = re.findall(r"removeWithDatetime_([A-Z|a-z|_]*)", reqKeyString)[0]
            start_date = datetime.datetime(int(reqDict["start_date_year"][0]),int(reqDict["start_date_month"][0]),int(reqDict["start_date_day"][0]))
            end_date = datetime.datetime(int(reqDict["end_date_year"][0]),int(reqDict["end_date_month"][0]),int(reqDict["end_date_day"][0]))

            modelInstances = getModelInstanceWithDateRange(eval(modelname),dateRange=[start_date,end_date+datetime.timedelta(days=1)])
            modelInstances.delete()
            updateEmailDateBeginEnd(eval(modelname))
            vacuumDB()


        elif 'preprocess_' in reqKeyString:
            modelname = re.findall(r"preprocess_([A-Z|a-z|_]*)", reqKeyString)[0]
            start_date = datetime.datetime(int(reqDict["start_date_year"][0]),int(reqDict["start_date_month"][0]),int(reqDict["start_date_day"][0]))
            end_date = datetime.datetime(int(reqDict["end_date_year"][0]),int(reqDict["end_date_month"][0]),int(reqDict["end_date_day"][0]))
            print("preprocess "+modelname + " from " + str(start_date) + " to " + str(end_date))
            preprocessData = PreprocessData(eval(modelname),start_date,end_date)
            if not preprocessData.runPreprocess2():
                preprocessData.runPreprocess()


        elif "getTestData" in reqKeyString:
            from poscoictsystem.settings import STATICFILES_DIRS
            import zipfile, os, io
            testDataPath = STATICFILES_DIRS[0] + "/testData/"
            zip_subdir = "testData"
            zip_filename = "%s.zip" % zip_subdir
            filenames = os.listdir(testDataPath)
            b = io.BytesIO()
            zf = zipfile.ZipFile(b, "w")
            for fpath in filenames:
                fpath = testDataPath + fpath
                fdir, fname = os.path.split(fpath)
                zip_path = os.path.join(zip_subdir, fname)
                zf.write(fpath, zip_path)
            zf.close()
            resp = HttpResponse(b.getvalue(), content_type="application/zip")
            resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
            return resp
        elif "analysis" in reqKeyString:
            MODELS_TO_ANALYSIS = [Target,Leadership,EmployeeBiography,EmployeeGrade,Education,EmailData,Token_Data,VDI_Data,M_EPData]
            df_to_Analysis = pd.DataFrame()
            df_to_predict = pd.DataFrame()
            for model_i, pref in zip(MODELS_TO_ANALYSIS,reqDict['prefix']):
                updateList = getDatelist2(model_i)
                selectedDate = int(pref)
                modelInstances = getModelInstanceWithDateRange(model_i, dateRangeStr=updateList[selectedDate])
                model_val = modelInstances.values()
                header =model_val[0].keys()
                df_model = pd.DataFrame(list(map(lambda x : list(x.values()),model_val)),columns=header)
                if model_i == Target:
                    df_to_Analysis = df_model
                else:
                    df_to_Analysis = pd.merge(df_to_Analysis,df_model,how="left",on="employeeID_id")
                    if len(df_to_predict) == 0:
                        df_to_predict = df_model
                    else:
                        df_to_predict = pd.merge(df_to_predict, df_model, how="outer", on="employeeID_id")
            df_to_Analysis = df_to_Analysis.drop_duplicates("employeeID_id")
            df_to_predict = df_to_predict.drop_duplicates("employeeID_id")
            cols2Select = ["employeeID_id","grade_co_r3_avg","holiday","edu_course_cnt","edu_course_time","sendCnt_byLevelRatio",
             "sendCnt_nwh_byLevelRatio","receiveCnt_byLevelRatio","nodeSize_byLevelRatio","nodeSize_byGroupRatio",
             "token_receive_byLevelRatio","mep_early_byLevelRatio","mep_late_byLevelRatio","vdi_early_byLevelRatio",
             "vdi_late_byLevelRatio","leadership_env_job","leadership_env","leadership_env_common","isTarget"]
            df_to_Analysis = df_to_Analysis[cols2Select]
            df_to_Analysis = df_to_Analysis.fillna(df_to_Analysis.mean())
            df_to_Analysis.index = range(len(df_to_Analysis))
            df_to_Analysis["early_work"]= (df_to_Analysis.mep_early_byLevelRatio + df_to_Analysis.vdi_early_byLevelRatio)/2
            df_to_Analysis["late_work"]= (df_to_Analysis.mep_late_byLevelRatio + df_to_Analysis.vdi_late_byLevelRatio)/2
            df_to_Analysis = df_to_Analysis.drop(["mep_early_byLevelRatio","vdi_early_byLevelRatio","mep_late_byLevelRatio","vdi_late_byLevelRatio"],1)
            df_to_predict = df_to_predict[cols2Select[:-1]]
            df_to_predict = df_to_predict.fillna(df_to_predict.mean())
            clf = xgb.XGBClassifier(learning_rate=0.1, n_estimators=1000, max_depth=2, \
                                    min_child_weight=1, gamma=0, subsample=1, colsample_bytree=1)
            clf.fit(df_to_Analysis.drop(["isTarget","employeeID_id"], 1).values, df_to_Analysis.isTarget.values)
            from . import xgb_explainer as xgb_exp

            dtrain = xgb.DMatrix(data=df_to_Analysis.drop(["isTarget","employeeID_id"], 1).astype(np.float64), label=df_to_Analysis.isTarget.values)
            params = {"subsample": 1, "colsample_bytree": 1, "gamma": 0, "max_depth": 2, 'silent': 1,
                      "min_child_weight": 1, "lambda": 1}
            best_iteration = 1000
            bst = xgb.train(params=params, num_boost_round=best_iteration, dtrain=dtrain)
            tree_lst = xgb_exp.model2table(bst, lmda=1.0)
            feature_names = dtrain.feature_names
            scores = []
            for i in df_to_Analysis.index:
                row = []
                sample = xgb.DMatrix.slice(dtrain, [i])
                sample.feature_names = feature_names
                empid = df_to_Analysis.iloc[i].employeeID_id
                pred= bst.predict(sample)[0]
                row.append(empid)
                row.append(pred)

                leaf_lst = bst.predict(sample, pred_leaf=True)
                dist = xgb_exp.logit_contribution(tree_lst, leaf_lst[0])
                row.append(dist['intercept'])
                for f_name in feature_names:
                    try:
                        row.append(dist[f_name])
                    except:
                        row.append(0.0)
                today = datetime.datetime.today()
                dt =datetime.date(today.year,today.month,today.day)
                dist.update({"employeeID_confirm":empid,"employeeID":Employee.objects.get(id=empid),"predict":pred,
                             "eval_date":dt,"start_date":dt})
                scorei = Score(**dist)
                scores.append(scorei)
                #result_mtx.append(row)
            cols = ["ID", "predict","intercept"] + list(feature_names)
            Score.objects.bulk_create(scores)
            #analysis_result = pd.DataFrame(result_mtx,columns=cols)
            #analysis_result.to_excel("rslt.xlsx")
        return HttpResponseRedirect(reverse('dataIO'))
    else:
        db.connections.close_all()

        processedDataSelects = [StructuredDataSelect(model=processedModel) for processedModel in processedModels]

        logDataSelects = [LogDataSelect(model=logmodel) for logmodel in logModels]

        hrDataSelects = [StructuredDataSelect(model = hrmodel)  for  hrmodel in hrModels]

        normalDataSelects = [StructuredDataSelect(model=normalmodel) for normalmodel in normalModels]

        scoreDataSelects = [StructuredDataSelect(model = Score)]


    context = {  'bu': get_Bu_buUrl(),
                 "recentUpdateDate": getRecentUpdateDates(),
                 'processedDataSelects':processedDataSelects,
                 'normalDataSelects':normalDataSelects,
                 'hrDataSelects':hrDataSelects,
                 'scoreDataSelects':scoreDataSelects,
                 'logDataSelects':logDataSelects,
                 'title': 'Excel file upload and download example',
                 'header': ('Please choose any excel file ' +
                            'from your cloned repository:')
                 }
    return render(request,'dataIO.html',context)















