from django.db import models
from django.db.models import Q,F, Sum, Count, Case, When, Avg, Func,ExpressionWrapper,DurationField
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import  timezone
import  numpy as np
import networkx as nx
import datetime
# Create your models here.


class LogFirstLast(models.Model):
    modelName = models.CharField(primary_key=True,max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.modelName + " start at "+str(self.start_date) +", end at "+ str(self.end_date)

class Employee(models.Model):
    id = models.IntegerField(primary_key=True)

    # 부	부.그룹. 이 아닌 그냥 부 (최소단위)
    bu = models.CharField(max_length=50,null=True)
    level = models.IntegerField(null=True)
    email = models.CharField(max_length=50,default="")
    empname = models.CharField(max_length=30, null=True)
    place = models.CharField(max_length=30, null=True)
    """useless columns 

    # 핵심인재유무	핵심인재 인지 아닌 지
    coreyn = models.BooleanField(default=False)

    # 나이
    age = models.FloatField(null=True)

    # 근무기간	총 근무 기간 (데이터 추출 당시)
    work_duration = models.FloatField(default=0)
    # 성별	Female / Male
    sex = models.BooleanField()
    pmlevel = models.IntegerField(null=True)

    istarget = models.BooleanField(default=True)
    """
    def __str__(self):
        return str(self.id)


"""
    empid = models.ForeignKey(Employee,null=False)
    empidN =  models.IntegerField(default=0)
"""
class EmployeeBiography(models.Model):
    # 사번
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)

    # 부	부.그룹. 이 아닌 그냥 부 (최소단위)
    bu = models.CharField(max_length=50,null=True)
    email = models.CharField(max_length=50, default="")
    level = models.IntegerField(null=True)
    empname = models.CharField(max_length=30, null=True)
    place = models.CharField(max_length=30, null=True)
    holiday = models.FloatField(null=True) #근태연차누적사용일수
    start_date = models.DateTimeField()
    eval_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    """ useless columns 
    
    
    # 핵심인재유무	핵심인재 인지 아닌 지
    coreyn = models.BooleanField(default=False)

    # 나이
    age = models.FloatField(null=True)

    # 근무기간	총 근무 기간 (데이터 추출 당시)
    work_duration = models.FloatField(default=0)
    # 성별	Female / Male
    sex = models.BooleanField()
    pmlevel = models.IntegerField(null=True)
    

    istarget = models.BooleanField(default=True)
    #해당기간 안의 유효한 hr
    @property
    def rewardyn(self):
        rewardObj = Reward_log.objects.filter(Q(rewardID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__gte = self.eval_date))
        return rewardObj.count() > 0
    """
    def yearbeforpoint(self):
        return datetime.datetime.now() - datetime.timedelta(days=365)

    def __str__(self):
        return str(self.employeeID_confirm) + " from "+str(self.start_date)+" to "+str(self.eval_date)



# 직원평가
class EmployeeGrade(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)

    # 년 역량 하향 등급	년 역량하향 등급 (상사로부터의 평가)
    grade_sv_y_3 = models.FloatField(null=True)
    grade_sv_y_2 = models.FloatField(null=True)
    grade_sv_y_1 = models.FloatField(null=True)
    grade_sv_r3_avg = models.FloatField(null=True)

    # 년 역량 동료 등급 년 역량동료(동료로부터의 평가)
    grade_co_y_1 = models.FloatField(null=True)
    grade_co_y_2 = models.FloatField(null=True)
    grade_co_y_3 = models.FloatField(null=True)
    grade_co_r3_avg = models.FloatField(null=True)

    grade_6 = models.FloatField(null=True)
    grade_5 = models.FloatField(null=True)
    grade_4 = models.FloatField(null=True)
    grade_3 = models.FloatField(null=True)
    grade_2 = models.FloatField(null=True)
    grade_1 = models.FloatField(null=True)
    grade_r3_avg = models.FloatField(null=True)
    # 평가일
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    # 최근 2년 동안 성과등급 평균	2015.7~2017.6까지 성과 등급의 평균 (총 4번의 평가 진행)

    def posco_set_grade_r3_avg(self):
        n = 0
        val = 0
        for i in [self.grade_1, self.grade_2, self.grade_3, self.grade_4, self.grade_5, self.grade_6]:
            if i == None:
                continue
            n += 1
            val += i
        if n == 0:
            self.grade_r3_avg = None
            return self.grade_r3_avg

        self.grade_r3_avg = val/n
        return self.grade_r3_avg

    def posco_set_grade_sv_r3_avg(self):
        n = 0
        val = 0
        for i in [self.grade_sv_y_1, self.grade_sv_y_2, self.grade_sv_y_3]:
            if i == None:
                continue
            n += 1
            val += i
        if n == 0:
            self.grade_sv_r3_avg = None
            return self.grade_sv_r3_avg

        self.grade_sv_r3_avg = val/n
        return self.grade_sv_r3_avg

    def posco_set_grade_co_r3_avg(self):
        n = 0
        val = 0
        for i in [self.grade_co_y_3,self.grade_co_y_2, self.grade_co_y_1]:
            if i == None:
                continue
            n += 1
            val += i
        if n == 0:
            self.grade_co_r3_avg = None
            return self.grade_co_r3_avg

        self.grade_co_r3_avg = val/n
        return self.grade_co_r3_avg

    def __str__(self):
        return str(self.employeeID_confirm)  + "_" +str(self.eval_date)




