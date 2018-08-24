#-*- coding: utf-8 -*-
import pandas as pd
from django.db.models import Q,F, Sum, Count, Case, When, Avg, Func,ExpressionWrapper,DurationField
from index.models import *
import datetime
import re,os,time
import numpy as np
import json
from django.db.models.functions import TruncMonth, TruncDay
from inspect import ismethod
from django import db
import networkx as nx
import copy
from .Preprocess_EmailLog import preprocess_EmailLog
from .Preprocess_GatePass_log import preprocess_GatePass_log
from .Preprocess_M_EP_log import preprocess_M_EP_log
from .Preprocess_Token_log import preprocess_Token_log
from .Preprocess_VDI_log import preprocess_VDI_log
TEMPEVAL_DATE = datetime.datetime.today()

class EmailGraphProcess:
    networksJson = {}
    centralityJson = {}

    def __init__(self,start_date,eval_date):
        self.start_date = start_date
        self.eval_date = eval_date
        self.setNetworks()
        self.setCentralities()

    def getGraph(self,querySet):
        emailcount = querySet.values("sendID","receiveID").annotate(weight = Count("sendID")).values("sendID","receiveID","weight")
        g = nx.DiGraph()
        for em in emailcount:
            node1 = em["sendID"]
            node2 = em["receiveID"]
            weight = em["weight"]
            g.add_edge(node1,node2,weight=weight)
        return g
    def setNetworks(self):
        self.emplevels = sorted(list(Employee.objects.values_list("level", flat=True).distinct()))
        emailCnctObj = EmailLog.objects.filter(Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))
        g_all = self.getGraph(emailCnctObj)
        self.networksJson.update({"all":g_all})
        for empLevel in self.emplevels:
            emailCnctObj_sangsa = EmailLog.objects.filter(((Q(receiveID__level=empLevel) & Q(sendID__level__lt=empLevel)) | (Q(sendID__level=empLevel) & Q(receiveID__level__lt=empLevel))) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))
            emailCnctObj_dongryo = EmailLog.objects.filter(Q(receiveID__level=empLevel) & Q(sendID__level=empLevel) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))
            emailCnctObj_buha = EmailLog.objects.filter(((Q(receiveID__level=empLevel) & Q(sendID__level__gt=empLevel)) | (Q(sendID__level=empLevel) & Q(receiveID__level__gt=empLevel))) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))

            g_s = self.getGraph(emailCnctObj_sangsa)
            g_d = self.getGraph(emailCnctObj_dongryo)
            g_b = self.getGraph(emailCnctObj_buha)
            self.networksJson.update({str(empLevel)+"_sangsa": g_s})
            self.networksJson.update({str(empLevel) + "_dongryo": g_d})
            self.networksJson.update({str(empLevel) + "_buha": g_b})

    def getCentrality(self,cenType,g):
        """
        nodeSize = 500
        if g.number_of_nodes() < nodeSize:
        """
        nodeSize = g.number_of_nodes()
        if nodeSize == 0:
            return {"-1":0}
        if cenType == "betweenness":
            return nx.betweenness_centrality(g,nodeSize)
        if cenType == "eigenvector":
            return nx.eigenvector_centrality(g,max_iter=1000)


    def setCentralities(self):
        groups = ["sangsa","dongryo","buha"]
        centralityType = ["betweenness","eigenvector"]
        for group in groups:
            for empLevel in self.emplevels:
                for centrality_i in centralityType:
                    cen_i = self.getCentrality(centrality_i,self.networksJson[str(empLevel)+"_"+group])
                    self.centralityJson.update({str(empLevel)+"_"+group+"_"+centrality_i:cen_i})

        for centrality_i in centralityType:
            cen_i = self.getCentrality(centrality_i, self.networksJson["all"])
            self.centralityJson.update({"all_"+centrality_i:cen_i})



