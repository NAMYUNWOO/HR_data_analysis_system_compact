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
    grade_sv_y_2 = models.FloatField(null=True)
    grade_sv_y_1 = models.FloatField(null=True)
    grade_sv_r2_avg = models.FloatField(null=True)

    # 년 역량 동료 등급 년 역량동료(동료로부터의 평가)
    grade_co_y_1 = models.FloatField(null=True)
    grade_co_y_2 = models.FloatField(null=True)
    grade_co_r2_avg = models.FloatField(null=True)

    grade_4 = models.FloatField(null=True)
    grade_3 = models.FloatField(null=True)
    grade_2 = models.FloatField(null=True)
    grade_1 = models.FloatField(null=True)
    grade_r2_avg = models.FloatField(null=True)
    # 평가일
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    # 최근 2년 동안 성과등급 평균	2015.7~2017.6까지 성과 등급의 평균 (총 4번의 평가 진행)

    def posco_set_grade_r2_avg(self):
        n = 0
        val = 0
        for i in [self.grade_1, self.grade_2, self.grade_3, self.grade_4]:
            if i == None:
                continue
            n += 1
            val += i
        if n == 0:
            self.grade_r2_avg = None
            return self.grade_r2_avg

        self.grade_r2_avg = val/n
        return self.grade_r2_avg

    def posco_set_grade_sv_r2_avg(self):
        n = 0
        val = 0
        for i in [self.grade_sv_y_1, self.grade_sv_y_2]:
            if i == None:
                continue
            n += 1
            val += i
        if n == 0:
            self.grade_sv_r2_avg = None
            return self.grade_sv_r2_avg

        self.grade_sv_r2_avg = val/n
        return self.grade_sv_r2_avg

    def posco_set_grade_co_r2_avg(self):
        n = 0
        val = 0
        for i in [self.grade_co_y_2, self.grade_co_y_1]:
            if i == None:
                continue
            n += 1
            val += i
        if n == 0:
            self.grade_co_r2_avg = None
            return self.grade_co_r2_avg

        self.grade_co_r2_avg = val/n
        return self.grade_co_r2_avg

    def __str__(self):
        return str(self.employeeID_confirm)  + "_" +str(self.eval_date)




# 교육평가
class Education(models.Model):

    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    #Y - 1년이수과정학점
    edu_credit = models.FloatField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()

    """
    edu_nbr = models.FloatField(null=True,default=0)
    toeic = models.BooleanField()
    opic  = models.BooleanField()
    tsc   = models.BooleanField()
    sjpt  = models.BooleanField()
    edu_credit_in = models.FloatField(null=True,default=0)
    edu_credit_out = models.FloatField(null=True, default=0)
    edu_credit = models.FloatField(null=True, default=0)
    lang_nbr = models.IntegerField(null=True, default=0)
    def posco_set_edu_credit(self):
        self.edu_credit = self.edu_credit_in + self.edu_credit_out
        return self.edu_credit


    def posco_set_lang_nbr(self):
        val = 0
        for i in [self.toeic,self.opic,self.tsc,self.sjpt]:
            if i:
                val += 1
        self.lang_nbr = val
        return self.lang_nbr

    """

    # 교육이수학점 1년 동안 총 직무이수학점+비직무이수학점 (=사내이수학점+사외이수학점)


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













































##############################################################

# Useless Models below

##############################################################


class Emaileigvec(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    eigvec = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

# Survey
class Survey(models.Model):

    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)


    # 업무몰입도 13번 질문 점수	13. 나는 지난 2주동안, 일할 때는 일 외의 다른 것들에 대해 아무 생각이 들지 않았다
    cct1 = models.FloatField(null=True)

    # 업무몰입도 14번 질문 점수	14. 업무를 할 때, 나는 에너지가 넘치는 걸 느낀다.
    cct2 = models.FloatField(null=True)

    # 업무몰입도 15번 질문 점수	15. 나에게 있어 포스코ICT는 내가 일할 수 있는 회사들 중에서 최고라고 생각한다.
    cct3 = models.FloatField(null=True)

    # 업무몰입도 16번 질문 점수	16. 나는 지난 2주동안 내 일에 완전히 몰두하였다.
    cct4 = models.FloatField(null=True)

    # 업무몰입도 17번 질문 점수	17. 적은 보수를 받더라도 나는 여전히 이 일을 하고 싶다
    cct5 = models.FloatField(null=True)

    # 평가일
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.employeeID_confirm)  + "_" +str(self.eval_date)