# 교육평가
class Education(models.Model):

    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    #Y - 1년이수과정학점
    edu_course_cnt = models.FloatField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()


    def __str__(self):
        return str(self.employeeID_confirm)  + "_" +str(self.eval_date)


class EmailLog(models.Model):
    sendID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False, related_name="email_sendID")
    receiveID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False, related_name="email_receiveID")
    nwh = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    eval_date = models.DateTimeField()

    def __str__(self):
        return str(self.sendID) + "_to_" + str(self.receiveID) + "_at_" + str(self.eval_date)

class EmailData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    sendCnt = models.FloatField(null=True, default=0)
    sendCnt_nwh = models.FloatField(null=True, default=0)
    receiveCnt = models.FloatField(null=True, default=0)
    sendCnt_byLevelRatio= models.FloatField(null=True, default=0)
    sendCnt_nwh_byLevelRatio = models.FloatField(null=True, default=0)
    receiveCnt_byLevelRatio = models.FloatField(null=True, default=0)
    nodeSize = models.FloatField(null=True, default=0)
    nodeSize_byLevelRatio = models.FloatField(null=True, default=0)
    nodeSize_byGroupRatio = models.FloatField(null=True, default=0)

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)


class EmailDateBeginEnd(models.Model):
    id = models.IntegerField(primary_key=True)
    eval_date = models.DateTimeField()
    def __str__(self):
        return str(self.eval_date)

class M_EP_log(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.employeeID) + "_at_" + str(self.eval_date)

class M_EPData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    mep_normal = models.FloatField(null=True, default=0)
    mep_early = models.FloatField(null=True,default=0)
    mep_late = models.FloatField(null=True,default=0)
    mep_normal_byLevelRatio = models.FloatField(null=True, default=0)
    mep_early_byLevelRatio = models.FloatField(null=True,default=0)
    mep_late_byLevelRatio = models.FloatField(null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def yearbeforpoint(self):
        return M_EP_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def __str__(self):
        return str(self.employeeID)


class VDI_log(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.employeeID) + "_at_" + str(self.eval_date)

class VDI_Data(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    vdi_normal = models.FloatField(null=True, default=0)
    vdi_early = models.FloatField(null=True,default=0)
    vdi_late = models.FloatField(null=True,default=0)
    vdi_normal_byLevelRatio = models.FloatField(null=True, default=0)
    vdi_early_byLevelRatio = models.FloatField(null=True,default=0)
    vdi_late_byLevelRatio = models.FloatField(null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def yearbeforpoint(self):
        return VDI_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)

class Token_log(models.Model):
    sendID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False, related_name="token_sendID")
    receiveID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False, related_name="token_receiveID")
    eval_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.sendID) +"to" +str(self.receiveID)

