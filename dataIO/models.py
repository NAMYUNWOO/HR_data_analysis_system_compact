from django.db import models
from index.models import *
# Create your models here.
def modelList():
    modellist = [EmployeeBiography , EmployeeGrade, Education, Leadership,
                 Token_Data,Token_log,VDI_Data,VDI_log,EmailData, EmailLog]

    return modellist


def getDatelist2(Model):
    if Model.__name__.lower().endswith("log"):
        try:
            logfirstlast = LogFirstLast.objects.get(pk=Model.__name__)
            return [str(logfirstlast.start_date)[:10] + " ~ " + str(logfirstlast.end_date)[:10]]
        except:
            return ["0개의 업데이트"]
    else:
        evaldate_startdate = Model.objects.order_by("-eval_date").values_list('eval_date', 'start_date').distinct()
        return list(map(lambda x: str(x[1])[:10] + " ~ " + str(x[0])[:10], evaldate_startdate))



def lastUpdateDates2(ModelList):
    zeroLenprocess = lambda x: ["0개의 없데이트"] if len(x) == 0 else x
    updateMat = [zeroLenprocess(getDatelist2(Model)) for Model in ModelList]
    return updateMat


def getRecentUpdateDates2():
    modelName = list(map(lambda x: x.__name__, modelList()))
    updateMat = lastUpdateDates2(modelList())
    logData = []
    hrData = []
    processedData = []
    scoreData = []
    for name_i, date_i in zip(modelName, updateMat):
        if 'score' in name_i.lower():
            scoreData.append((name_i, date_i))
            continue
        if name_i.endswith('log') or name_i.endswith('EmailLog'):
            logData.append((name_i, date_i))
        else:
            if 'data' in name_i.lower() or 'flow' in name_i.lower():
                processedData.append((name_i, date_i))
            else:
                hrData.append((name_i,date_i))
    return (logData,processedData,hrData,scoreData)


def ifexistDel(model,empObj,eval_date,start_date):
    isExists = model.objects.filter(Q(employeeID=empObj) & Q(eval_date=eval_date) & Q(start_date=start_date))
    if isExists.count() != 0:
        isExists.delete()