# 출장
class Trip(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    trip_domestic = models.FloatField(null=True,default=0)
    trip_town = models.FloatField(null=True,default=0)
    trip_abroad = models.FloatField(null=True, default=0)
    annual_vacation_gen_dt = models.DateField(null=True)
    annual_vacation_gen_amt = models.FloatField(null=True, default=0)
    annual_vacation_gen_usage = models.FloatField(null=True, default=0)
    btrip_nbr = models.FloatField(null=True, default=0)

    #연차소진률
    off_use_pct_permon = models.FloatField(null=True, default=0)
    # 평가일
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    # 출장 일수  1년 동안 총 출장 일수
    def posco_set_btrip_nbr(self):
        self.btrip_nbr = self.trip_domestic + self.trip_town + self.trip_abroad
        return self.btrip_nbr

    def posco_set_off_use_pct_permon(self):
        nowdt = self.eval_date
        monthgap = (nowdt.year * 12 + nowdt.month) - (self.annual_vacation_gen_dt.month + self.annual_vacation_gen_dt.year * 12)
        try:
            self.off_use_pct_permon = 100*(self.annual_vacation_gen_usage / self.annual_vacation_gen_amt)/ monthgap
        except:
            self.off_use_pct_permon = None
        if  self.off_use_pct_permon == None or self.off_use_pct_permon < 0:
            self.off_use_pct_permon = None
        return self.off_use_pct_permon

    def __str__(self):
        return str(self.employeeID_confirm)  + "_" +str(self.eval_date)

class Thanks_log(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    #thxs_receiveID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False,related_name="deadfield")
    thxType = models.CharField(max_length=20,null=False) # {"감사노트":"thanksNote","감사문자":"thanksMsg","감사토큰":"thanksToken","감사편지":"thanksletter"}
    writerType = models.CharField(max_length=20,null=False) # send, receive, follow,
    followType = models.CharField(max_length=20,null=False) #c {"내용":"contents","공감":"like","댓글":"reply"}
    eval_date = models.DateField()
    def __str__(self):
        return str(self.employeeID) + "_at_" + str(self.eval_date)

class Thanks_Data(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    thank_letter_tot_receive = models.FloatField(null=True,default=0)
    thank_token_tot_receive = models.FloatField(null=True, default=0)
    thank_msg_tot_receive = models.FloatField(null=True, default=0)
    thank_note_tot_receive = models.FloatField(null=True, default=0)
    thank_letter_tot_send = models.FloatField(null=True,default=0)
    thank_token_tot_send = models.FloatField(null=True, default=0)
    thank_msg_tot_send = models.FloatField(null=True, default=0)
    thank_note_tot_send = models.FloatField(null=True, default=0)
    thank_like_tot = models.FloatField(null=True, default=0)
    thank_reply_tot = models.FloatField(null=True, default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()

    def yearbeforpoint(self):
        return Thanks_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def posco_set_thank_tot_receive_send(self):
        thxTypes_arr = ["thanksletter","thanksToken","thanksMsg","thanksNote"]
        send_or_recieve = ["send", "receive"]
        for thxType in thxTypes_arr:
            for sor in send_or_recieve:
                thxObj = Thanks_log.objects.filter(Q(employeeID=self.employeeID_confirm)&Q(writerType=sor)&Q(thxType = thxType) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
                if thxType == "thanksletter" and sor == "send":
                    self.thank_letter_tot_send = thxObj.count()
                elif thxType == "thanksToken" and sor == "send":
                    self.thank_token_tot_send = thxObj.count()
                elif thxType == "thanksMsg" and sor == "send":
                    self.thank_msg_tot_send = thxObj.count()
                elif thxType == "thanksNote" and sor == "send":
                    self.thank_note_tot_send = thxObj.count()
                elif thxType == "thanksletter" and sor == "receive":
                    self.thank_letter_tot_receive = thxObj.count()
                elif thxType == "thanksToken" and sor == "receive":
                    self.thank_token_tot_receive = thxObj.count()
                elif thxType == "thanksMsg" and sor == "receive":
                    self.thank_msg_tot_receive = thxObj.count()
                elif thxType == "thanksNote" and sor == "receive":
                    self.thank_note_tot_receive = thxObj.count()

    def posco_set_thank_tot_follow(self):
        thxObjLike = Thanks_log.objects.filter(Q(employeeID=self.employeeID_confirm) & Q(writerType="follow") & Q(followType="like") & Q(eval_date__gte=self.start_date) & Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        thxObjReply = Thanks_log.objects.filter(Q(employeeID=self.employeeID_confirm) & Q(writerType="follow") & Q(followType="reply") & Q(eval_date__gte=self.start_date) & Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.thank_like_tot = thxObjLike.count()
        self.thank_reply_tot = thxObjReply.count()

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)



class EP_log(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateTimeField()

    def __str__(self):
        return str(self.employeeID) + "_at_" + str(self.eval_date)


class EPData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    employeeID_confirm = models.IntegerField(default=0)
    ep_access_day_mean = models.FloatField(null=True, default=0)
    ep_access_day_var = models.FloatField(null=True, default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()

    def yearbeforpoint(self):
        return EP_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)


    def posco_set_ep_access_day_mean(self):
        epobj = EP_log.objects.filter(Q(employeeID=self.employeeID) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if epobj.count() == 0:
            return 0
        avg = epobj.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("employeeID")).aggregate(avg=Avg("the_count"))["avg"]
        self.ep_access_day_mean = avg
        return self.ep_access_day_mean

    def posco_set_ep_access_day_var(self):
        epobj = EP_log.objects.filter(Q(employeeID=self.employeeID) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if epobj.count() == 0:
            return 0
        valList = list(epobj.annotate(day=TruncMonth("eval_date")).values("day").annotate(the_count=Count("employeeID")).values_list("the_count",flat=True))
        var_ = np.std(valList)
        self.ep_access_day_var = var_

class VDI_indi_log(models.Model):
    user_indi_ID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    useMinute = models.FloatField(default=0)
    eval_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.user_indi_ID) + "_at_" + str(self.eval_date)

class VDI_indi_Data(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    vdi_indi_mean_timem = models.FloatField(null=True,default=0)
    vdi_indi_tot_access = models.FloatField(null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def yearbeforpoint(self):
        return VDI_indi_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def posco_set_vdi_indi_tot_access(self):
        vdi_indi_Obj = VDI_indi_log.objects.filter(Q(user_indi_ID=self.employeeID_confirm)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.vdi_indi_tot_access = vdi_indi_Obj.count()
        return self.vdi_indi_tot_access

    def posco_set_vdi_indi_mean_timem(self):
        vdi_indi_mean = VDI_indi_log.objects.filter(Q(user_indi_ID=self.employeeID_confirm)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1))).aggregate(avg = Avg("useMinute"))["avg"]
        self.vdi_indi_mean_timem = vdi_indi_mean
        return self.vdi_indi_mean_timem

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)


class VDI_share_log(models.Model):
    user_share_ID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    useMinute = models.FloatField(default=0)
    eval_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.user_share_ID) + "_at_" + str(self.eval_date)

class VDI_share_Data(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    vdi_share_mean_time = models.FloatField(null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def yearbeforpoint(self):
        return VDI_share_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def posco_set_vdi_share_mean_time(self):
        vdi_share_mean = VDI_share_log.objects.filter(Q(user_share_ID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1))).aggregate(avg = Avg("useMinute"))["avg"]
        self.vdi_share_mean_time = vdi_share_mean
        return self.vdi_share_mean_time
    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)




class Reward_log(models.Model):
    rewardID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateTimeField()

class Flow(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    flow = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.employeeID_confirm) + "_score_"+str(self.flow) +'_at_' + str(self.eval_date)

class Score(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    #몰입
    score1 =  models.FloatField(default=0)
    # 성과
    score2 = models.FloatField(default=0)
    # 핵심
    score3 = models.FloatField(default=0)
    # 업무
    score4 = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.employeeID_confirm) + "_score_"+str(self.score) +'_at_' + str(self.eval_date)


class PCM_log(models.Model):
    employeeID =  models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateTimeField()
    pcm_tot_enroll  = models.FloatField(null=True, default=0)
    pcm_tot_remove  = models.FloatField(null=True, default=0)
    pcm_tot_check  = models.FloatField(null=True, default=0)
    pcm_tot_checked  = models.FloatField(null=True, default=0)

    def __str__(self):
        return str(self.employeeID) + "_at_" + str(self.eval_date)


class PCMData(models.Model):
    employeeID =  models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    pcm_tot_enroll  = models.FloatField(null=True, default=0)
    pcm_tot_remove  = models.FloatField(null=True, default=0)
    pcm_tot_check  = models.FloatField(null=True, default=0)
    pcm_tot_checked  = models.FloatField(null=True, default=0)

    def posco_set_all(self):
        pcmobj_ = PCM_log.objects.filter(employeeID=self.employeeID_confirm).order_by("eval_date")
        if len(pcmobj_) == 0:
            return
        pcmobj = pcmobj_.first()
        self.pcm_tot_enroll = pcmobj.pcm_tot_enroll
        self.pcm_tot_remove = pcmobj.pcm_tot_remove
        self.pcm_tot_check = pcmobj.pcm_tot_check
        self.pcm_tot_checked = pcmobj.pcm_tot_checked


    def __str__(self):
        return str(self.employeeID) + "_at_" + str(self.eval_date)


class IMS_log(models.Model):
    employeeID =  models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    imstype = models.CharField(max_length=20, null=False)
    eval_date = models.DateTimeField()
    def __str__(self):
        return str(self.employeeID) + "_at_" + str(self.eval_date)

class IMSData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    ims_tot_enroll = models.FloatField(null=True, default=0)
    ims_tot_opinion_enroll  = models.FloatField(null=True, default=0)
    ims_tot_idea_enroll  = models.FloatField(null=True, default=0)
    ims_tot_board_enroll  = models.FloatField(null=True, default=0)
    ims_tot_board_opinion_enroll  = models.FloatField(null=True, default=0)

    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()

    def yearbeforpoint(self):
        return IMS_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def _ims_tot_opinion_enroll(self):
        imsObj = IMS_log.objects.filter(Q(employeeID=self.employeeID_confirm)&Q(imstype="opinion") &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.ims_tot_opinion_enroll = imsObj.count()

    def _ims_tot_idea_enroll(self):
        imsObj = IMS_log.objects.filter(Q(employeeID=self.employeeID_confirm)&Q(imstype="idea") &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.ims_tot_idea_enroll = imsObj.count()

    def _ims_tot_board_enroll(self):
        imsObj = IMS_log.objects.filter(Q(employeeID=self.employeeID_confirm)&Q(imstype="board") &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.ims_tot_board_enroll = imsObj.count()

    def _ims_tot_board_opinion_enroll(self):
        imsObj = IMS_log.objects.filter(Q(employeeID=self.employeeID_confirm)&Q(imstype="board_opinion") &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.ims_tot_board_opinion_enroll = imsObj.count()

    def _ims_tot_enroll(self):
        self.ims_tot_enroll = self.ims_tot_opinion_enroll + self.ims_tot_idea_enroll +  self.ims_tot_board_enroll + self.ims_tot_board_opinion_enroll

    def posco_set_ims_data_set(self):
        self._ims_tot_opinion_enroll()
        self._ims_tot_idea_enroll()
        self._ims_tot_board_enroll()
        self._ims_tot_board_opinion_enroll()
        self._ims_tot_enroll()


    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)



class Meeting_log(models.Model):
    employeeID =  models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateTimeField() # meeting start
    eval_date2 = models.DateTimeField() # meeting end

    def __str__(self):
        return str(self.employeeID) + "_meeting_from_" + str(self.eval_date) + "_to_"  +str(self.eval_date2)


class MeetingData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    meeting_join_count = models.FloatField(null=True, default=0)
    mean_meeting_time  = models.FloatField(null=True, default=0)  # 시간단위
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()

    def yearbeforpoint(self):
        return Meeting_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def posco_set_meeting_join_count(self):
        meetingObj = Meeting_log.objects.filter(Q(employeeID=self.employeeID)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.meeting_join_count = meetingObj.count()

    def posco_set_mean_meeting_time(self):
        meetingObj = Meeting_log.objects.filter(Q(employeeID=self.employeeID) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1))
                            ).annotate(
                            gap = ExpressionWrapper(F("eval_date2") - F("eval_date"),DurationField())
                            ).values_list("gap",flat=True)
        if meetingObj.count() == 0:
            return 0
        mean_meeting = sum(map(lambda x:x.total_seconds()/3600,meetingObj))/meetingObj.count()
        self.mean_meeting_time = mean_meeting


class TMS_log(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=True, related_name="executor")
    employeeID2 = models.ForeignKey(Employee,on_delete=models.PROTECT, null=True, related_name="cooperator")
    eval_date = models.DateTimeField()
    def __str__(self):
        return str(self.employeeID) + "_and_" + str(self.employeeID2) + "_at_" + str(self.eval_date)

class TMSData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    tms_tot_attendant = models.FloatField(null=True,default=0)
    tms_tot_coworker = models.FloatField(null=True,default=0)
    def posco_set_tms_tot_attendant(self):
        tmsobj = TMS_log.objects.filter(Q(employeeID=self.employeeID_confirm) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.tms_tot_attendant = tmsobj.count()


    def posco_set_tms_tot_coworker(self):
        tmsobj = TMS_log.objects.filter(Q(employeeID2=self.employeeID_confirm) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.tms_tot_coworker = tmsobj.count()


class Approval_log(models.Model):
    requesterID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False, related_name="requesterID")
    approverID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False, related_name="approverID")
    eval_date = models.DateTimeField()
    approve_date = models.DateTimeField()
    def __str__(self):
        return str(self.requesterID) + "_to_" + str(self.approverID) + "_at_" + str(self.eval_date)



class ApprovalData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    approve_tot_request = models.FloatField(null=True,default=0)
    approve_tot_sign = models.FloatField(null=True,default=0)
    approve_mean_timeh = models.FloatField(null=True,default=0)
    def yearbeforpoint(self):
        return Approval_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def posco_set_approve_tot_request(self):
        approvalObj = Approval_log.objects.filter(Q(requesterID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.approve_tot_request = approvalObj.count()

    def posco_set_approve_tot_sign(self):
        approvalObj = Approval_log.objects.filter(Q(approverID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.approve_tot_sign = approvalObj.count()

    def posco_set_approve_mean_timeh(self):
        approvalObj = Approval_log.objects.filter(
                            Q(requesterID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1))
                            ).annotate(
                            gap = ExpressionWrapper(F("approve_date") - F("eval_date"),DurationField())
                            ).values_list("gap",flat=True)
        if approvalObj.count() == 0:
            return 0
        approve_mean_timeh = sum(map(lambda x:x.total_seconds()/3600,approvalObj))/approvalObj.count()
        self.approve_mean_timeh = approve_mean_timeh

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)





class Portable_out_Data(models.Model):

    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    porta_tot_request = models.FloatField(null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def yearbeforpoint(self):
        return Portable_out_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)
    def posco_set_porta_tot_request(self):
        portaObj = Portable_out_log.objects.filter(Q(requesterID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.porta_tot_request = portaObj.count()
        return self.porta_tot_request
    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)


class PC_out_Data(models.Model):

    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    pcout_tot_request = models.FloatField(null=True,default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def yearbeforpoint(self):
        return PC_out_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def posco_set_pcout_tot_request(self):
        pcObj = PC_out_log.objects.filter(Q(requesterID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.pcout_tot_request =  pcObj.count()
        return self.pcout_tot_request

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)

class PC_control_Data(models.Model):

    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    pccontrol_mean_timeh = models.FloatField(null=True,default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def yearbeforpoint(self):
        return PC_control_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def posco_set_pccontrol_mean_timeh(self):
        pcObj = PC_control_log.objects.filter(
                            Q(requesterID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1))
                            ).annotate(
                            gap = ExpressionWrapper(F("approval_date") - F("eval_date"),DurationField())
                            ).values_list("gap",flat=True)
        if pcObj.count() == 0:
            return 0
        pccontrol_meanH = sum(map(lambda x:x.total_seconds()/3600,pcObj))/pcObj.count()
        self.pccontrol_mean_timeh = pccontrol_meanH
        return self.pccontrol_mean_timeh

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)


class PC_control_log(models.Model):
    requesterID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    approval_date = models.DateTimeField(null=True,default = timezone.now)
    eval_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.requesterID) + "_at_" + str(self.eval_date)


class PC_out_log(models.Model):
    requesterID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.requesterID) + "_at_" + str(self.eval_date)

class Portable_out_log(models.Model):
    requesterID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.requesterID) + "_at_" + str(self.eval_date)









class ECMData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    ecm_before_in79 = models.FloatField(null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def yearbeforpoint(self):
        return ECM_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def posco_set_ecm_before_in79(self):
        ecmCnctObj = ECM_log.objects.filter(Q(userECMID=self.employeeID_confirm)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if ecmCnctObj.count() == 0:
            return 0
        daycnt = ecmCnctObj.filter(Q(eval_date__hour__gte=7) & Q(eval_date__hour__lt=9)).annotate(day=TruncDay("eval_date")).values("day").distinct().count()
        self.ecm_before_in79 = daycnt
        return self.ecm_before_in79

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)



class ECM_log(models.Model):
    userECMID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.userECMID) + "_at_" + str(self.eval_date)



class CafeteriaData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    food_tot_spend = models.FloatField(null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def yearbeforpoint(self):
        return Cafeteria_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def posco_set_food_tot_spend(self):
        cafeterialObj = Cafeteria_log.objects.filter(Q(buyerID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.food_tot_spend = cafeterialObj.aggregate(tot = Sum("payment"))["tot"]
        return self.food_tot_spend

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)


class Cafeteria_log(models.Model):
    buyerID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    payment = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    eval_date = models.DateField()
    def __str__(self):
        return str(self.buyerID) + "_at_" + str(self.eval_date)



class BlogData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()
    blog_tot_visit =  models.FloatField(null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def yearbeforpoint(self):
        return Blog_log.objects.order_by("-eval_date").first().eval_date - datetime.timedelta(days=365)

    def posco_set_blog_tot_visit(self):
        blogObj = Blog_log.objects.filter(Q(blogID=self.employeeID_confirm)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        self.blog_tot_visit = blogObj.count()
        return self.blog_tot_visit

    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)


class Blog_log(models.Model):
    blogID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    eval_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.blogID) + "_at_" + str(self.eval_date)


class SNAGraph(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT, null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date1 = models.DateTimeField()
    eval_date2 = models.DateTimeField()
    x = models.FloatField(null=True,default=0)
    y = models.FloatField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + "x: "+str(self.x) + " y: "+str(self.y)