class PreprocessData:
    def __init__(self,inputModel, start_date, eval_date):

        self.start_date = start_date
        self.eval_date = eval_date
        self.inputModel = inputModel
        self.log_data = {
                            EmailLog:EmailData,
                            Token_log:Token_Data,
                            VDI_log:VDI_Data,
                            M_EP_log:M_EPData,
                            GatePass_log : GatePassData,
                            Approval_log: ApprovalData,
                            PCM_log: PCMData,
                            TMS_log: TMSData,
                            EP_log: EPData,
                            Meeting_log: MeetingData,
                            Thanks_log: Thanks_Data,
                            Portable_out_log: Portable_out_Data,
                            IMS_log: IMSData,
                            PC_control_log: PC_control_Data,
                            PC_out_log: PC_out_Data,
                            Blog_log: BlogData,
                            Cafeteria_log: CafeteriaData,
                            ECM_log: ECMData
                        }
        self.preprocess_func_hash = {
            EmailLog : preprocess_EmailLog,
            Token_log : preprocess_Token_log,
            VDI_log : preprocess_VDI_log,
            M_EP_log:preprocess_M_EP_log,
            GatePass_log:preprocess_GatePass_log
        }
        """
        # useless
        {
            Approval_log:ApprovalData,
            PCM_log:PCMData,
            TMS_log:TMSData,
            EP_log:EPData,
            Meeting_log:MeetingData,
            Thanks_log:Thanks_Data,
            Portable_out_log:Portable_out_Data,
            IMS_log:IMSData,
            PC_control_log:PC_control_Data,
            PC_out_log:PC_out_Data,
            Blog_log:BlogData,
            Cafeteria_log:CafeteriaData,
            ECM_log:ECMData
        }
        """
        if inputModel in self.log_data.values():
            self.Model = inputModel
        else:
            self.Model = self.log_data[inputModel]


        """
        # useless EmailGraph
        if self.Model == EmailData:
            self.egp = EmailGraphProcess(start_date=start_date,eval_date=eval_date)
        """
    """
    def getSnaData(self, empId, myDict=None, graph=None):
        closeness_indegree_outDegree = [None, None, None]
        if graph != None:
            try:
                closeness_indegree_outDegree[0] = nx.closeness_centrality(graph, empId)
            except:
                pass
            try:
                closeness_indegree_outDegree[1] = graph.in_degree(empId)
            except:
                pass
            try:
                closeness_indegree_outDegree[2] = graph.out_degree(empId)
            except:
                pass
            return closeness_indegree_outDegree
        try:
            rslt = myDict[empId]
            return rslt
        except:
            return None
    """
    def runPreprocess2(self):
        preprocess_func = self.preprocess_func_hash.get(self.inputModel,None)
        if preprocess_func == None:
            return False
        preprocess_func(self.inputModel,self.Model,(self.start_date,self.eval_date))
        return True


    def runPreprocess(self):
        instance_i_list = []
        empList = list(Employee.objects.all().order_by("level").values_list('id', flat=True))
        for id_i in empList:
            print(id_i, end="\r")
            empObj = Employee.objects.get(pk=id_i)

            isExists = self.Model.objects.filter(Q(employeeID=empObj) & Q(eval_date=self.eval_date) & Q(start_date=self.start_date))
            if isExists.count() != 0:
                isExists.delete()
            instance_i = self.Model(employeeID=empObj, employeeID_confirm=id_i, start_date=self.start_date,eval_date=self.eval_date)
            attrs = []
            for name in dir(instance_i):
                try:
                    attrs.append(getattr(instance_i, name))
                except:
                    continue
            __methods = list(filter(lambda x: ismethod(x), attrs))
            methods = list(filter(lambda x: x.__name__.startswith("posco_set"), __methods))
            for method in methods:
                method()
            instance_i_list.append(instance_i)
        self.Model.objects.bulk_create(instance_i_list)
        return True


