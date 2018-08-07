from django.shortcuts import render
import time
import random
from django.views.generic import View
from index.models import *
from django.db.models import F, Sum, Count, Case, When, Avg, Func
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.db.models import Q
import datetime
from django.http import HttpResponseRedirect, HttpResponse
from jchart import Chart
from jchart.config import Axes, DataSet, rgba
from dataIO.views import getRecentUpdateDates
from urllib import parse
# Create your views here.





def get_Bu_buUrl():
    bu = [list(i.values())[0] for i in list(EmployeeBiography.objects.values("bu").distinct()) if
          list(i.values())[0] != None]
    buUrl = [parse.quote(i) for i in bu]
    bu_buUrl = [(i, j) for i, j in zip(bu, buUrl)]
    return bu_buUrl

class LineChart(Chart):
    chart_type = 'line'
    scales = {
        'xAxes': [Axes(type='time', position='bottom')],
    }

    def getXdataYdata(self,querySet,labels):
        if querySet.count() == 0:
            self.myLabel = labels
            self.ydataArr = [[0]]
            self.xdata = [0]
            return 0
        self.myLabel = labels
        n = len(querySet[0])
        self.ydataArr = [[j["the_count" + str(1 + i)] for j in querySet] for i in range(n - 1)]
        self.xdata = [i['eval_date'] for i in querySet]
        return 0

    def get_datasets(self, **kwargs):
        colors = [
            (255, 99, 132),
            (54, 162, 235),
            (255, 206, 86),
            (75, 192, 192),
            (153, 102, 255),
            (255, 159, 64),
            (142, 68, 173),
            (23, 165, 137),
            (241, 196, 15),
            (51, 255, 66),
            (255, 51, 249)
        ]
        dataSetArr = []
        def roud_None(y):
            try:
                return '%.1f' % round(y, 2)
            except:
                None

        for ydata,label,color in zip(self.ydataArr,self.myLabel,colors[:len(self.myLabel)]):
            data_i = []
            for x,y in zip(self.xdata,ydata):
                data_i.append({"y": roud_None(y), "x": str(x)})

            DataSet_i = DataSet(type='line',
                                label = label,
                                data=data_i,
                                color=color,
                                fill=False)
            dataSetArr.append(DataSet_i)
        return dataSetArr



class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 0)'

class PieChartdata:
    def __init__(self,querySet,queryset_objects,label = {},numToStr = None):
        self.qs = querySet
        self.qsobj = queryset_objects
        self.xdata,self.ydata = self.__getXdataYdata(label,numToStr)

    def __getXdataYdata(self,label,numToStr):
        xy_data = [[i[self.qsobj], int(i["the_count"])] for i in self.qs]
        if label != {} and numToStr != None :
            xdata = list(map(lambda x: str(label[x[0]]) + numToStr, xy_data))
        elif label != {} and numToStr == None :
            xdata = list(map(lambda x: label[x[0]], xy_data))
        elif label == {} and numToStr != None :
            xdata = list(map(lambda x: str(int(x[0])) + numToStr, xy_data))
        else:
            xdata = list(map(lambda x: x[0], xy_data))
        ydata = list(map(lambda x: x[1], xy_data))
        return xdata,ydata

    def getchartDataType(self):
        extra_serie = {"tooltip": {"y_start": "", "y_end": " 명"}}
        chartdata = {'x': self.xdata, 'y1': self.ydata, 'extra1': extra_serie}
        charttype = "pieChart"
        return chartdata,charttype



def getRecentUpdateDate_str():
    dateList = getRecentUpdateDates()
    arr = []
    for name_dt in dateList:
        if name_dt[1][0] == "0개의 업데이트":
            continue
        dt = datetime.datetime.strptime(name_dt[1][0],"%Y-%m-%d")
        arr.append(dt)
    if len(arr) == 0:
        return "0개의 업데이트"
    else:
        recentDt = max(arr)
    return str(recentDt)

class Index(View):

    def get(self,request):
        isGet = self.getRequestSearch(request)
        if isGet != None:
            return isGet
        context = self.getContext()
        return render(request,'index.html',context)

    def lineChartGen(self,Model, fields, labels):
        the_counts = {"the_count" + str(idx + 1): Avg(i) for idx, i in enumerate(fields)}
        modelObj = Model.values("eval_date").annotate(**the_counts).order_by("eval_date")
        lineChart = LineChart()
        lineChart.getXdataYdata(modelObj, labels)
        return lineChart

################## refactoring target #########################################################
    def getEmpBioObj(self):
        if self.bu == None:
            empBioAll = Employee.objects.all()#filter(istarget=True)
            if self.region == "all":
                return empBioAll
            elif self.region == "seoul_gyeongi":
                return empBioAll.filter(Q(place="서울")|Q(place="판교")|Q(place="센터"))
            elif self.region == "gwangyang":
                return empBioAll.filter(place="광양")
            else:
                return empBioAll.filter(place="포항")
        else:
            empBioAll = EmployeeBiography.objects.filter(bu=self.bu)
            return empBioAll

    def getEmpObj(self,Model):
        if self.bu == None:
            empObjAll = Model.objects.all()#filter(employeeID__istarget=True)
            if self.region == "all":
                return empObjAll
            elif self.region == "seoul_gyeongi":
                return empObjAll.annotate(place=F('employeeID__place')).filter(Q(place="서울") | Q(place="판교") | Q(place="센터"))
            elif self.region == "gwangyang":
                return  empObjAll.annotate(place=F('employeeID__place')).filter(place="광양")
            else:
                return empObjAll.annotate(place=F('employeeID__place')).filter(place="포항")
        else:
            empBioAll = Model.objects.filter(employeeID__bu=self.bu)
            return empBioAll

