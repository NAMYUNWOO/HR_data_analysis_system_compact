from django.shortcuts import render
from index.views import get_Bu_buUrl
from index.models import Employee,EmployeeBiography,EmailData,M_EPData,EmployeeGrade,Education,Token_Data,VDI_Data,GatePassData,Score
from index.views import LineChart, BarChart
from django.db.models import F,Q
from django.urls import reverse
from django.http import HttpResponseRedirect

# Create your views here.


def lineChartGen(Model,empobj,fields,labels):
    the_counts={"the_count"+str(idx+1):F(i) for idx,i in enumerate(fields)}
    modelVals = list(the_counts.keys()) +['eval_date']
    modelObj = Model.objects.filter(employeeID = empobj).annotate(**the_counts).values(*modelVals).order_by('eval_date')
    lineChart = LineChart()
    lineChart.getXdataYdata(modelObj,labels)
    return lineChart



def employee(request,id):
    # search
    if request.method == 'GET':
        search_query = request.GET.get('search_box', None)
        if search_query != None:
            return HttpResponseRedirect(reverse('employee', args=[search_query]))


    # error 처리 and 결과 없음 처리
    try:
        empobj = Employee.objects.get(pk=id)

    except:
        return render(request, 'employee.html',{"fail":id,})


    email_LineChart = lineChartGen(EmailData,empobj,
                              ["sendCnt", "sendCnt_nwh", "receiveCnt",
                               "sendCnt_byLevelRatio", "sendCnt_nwh_byLevelRatio",
                               "receiveCnt_byLevelRatio","nodeSize", "nodeSize_byLevelRatio",
                               "nodeSize_byGroupRatio"],
                              ["발신량","발신량(근무시간 외)","수신량",
                               "발신량 직급별 비율","발신량 (근무시간 외) 직급별 비율",
                               "수신량 직급별 비율","노드 사이즈","노드사이즈 직급별 비율",
                               "노드사이즈 조직별 비율"])

    mep_LineChart = lineChartGen(M_EPData,empobj,
                                        ["mep_early", "mep_late", "mep_early_byLevelRatio", "mep_late_byLevelRatio"],
                                        ["근무시간전 접속","근무시간후 접속","근무시간전 접속 직급별 비율","근무시간후 접속 직급별 비율"])

    grade_LineChart = lineChartGen(EmployeeGrade,empobj,
                                       ['grade_r3_avg','grade_co_r3_avg','grade_sv_r3_avg'],
                                       ['성과 3년평균', '동료평가 3년평균','상사평가 3년평균'])



    edu_LineChart = lineChartGen(Education,empobj,
                                    ['edu_course_cnt'],
                                    ['사내교육 이수학점'])

    token_LineChart = lineChartGen(Token_Data,empobj,
                                         ["token_send", "token_receive", "token_send_byLevelRatio","token_receive_byLevelRatio"],
                                         ["토큰발신", "토큰수신", "토큰발신 직급별 비율", "토큰수신 직급별 비율"])


    vdi_LineChart = lineChartGen(VDI_Data,empobj,
                                         ["vdi_early", "vdi_late", "vdi_early_byLevelRatio","vdi_late_byLevelRatio"],
                                         ["근무시간전 접속", "근무시간후 접속", "근무시간전 접속 직급별 비율", "근무시간후 접속 직급별 비율"])

    gatepass_LineChart = lineChartGen(GatePassData,empobj,
                                              ["staying_office_meanM", "outting_freq_mean", "inTime_mean",
                                               "outTime_mean", "working_days"],
                                              ["근무시간(분)", "외출빈도", "출근시간", "퇴근시간", "근무일"])
    scoreObj = Score.objects.filter(employeeID = empobj).order_by("-eval_date").first().__dict__
    scoreFields = ['predict','intercept','grade_co_r3_avg','holiday','edu_course_cnt','edu_course_time','sendCnt_byLevelRatio',
                    'sendCnt_nwh_byLevelRatio','receiveCnt_byLevelRatio','nodeSize_byLevelRatio','nodeSize_byGroupRatio',
                    'token_receive_byLevelRatio','leadership_env_job','leadership_env','leadership_env_common','early_work','late_work']
    xdataScore = [scoreObj[fl] for fl in scoreFields]
    scoreBar = BarChart()
    scoreBar.getLabelData(labels=scoreFields,xdata=xdataScore)

    context = {"bu":get_Bu_buUrl(),
               "empID":id, "name":empobj.empname,
               "place":empobj.place,
               "bonbu":empobj.bu,
               "level":empobj.level,
               "emailaddr":empobj.email,
               "email":email_LineChart,
               "mep":mep_LineChart,
               "grade":grade_LineChart,
               "edu":edu_LineChart,
               "token":token_LineChart,
               "vdi":vdi_LineChart,
               "gate":gatepass_LineChart,
               "score":scoreBar
               }
    return render(request, 'employee.html',context)