class FillData:
    """
     LOG Data Input
    """
    def __init__(self,modelName,filePathName=None,start_date=None,end_date=None):


        db.connections.close_all()
        fileStr = str(filePathName).split(".")
        self.modelName = modelName
        self.fileType = fileStr[1]
        self.isDF = False
        self.eval_date = end_date
        self.start_date = start_date
        self.filePathName = filePathName
        if filePathName and self.__dataframeSetter(filePathName,self.modelName.lower().startswith("email")):
            self.isDF = True
        else:
            print("incorrect Input")

    def fillDB(self):
        if self.filePathName and not self.isDF:
            print("DataFrame is not loaded")
            return False

        modelname_method = {
            "EmployeeBiography": self._fillHRdata
            , "EmailLog": self._fillEmailData
            , "VDI_log": self._fillVdiData
            , "Token_log": self._fillTokenData
            , 'M_EP_log': self._fillMEPData
            , 'GatePass_log': self._fillGatePassData
            , 'Leadership':self._fillLeaderShipData
            , "Target":self._fillTargetData
        }

        # updateUselessModel
        """
        modelname_method.update({"Approval_log": self._fillApprovalData
        , "Education": self._fillEducationData
        , "EmployeeGrade": self._fillGradeData
        , "Blog_log":  self._fillBlogData
        , "Cafeteria_log": self._fillCafeteriaData
        , "ECM_log": self._fillEcmData
        , "IMS_log": self._fillImsData
        , "PC_control_log": self._fillPcControlData
        , "PC_out_log": self._fillPcOutData
        , "Portable_out_log": self._fillPortableOutData
        , "Reward_log": self._fillRewardData
        , "Score": self._fillScoreData
        , "Survey": self._fillSurveyData
        , "Thanks_log": self._fillThanksData
        , "Trip": self._fillTripData
        , "VDI_indi_log": self._fillVdiIndiData
        , "VDI_share_log": self._fillVdiShareData
        , "Meeting_log":self._fillMeetingData
        ,'EP_log':self._fillEPData
        ,'PCM_log':self._fillPCMData
        , 'TMS_log':self._fillTMSData})
        """
        methodToProcessData = modelname_method[self.modelName]
        methodToProcessData()

    def csvfileToDataFrame(self,filePathName):
        encodings = ["cp949","utf-8","euc-kr"]
        filePathName_ = copy.copy(filePathName)
        file_read = filePathName_.read()
        for encoding_i in encodings:
            try:
                file_data = file_read.decode(encoding_i)
                lines = file_data.split("\n")
                lines = list(map(lambda row: row.strip().split(","), lines))
                header = lines[0]
                rows = lines[1:]
                df = pd.DataFrame(data=rows, columns=header)
                print(header)
                return df
            except:
                pass
        return  pd.DataFrame([])

    def __dataframeSetter(self,filePathName,isemail):
        if isemail:
            try:
                self.df = pd.read_csv(filePathName, index_col=False,encoding="utf-8")
                return True
            except:
                self.df = pd.read_csv(filePathName, index_col=False,encoding='cp949')
                return True
        try:
            if self.fileType.startswith("xls"):
                self.df = pd.read_excel(filePathName,encoding="utf-8")
                self.df = self.df.where((pd.notnull(self.df)), None)
            elif self.fileType == "csv":
                self.df = self.csvfileToDataFrame(filePathName)
                #self.df = pd.read_csv(filePathName,encoding="utf-8")
                #self.df = self.df.where((pd.notnull(self.df)), None)
            return True
        except:
            pass

        try:
            if self.fileType.startswith("xls"):
                self.df = pd.read_excel(filePathName, encoding="cp949")
                self.df = self.df.where((pd.notnull(self.df)), None)
            elif self.fileType == "csv":
                self.df = pd.read_csv(filePathName, encoding="cp949")
                self.df = self.df.where((pd.notnull(self.df)), None)
            return True
        except:
            pass

        try:
            if self.fileType.startswith("xls"):
                self.df = pd.read_excel(filePathName, encoding="euc-kr")
                self.df = self.df.where((pd.notnull(self.df)), None)
            elif self.fileType == "csv":
                self.df = pd.read_csv(filePathName, encoding="euc-kr")
                self.df = self.df.where((pd.notnull(self.df)), None)
            return True
        except:
            return False

    def _fillHRdata(self):
        self._fillBiographyData()
        self._fillEducationData()
        self._fillGradeData()

    def __strEval_date_converter(self,eval_date):
        global TEMPEVAL_DATE
        try:
            eval_date = re.sub("/","-",eval_date)
            try:
                eval_date_ = re.findall("[0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}", eval_date)[0]
            except:
                eval_date_ = re.findall("[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}[.]*", eval_date)[0]
        except:
            return TEMPEVAL_DATE


        if len(eval_date_) >= 11:
            TEMPEVAL_DATE = datetime.datetime.strptime(eval_date_.strip(), "%Y-%m-%d %H:%M:%S")
            return TEMPEVAL_DATE
        else:
            TEMPEVAL_DATE = datetime.datetime.strptime(eval_date_.strip(), "%Y-%m-%d")
            return TEMPEVAL_DATE


    def _fillBiographyData(self):
        noneisZero = lambda x:0 if x == None else x
        def placeExtract(place):
            place = str(place)
            if "센" in place:
                return "센터"
            if "판교" in place:
                return "판교"
            if "분당" in place:
                return "판교"
            if "포항" in place:
                return "포항"
            if "광양" in place:
                return "광양"
            if "서울" in place:
                return "서울"
            return "etc"

        EmployeeBiography_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            id_ = int(df_instance["id"])
            bu = df_instance.bu
            place = placeExtract(df_instance.place)
            email = df_instance.email
            name = df_instance['name']
            holiday = df_instance.holiday
            try:
                level = int(re.findall('[0-9]{1}',df_instance.level)[0])
            except:
                level = 0
            """ not using
            age = df_instance.age
            coreyn = bool(df_instance.coreyn)
            sex = df_instance.sex.startswith("남")
            work_duration = df_instance.work_duration
            istarget = bool(df_instance.istarget)
            pmlevel = noneisZero(df_instance.pmlevel)
            """
            employee_i = Employee.objects.filter(pk=id_)
            if employee_i.count() == 0:
                emp = Employee(id= id_,bu=bu, place=place,empname=name,level = level,email=email)
                emp.save()
            else:
                emp = Employee.objects.filter(pk=id_).update(level=level,bu=bu,place = place ,email=email,empname=name)
            empBio = EmployeeBiography(employeeID = Employee.objects.get(pk=id_),employeeID_confirm = id_ ,bu=bu,
                                       place=place,empname=name,start_date= self.start_date ,eval_date = self.eval_date,
                                       level = level,email=email,holiday=holiday)
            EmployeeBiography_list.append(empBio)
        EmployeeBiography.objects.bulk_create(EmployeeBiography_list)

        return True

    def _fillGradeData(self):
        employeeGrade_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            employeeID_ = df_instance.id
            gradeHash1 = {"s":6,"a":5,"b+":4,"b-":3,"c":2,"d":1,"S":6,"A":5,"B+":4,"B-":3,"C":2,"D":1,None:None}
            try:
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue
            employeeID_confirm = df_instance.id
            grade_sv_y_1 = df_instance.grade_sv_y_1
            grade_sv_y_2 = df_instance.grade_sv_y_2
            grade_sv_y_3 = df_instance.grade_sv_y_3
            grade_co_y_1 = df_instance.grade_co_y_1
            grade_co_y_2 = df_instance.grade_co_y_2
            grade_co_y_3 = df_instance.grade_co_y_2
            grade_1 = gradeHash1.get(df_instance.grade_1,None)
            grade_2 = gradeHash1.get(df_instance.grade_2,None)
            grade_3 = gradeHash1.get(df_instance.grade_3,None)
            grade_4 = gradeHash1.get(df_instance.grade_4,None)
            grade_5 = gradeHash1.get(df_instance.grade_3,None)
            grade_6 = gradeHash1.get(df_instance.grade_4,None)
            empGrade = EmployeeGrade(employeeID=employeeID, employeeID_confirm=employeeID_confirm,
                                     grade_sv_y_1=grade_sv_y_1, grade_sv_y_2=grade_sv_y_2,grade_sv_y_3=grade_sv_y_3,
                                     grade_co_y_1=grade_co_y_1, grade_co_y_2=grade_co_y_2, grade_co_y_3=grade_co_y_3,
                                     grade_1=grade_1,grade_2=grade_2,grade_3=grade_3,
                                     grade_4=grade_4,grade_5=grade_5,grade_6=grade_6,
                                     eval_date=self.eval_date, start_date = self.start_date)
            empGrade.posco_set_grade_r3_avg()
            empGrade.posco_set_grade_sv_r3_avg()
            empGrade.posco_set_grade_co_r3_avg()
            employeeGrade_list.append(empGrade)
        EmployeeGrade.objects.bulk_create(employeeGrade_list)
        return True


    def _fillEducationData(self):
        education_list = []
        noneIsZero = lambda x: 0 if x == None else x
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            employeeID_ = df_instance.id
            try:
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue
            employeeID_confirm = df_instance.id
            edu_course_cnt = noneIsZero(df_instance.edu_course_cnt)
            empEdu = Education(employeeID=employeeID, employeeID_confirm=employeeID_confirm,edu_course_cnt = edu_course_cnt,
                               eval_date=self.eval_date, start_date = self.start_date)

            education_list.append(empEdu)
        Education.objects.bulk_create(education_list)
        return True

    def _fillLeaderShipData(self):
        Leadership_list = []
        def floatOrNan(x):
            try:
                return float(x)
            except:
                return np.NaN
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]

            try:
                employeeID_ = int(df_instance.id)
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue
            employeeID_confirm = employeeID_
            leadership_env_job = floatOrNan(df_instance.leadership_env_job)
            leadership_env = floatOrNan(df_instance.leadership_env)
            leadership_env_common = floatOrNan(df_instance.leadership_env_common)
            leadershipObj = Leadership(employeeID=employeeID,employeeID_confirm=employeeID_confirm,
                                leadership_env_job=leadership_env_job,leadership_env = leadership_env,
                                leadership_env_common=leadership_env_common,eval_date=self.eval_date, start_date = self.start_date)

            Leadership_list.append(leadershipObj)
        Leadership.objects.bulk_create(Leadership_list)
        return True

    def _fillTargetData(self):
        Target_list = []
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]

            try:
                employeeID_ = int(df_instance.id)
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue
            employeeID_confirm = employeeID_
            isT = int(df_instance.target)
            if isT != 0 and isT != 1:
                continue
            TargetObj = Target(employeeID=employeeID,employeeID_confirm=employeeID_confirm,
                               isTarget = bool(isT),eval_date=self.eval_date, start_date = self.start_date)

            Target_list.append(TargetObj)
        Target.objects.bulk_create(Target_list)
        return True


    def _fillEmailData(self):
        module_dir = os.path.dirname(__file__)
        file_path = os.path.join(module_dir, 'holiday.json')
        holiday_ = open(file_path).read()
        holidayHash = json.loads(holiday_)
        def emailextractor(x):
            try:
                x1 = re.sub("[가-힣|\>|\<|' '*|;]", " ", str(x))
                return re.findall("[^' ']*@[^' ']*", x1)
            except:
                return [""]
        emailHash = {i:j for i,j in list(Employee.objects.values_list("email","id").distinct())}
        success = False
        self.df.columns = ["col" + str(i) for i in range(len(self.df.columns))]
        self.df = self.df[self.df.col0 == "보낸메일함"]
        self.df.index = range(len(self.df))
        senders = self.df.col1
        seval_date = self.df.col2
        receivers = self.df[["col4", "col5", "col6"]]
        senders = senders.map(lambda x: emailextractor(x))
        receivers = receivers.applymap(lambda x: emailextractor(x))
        receivers = receivers.col4 + receivers.col5 + receivers.col6
        try:
            logFirstLast = LogFirstLast.objects.get(pk=EmailLog.__name__)
            earlyDate = logFirstLast.start_date
            recentDate = logFirstLast.end_date
        except:
            emailLogFirstLast = LogFirstLast(modelName = EmailLog.__name__, start_date = datetime.datetime(9999,1,1), end_date = datetime.datetime(1,1,1))
            emailLogFirstLast.save()
            logFirstLast = LogFirstLast.objects.get(pk=EmailLog.__name__)
            earlyDate = logFirstLast.start_date
            recentDate = logFirstLast.end_date

        if type(seval_date[0]) == str:
            seval_date = seval_date.map(lambda x: self.__strEval_date_converter(x))
        empEmailLog_list = []
        for i in range(len(senders)):
            if len(receivers[i]) == 0 or len(senders[i]) == 0:
                continue
            try:
                sendID_ = emailHash[senders[i][0].strip()]
            except:
                continue
            for receiver in receivers[i]:
                try:
                    receiveID_ = emailHash[receiver]
                except:
                    continue
                try:
                    sendID = Employee.objects.get(id=sendID_)
                    receiveID = Employee.objects.get(id=receiveID_)
                except:
                    continue
                eval_date = seval_date[i]
                nwh = False
                YMD = str(eval_date.year)+"-"+str(eval_date.month)+"-"+str(eval_date.day)
                if holidayHash.get(YMD,False) or eval_date.hour > 20 or eval_date.hour < 8:
                    nwh = True

                empEmailLog = EmailLog(sendID=sendID, receiveID=receiveID, eval_date=eval_date,nwh=nwh)
                empEmailLog_list.append(empEmailLog)
                earlyDate = min(earlyDate,eval_date)
                recentDate = max(eval_date,recentDate)
                success = True
        if not success:
            return False
        EmailLog.objects.bulk_create(empEmailLog_list)
        LogFirstLast.objects.filter(pk=EmailLog.__name__).update(start_date = earlyDate, end_date = recentDate)
        return True


    def _fillMEPData(self):
        mep_list = []


        try:
            logFirstLast = LogFirstLast.objects.get(pk=M_EP_log.__name__)
            earlyDate = logFirstLast.start_date
            recentDate = logFirstLast.end_date
        except:
            emailLogFirstLast = LogFirstLast(modelName = M_EP_log.__name__, start_date = datetime.datetime(9999,1,1), end_date = datetime.datetime(1,1,1))
            emailLogFirstLast.save()
            logFirstLast = LogFirstLast.objects.get(pk=M_EP_log.__name__)
            earlyDate = logFirstLast.start_date
            recentDate = logFirstLast.end_date

        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            try:
                employeeID_ = int(df_instance.id)
                employeeID = Employee.objects.get(id=int(employeeID_))
            except:
                continue
            if type(df_instance.eval_date) == str:
                eval_date = self.__strEval_date_converter(df_instance.eval_date)
            else:
                eval_date = df_instance.eval_date
            earlyDate = min(earlyDate, eval_date)
            recentDate = max(eval_date, recentDate)
            mep_i = M_EP_log(employeeID = employeeID,eval_date=eval_date)
            mep_list.append(mep_i)
        M_EP_log.objects.bulk_create(mep_list)
        LogFirstLast.objects.filter(pk=M_EP_log.__name__).update(start_date=earlyDate, end_date=recentDate)
        return True


    def _fillVdiData(self):
        success = False
        vdi_log_obj_list = []
        try:
            logFirstLast = LogFirstLast.objects.get(pk=VDI_log.__name__)
            earlyDate = logFirstLast.start_date
            recentDate = logFirstLast.end_date
        except:
            emailLogFirstLast = LogFirstLast(modelName = VDI_log.__name__, start_date = datetime.datetime(9999,1,1), end_date = datetime.datetime(1,1,1))
            emailLogFirstLast.save()
            logFirstLast = LogFirstLast.objects.get(pk=VDI_log.__name__)
            earlyDate = logFirstLast.start_date
            recentDate = logFirstLast.end_date
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            employeeID_ = df_instance.id
            try:
                employeeID = Employee.objects.get(id=employeeID_)
            except:
                continue

            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)
            earlyDate = min(earlyDate, eval_date)
            recentDate = max(eval_date, recentDate)
            vdi_log_obj = VDI_log(employeeID=employeeID,eval_date=eval_date)
            vdi_log_obj_list.append(vdi_log_obj)
            success = True
        if not success:
            return False
        VDI_log.objects.bulk_create(vdi_log_obj_list)
        LogFirstLast.objects.filter(pk=VDI_log.__name__).update(start_date=earlyDate, end_date=recentDate)
        return True

    def _fillTokenData(self):
        token_log_list = []
        self.df["type"] = self.df["type"].map(lambda x : x.strip())
        self.df = self.df[self.df["type"] == "감사토큰"]
        print(self.df)
        try:
            logFirstLast = LogFirstLast.objects.get(pk=Token_log.__name__)
            earlyDate = logFirstLast.start_date
            recentDate = logFirstLast.end_date
        except:
            emailLogFirstLast = LogFirstLast(modelName = Token_log.__name__, start_date = datetime.datetime(9999,1,1), end_date = datetime.datetime(1,1,1))
            emailLogFirstLast.save()
            logFirstLast = LogFirstLast.objects.get(pk=Token_log.__name__)
            earlyDate = logFirstLast.start_date
            recentDate = logFirstLast.end_date
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            token_sendID_ = df_instance.sendID
            token_receiveID_ = df_instance.receiveID
            eval_date = df_instance.eval_date
            if type(eval_date) == str:
                eval_date = self.__strEval_date_converter(eval_date)
            earlyDate = min(earlyDate, eval_date)
            recentDate = max(eval_date, recentDate)
            try:
                sendID = Employee.objects.get(id=int(token_sendID_))

            except:
                continue
            try:
                receiveID_raw = re.findall("[0-9]+", token_receiveID_)[0]
                receiveID = Employee.objects.get(id= int(receiveID_raw))
            except:
                continue
            tokenlog = Token_log(sendID =sendID,receiveID=receiveID,eval_date=eval_date)
            token_log_list.append(tokenlog)
        Token_log.objects.bulk_create(token_log_list)
        LogFirstLast.objects.filter(pk=Token_log.__name__).update(start_date=earlyDate, end_date=recentDate)
        return True

    def _fillGatePassData(self):
        gatepass_list = []
        try:
            logFirstLast = LogFirstLast.objects.get(pk=GatePass_log.__name__)
            earlyDate = logFirstLast.start_date
            recentDate = logFirstLast.end_date
        except:
            emailLogFirstLast = LogFirstLast(modelName = GatePass_log.__name__, start_date = datetime.datetime(9999,1,1), end_date = datetime.datetime(1,1,1))
            emailLogFirstLast.save()
            logFirstLast = LogFirstLast.objects.get(pk=GatePass_log.__name__)
            earlyDate = logFirstLast.start_date
            recentDate = logFirstLast.end_date
        for i in range(len(self.df)):
            df_instance = self.df.iloc[i, :]
            try:
                employeeID_ = int(df_instance.id)
                employeeID = Employee.objects.get(id=int(employeeID_))
            except:
                continue
            yyyymmdd = "-".join(re.findall('[0-9]+', df_instance.eval_date1))
            hhmmss = ":".join(re.findall("[0-9]+", df_instance.eval_date2))
            eval_date_ = yyyymmdd.strip()+" "+hhmmss.strip()
            eval_date = self.__strEval_date_converter(eval_date_)
            earlyDate = min(earlyDate, eval_date)
            recentDate = max(eval_date, recentDate)
            isIn = "입실" in df_instance.eventtype
            gpl = GatePass_log(employeeID = employeeID,eval_date = eval_date,isIn = isIn)
            gatepass_list.append(gpl)
        GatePass_log.objects.bulk_create(gatepass_list)
        LogFirstLast.objects.filter(pk=GatePass_log.__name__).update(start_date=earlyDate, end_date=recentDate)
        return True
