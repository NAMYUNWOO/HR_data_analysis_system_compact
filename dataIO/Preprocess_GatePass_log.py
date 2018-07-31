from django.db.models import Q,F, Sum, Count, Case, When, Avg, Func,ExpressionWrapper,DurationField
from index.models import Employee
import datetime

def overOutAddTime(seconds):
    if seconds <= 14400:
        return seconds + 86400
    return seconds

def preprocess_GatePass_log(GatePass_log,GatePassData,dateRange):
    GatePassData_list = []
    emp_idList = list(Employee.objects.all().order_by("level").values_list('id', flat=True))
    for emp_id in emp_idList:
        empObj = Employee.objects.get(pk=emp_id)
        gpobj = GatePass_log.objects.filter(Q(employeeID=emp_id) & Q(eval_date__gte=dateRange[0]) & Q(eval_date__lte=dateRange[1] + datetime.timedelta(days=1)))
        if gpobj.count() == 0:
            continue
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
            if idx < len(gp_list) - 1:
                nextIO = gp_list[idx + 1]["isIn"]
                nextIOTime = gp_list[idx + 1]["eval_date"]
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
                    dayOverPoint = datetime.datetime(currentIOTime.year, currentIOTime.month, currentIOTime.day, 4, 0, 0)
                else:
                    nextday = currentIOTime + datetime.timedelta(days=1)
                    dayOverPoint = datetime.datetime(nextday.year, nextday.month, nextday.day, 4, 0, 0)

            if idx == len(gp_list) - 1:
                if currentIO:
                    inTimeArr.append(inStack[0])
                    outtingFreqArr.append(len(outStack) - 1)
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

                if not (currentIO ^ nextIO):
                    # 마지막:in - 다음날:in, or 마지막:out - 다음날:out 으로 판단될 경우 => 퇴근시간을 알수 없음, 사무실에 머무는시간을 알수 없음
                    # 마지막:out - 다음날:out 의 경우 in 시간이 불명확하므로 마지막 out이 외출인지 퇴근인지 알 수 없음
                    inTimeArr.append(inStack[0])
                    outtingFreqArr.append(len(outStack) - 1)
                    if not currentIO:
                        outtingFreqArr[-1] += 0.5
                    inStack = []
                    outStack = []
                    continue

                # 하루가 마감된 것으로 판단
                if currentIO and (currentIO ^ nextIO):
                    # In으로 하루가 마감, 다음날 out으로 시작 => 밤샘
                    outStack.append(dayOverPoint)  # dayOverPoint에 퇴근한것으로 처리
                    inTimeArr.append(inStack[0])
                    outTimeArr.append(outStack[-1])
                    workingMinute = (outStack[-1] - inStack[0]).total_seconds() / 60
                    stayingMinuteArr.append(workingMinute)
                    outtingFreqArr.append(len(outStack) - 1)
                    outStack = []
                    inStack = []
                    # inStack.append(dayOverPoint) # dayOverPoint에 다시 출근한것으로 처리
                elif not currentIO and (currentIO ^ nextIO):
                    # out으로 하루가 마감, 다음날 In으로 시작 => 정상 퇴근
                    inTimeArr.append(inStack[0])
                    outTimeArr.append(outStack[-1])
                    workingMinute = (outStack[-1] - inStack[0]).total_seconds() / 60
                    stayingMinuteArr.append(workingMinute)
                    outtingFreqArr.append(len(outStack) - 1)
                    outStack = []
                    inStack = []
        modelParams = {"employeeID":empObj,"employeeID_confirm":emp_id,"start_date":dateRange[0], "eval_date":dateRange[1]}
        if len(outtingFreqArr) != 0:
            outting_freq_mean = sum(outtingFreqArr) / len(outtingFreqArr)
            modelParams.update({"outting_freq_mean":outting_freq_mean})
        if len(stayingMinuteArr) != 0:
            staying_office_meanM = sum(stayingMinuteArr) / len(stayingMinuteArr)
            staying_office_meanStr = str(datetime.timedelta(minutes=int(staying_office_meanM)))
            modelParams.update({"staying_office_meanM": staying_office_meanM})
            modelParams.update({"staying_office_meanStr": staying_office_meanStr})
        if len(inTimeArr) != 0:
            inTime_mean = sum([dt.hour * 3600 + dt.minute * 60 + dt.second for dt in inTimeArr]) / len(inTimeArr)
            inTime_meanStr = str(datetime.timedelta(seconds=int(inTime_mean)))
            modelParams.update({"inTime_mean": inTime_mean})
            modelParams.update({"inTime_meanStr": inTime_meanStr})
        if len(outTimeArr) != 0:
            outTime_mean = sum(
                [overOutAddTime(dt.hour * 3600 + dt.minute * 60 + dt.second) for dt in outTimeArr]) / len(outTimeArr)
            outTime_meanStr = str(datetime.timedelta(seconds=int(outTime_mean)))
            modelParams.update({"outTime_mean": outTime_mean})
            modelParams.update({"outTime_meanStr": outTime_meanStr})
        working_days = len(inTimeArr)
        modelParams.update({"working_days": working_days})
        gatePassData_obj = GatePassData(**modelParams)
        GatePassData_list.append((gatePassData_obj))
        GatePassData.objects.bulk_create(GatePassData_list)