################## refactoring target #########################################################


    def getRequestSearch(self,request):
        if request.method == 'GET':
            search_query = request.GET.get('search_box', None)
            if search_query != None:
                return HttpResponseRedirect(reverse('employee', args=[search_query]))
        return None


    def getContext(self,region="all",bu=None):
        self.region = region
        self.bu = bu
        empBioObj = self.getEmpBioObj()
        """
        ################ Get Scores #######################################################
        def rounding_none(x):
            if x == None:
                return x
            return '%.1f' % round(x, 2)

        scores_ = self.getEmpObj(Score).aggregate(score1 = Avg('score1'),score2 = Avg('score2'),score3 = Avg('score3'),score4 = Avg('score4'))
        scores = list(map(lambda x:rounding_none(x),[scores_['score1'],scores_['score2'],scores_['score3'],scores_['score4']]))
        


        ################ Scores End #######################################################
        """


        ################## lineChart #########################################################

        email_avgLineChart = self.lineChartGen(self.getEmpObj(EmailData),
                                  ["sendCnt", "sendCnt_nwh", "receiveCnt",
                                   "sendCnt_byLevelRatio", "sendCnt_nwh_byLevelRatio",
                                   "receiveCnt_byLevelRatio","nodeSize", "nodeSize_byLevelRatio",
                                   "nodeSize_byGroupRatio"],
                                  ["발신량","발신량(근무시간 외)","수신량",
                                   "발신량 직급별 비율","발신량 (근무시간 외) 직급별 비율",
                                   "수신량 직급별 비율","노드 사이즈","노드사이즈 직급별 비율",
                                   "노드사이즈 조직별 비율"])

        mep_avgLineChart = self.lineChartGen(self.getEmpObj(M_EPData),
                                            ["mep_early", "mep_late", "mep_early_byLevelRatio", "mep_late_byLevelRatio"],
                                            ["근무시간전 접속","근무시간후 접속","근무시간전 접속 직급별 비율","근무시간후 접속 직급별 비율"])


        grade_avgLineChart = self.lineChartGen(self.getEmpObj(EmployeeGrade),
                                           ['grade_r3_avg','grade_co_r3_avg','grade_sv_r3_avg'],
                                           ['성과 3년평균', '동료평가 3년평균','상사평가 3년평균'])



        edu_avgLineChart = self.lineChartGen(self.getEmpObj(Education),
                                        ['edu_course_cnt'],
                                        ['사내교육 이수학점'])

        token_avgLineChart = self.lineChartGen(self.getEmpObj(Token_Data),
                                             ["token_send", "token_receive", "token_send_byLevelRatio","token_receive_byLevelRatio"],
                                             ["토큰발신", "토큰수신", "토큰발신 직급별 비율", "토큰수신 직급별 비율"])


        vdi_avgLineChart = self.lineChartGen(self.getEmpObj(VDI_Data),
                                             ["vdi_early", "vdi_late", "vdi_early_byLevelRatio","vdi_late_byLevelRatio"],
                                             ["근무시간전 접속", "근무시간후 접속", "근무시간전 접속 직급별 비율", "근무시간후 접속 직급별 비율"])

        gatepass_avgLineChart = self.lineChartGen(self.getEmpObj(GatePassData),
                                             ["staying_office_meanM", "outting_freq_mean", "inTime_mean","outTime_mean","working_days"],
                                             ["근무시간(분)", "외출빈도", "출근시간", "퇴근시간","근무일"])

        leadership_avgLineChart = self.lineChartGen(self.getEmpObj(Leadership),
                                             ["leadership_env_job","leadership_env","leadership_env_common"],
                                             ["리더쉽.환경.직무", "리더쉽.환경.리더쉽", "러더쉽.환경.공통"])
        ################ lineChart End #######################################################






        context = {
            "bu":get_Bu_buUrl(),
            "currentBu":self.bu,
            "recentUpdateDate":  getRecentUpdateDate_str(),
            "employee_size": empBioObj.count(),
            "email":email_avgLineChart,
            "grade": grade_avgLineChart,
            "edu": edu_avgLineChart,
            "token":token_avgLineChart,
            "vdi": vdi_avgLineChart,
            "mep":mep_avgLineChart,
            "gate":gatepass_avgLineChart,
            "leadership":leadership_avgLineChart
        }

        if self.region == "all":
            context["region"] = "POSCO ICT"
        elif self.region == "seoul_gyeongi":
            context["region"] = "센터.분당"
        elif self.region == "gwangyang":
            context["region"] = "광양"
        else:
            context["region"] = "포항"
        return context