class Token_Data(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    token_send = models.FloatField(null=True,default=0)
    token_receive = models.FloatField(null=True,default=0)
    token_send_byLevelRatio = models.FloatField(null=True,default=0)
    token_receive_byLevelRatio = models.FloatField(null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def yearbeforpoint(self):
        return Token_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)


class GatePass_log(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateTimeField()
    isIn = models.BooleanField()  # true: in, false:out
    def __str__(self):
        return str(self.employeeID) + "_at_" + str(self.eval_date)

class GatePassData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    staying_office_meanM =  models.FloatField(null=True)
    staying_office_meanStr = models.CharField(max_length=20, null=True)
    outting_freq_mean = models.FloatField(null=True)
    inTime_mean = models.FloatField(null=True)
    outTime_mean = models.FloatField(null=True)
    inTime_meanStr = models.CharField(max_length=20,null=True)
    outTime_meanStr = models.CharField(max_length=20,null=True)
    working_days =  models.FloatField(null=True,default=0)


    def posco_set_staying_office_outting_meanh(self):
        gpobj = GatePass_log.objects.filter(Q(employeeID=self.employeeID_confirm) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if gpobj.count() == 0:
            return
        gp_list = list(gpobj.values("eval_date", "isIn").order_by("eval_date"))
        outtingFreqArr = []
        inTimeArr = []
        outTimeArr = []
        stayingMinuteArr = []
        inStack = []
        outStack = []
        dayOverPoint = datetime.datetime.now()
        for idx, gp_i in enumerate(gp_list):
            currentIO = gp_i["isIn"]
            currentIOTime = gp_i["eval_date"]
            if idx < len(gp_list)-1:
                nextIO = gp_list[idx+1]["isIn"]
                nextIOTime = gp_list[idx+1]["eval_date"]
            else:
                nextIO = not currentIO
                nextIOTime = currentIOTime

            if len(inStack) == 0 and not currentIO:
                continue

            if currentIO:
                inStack.append(currentIOTime)
            else:
                outStack.append(currentIOTime)
            """
            if len(inStack) < len(outStack):
                # 들어온 기록이 없는데 나간 기록이 먼저 생길경우, 항상 In first, out second 이기 때문에 outStack의 길이가 inStack보다 길수 없다.
                inStack.append(outStack[-1])
            """
            if len(inStack) == 1:
                # 첫 In 기록 이 생길경우
                if currentIOTime.hour < 4:
                    dayOverPoint = datetime.datetime(currentIOTime.year,currentIOTime.month,currentIOTime.day,4,0,0)
                else:
                    nextday = currentIOTime + datetime.timedelta(days=1)
                    dayOverPoint = datetime.datetime(nextday.year, nextday.month, nextday.day, 4, 0,0)

            if idx == len(gp_list) - 1:
                if currentIO:
                    inTimeArr.append(inStack[0])
                    outtingFreqArr.append(len(outStack)-1)
                    if not currentIO:
                        outtingFreqArr[-1] += 0.5
                    inStack = []
                    outStack = []
                else:
                    inTimeArr.append(inStack[0])
                    outTimeArr.append(outStack[-1])
                    workingMinute = (outStack[-1] - inStack[0]).total_seconds() / 60
                    stayingMinuteArr.append(workingMinute)
                    outtingFreqArr.append(len(outStack) - 1)
                    outStack = []
                    inStack = []
                continue

            if nextIOTime >= dayOverPoint:

                if not (currentIO^nextIO):
                    # 마지막:in - 다음날:in, or 마지막:out - 다음날:out 으로 판단될 경우 => 퇴근시간을 알수 없음, 사무실에 머무는시간을 알수 없음
                    # 마지막:out - 다음날:out 의 경우 in 시간이 불명확하므로 마지막 out이 외출인지 퇴근인지 알 수 없음
                    inTimeArr.append(inStack[0])
                    outtingFreqArr.append(len(outStack)-1)
                    if not currentIO:
                        outtingFreqArr[-1] += 0.5
                    inStack = []
                    outStack = []
                    continue

                # 하루가 마감된 것으로 판단
                if currentIO and (currentIO^nextIO):
                    # In으로 하루가 마감, 다음날 out으로 시작 => 밤샘
                    outStack.append(dayOverPoint) # dayOverPoint에 퇴근한것으로 처리
                    inTimeArr.append(inStack[0])
                    outTimeArr.append(outStack[-1])
                    workingMinute = (outStack[-1] - inStack[0]).total_seconds() / 60
                    stayingMinuteArr.append(workingMinute)
                    outtingFreqArr.append(len(outStack) - 1)
                    outStack = []
                    inStack = []
                    #inStack.append(dayOverPoint) # dayOverPoint에 다시 출근한것으로 처리
                elif not currentIO and (currentIO^nextIO):
                    # out으로 하루가 마감, 다음날 In으로 시작 => 정상 퇴근
                    inTimeArr.append(inStack[0])
                    outTimeArr.append(outStack[-1])
                    workingMinute = (outStack[-1] - inStack[0]).total_seconds() / 60
                    stayingMinuteArr.append(workingMinute)
                    outtingFreqArr.append(len(outStack) - 1)
                    outStack = []
                    inStack = []


        if len(outtingFreqArr) != 0:
            self.outting_freq_mean = sum(outtingFreqArr)/len(outtingFreqArr)
        if len(stayingMinuteArr) != 0:
            self.staying_office_meanM = sum(stayingMinuteArr) / len(stayingMinuteArr)
            self.staying_office_meanStr =  str(datetime.timedelta(minutes=int(self.staying_office_meanM)))
        if len(inTimeArr) != 0:
            self.inTime_mean = sum([dt.hour * 3600 + dt.minute * 60 + dt.second for dt in inTimeArr]) / len(inTimeArr)
            self.inTime_meanStr = str(datetime.timedelta(seconds=int(self.inTime_mean) ))
        if len(outTimeArr) != 0:
            self.outTime_mean = sum([self.overOutAddTime(dt.hour * 3600 + dt.minute * 60 + dt.second) for dt in outTimeArr]) / len(outTimeArr)
            self.outTime_meanStr = str(datetime.timedelta(seconds=int(self.outTime_mean)))
        self.working_days = len(inTimeArr)

    def overOutAddTime(self,seconds):
        if seconds <= 14400:
            return seconds + 86400
        return seconds

    def __str__(self):
        return str(self.employeeID) + "_at_" + str(self.eval_date)




class Leadership(models.Model):
    employeeID = models.ForeignKey(Employee, on_delete=models.PROTECT, null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    leadership_env_job = models.FloatField(null=True)
    leadership_env = models.FloatField(null=True)
    leadership_env_common = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def yearbeforpoint(self):
        return Token_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)


