import pandas as pd
import datetime
import numpy as np
from index.models import Employee
from django.db.models import Q
import re
from functools import reduce
N_IQR = 3

def mean_except_outlier(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    series2 = series[series > q1 - N_IQR*iqr]
    if len(series2) == 0:
        return np.mean(series)
    return np.mean(series2)

def preprocess_Token_log(Token_log,Token_Data,dateRange):
    rows = list(Token_log.objects.filter(Q(eval_date__gte=dateRange[0]) & Q(eval_date__lte=dateRange[1] + datetime.timedelta(days=1))).values_list("sendID_id", "eval_date", "receiveID_id"))
    token = pd.DataFrame(rows ,columns=["sender","date","receiver"])
    empInfo = pd.DataFrame(list(Employee.objects.values_list("id", "level")), columns=["ID", "level"])
    empInfo["sender"] = empInfo.ID
    empInfo["receiver"] = empInfo.ID

    empInfo["senderlevel"] = empInfo.level
    empInfo["receiverlevel"] = empInfo.level

    token = pd.merge(token, empInfo[["sender", "senderlevel"]], how="left", on="sender")
    token = pd.merge(token, empInfo[["receiver", "receiverlevel"]], how="left", on="receiver")

    token.date = token.date.map(lambda x: datetime.datetime.strptime(str(x)[:10], "%Y-%m-%d"))

    token["month"] = token.date.map(lambda x: x.year * 12 + x.month)

    token_sendcnt = token.groupby(["sender", "month"]).size().reset_index(name="sendcount")

    token_receivecnt = token.groupby(["receiver", "month"]).size().reset_index(name="receivecount")

    token_receiveavg = token_receivecnt.groupby("receiver").agg({"receivecount": mean_except_outlier}).reset_index()

    token_sendavg = token_sendcnt.groupby("sender").agg({"sendcount": mean_except_outlier}).reset_index()

    token_sendavg["ID"] = token_sendavg.sender
    token_receiveavg["ID"] = token_receiveavg.receiver

    token_sendReceiveAvg_month = pd.merge(token_sendavg, token_receiveavg, on="ID", how="outer")

    token_sendReceiveAvg_month = token_sendReceiveAvg_month[["ID", "sendcount", "receivecount"]]

    token_sendReceiveAvg_month.columns = ["ID", "sendCntMean_mon", "receiveCntMean_mon"]

    token_sendReceiveAvg_month = token_sendReceiveAvg_month.fillna(0)

    token_sendReceiveAvg_month = token_sendReceiveAvg_month.apply(lambda x: round(x, 2))

    token_sendReceiveAvg_month = pd.merge(token_sendReceiveAvg_month, empInfo[["ID", "level"]], how="left", on="ID")

    token_sendReceiveAvg_month.level = token_sendReceiveAvg_month.level.fillna("null_level")

    token_sendcnt["ID"] = token_sendcnt.sender
    token_receivecnt["ID"] = token_receivecnt.receiver

    token_sendreceiveCnt = pd.merge(token_sendcnt, token_receivecnt, on=["ID", "month"], how="outer")

    token_sendreceiveCnt = token_sendreceiveCnt.fillna(0)

    token_sendreceiveCnt["sendReceiveCnt"] = token_sendreceiveCnt.sendcount + token_sendreceiveCnt.receivecount

    token_sendreceiveCnt = token_sendreceiveCnt[["ID", "month", "sendReceiveCnt"]]

    token_send_add_receiveAvg_month = token_sendreceiveCnt.groupby("ID").agg(
        {"sendReceiveCnt": mean_except_outlier}).reset_index()

    token_send_add_receiveAvg_month.columns = ["ID", "sendReceiveCntAvg_mon"]

    tokendata = pd.merge(token_sendReceiveAvg_month, token_send_add_receiveAvg_month, how="left", on="ID")

    tokendata.sendReceiveAvg = tokendata.sendReceiveCntAvg_mon.map(lambda x: round(x, 2))

    groupmean = tokendata.drop("ID", axis=1).groupby("level").agg(mean_except_outlier).reset_index()
    levelmean = pd.merge(pd.DataFrame(tokendata.level), groupmean, how="left", on="level")

    for i in levelmean.columns[1:]:
        tokendata[i + "_byLevel"] = round(100 * tokendata[i] / levelmean[i], 2)

    tokendata = tokendata.drop("level", axis=1)

    tokendata = tokendata.applymap(lambda x: round(x, 2))

    tokendata = pd.merge(empInfo[["ID"]], tokendata, how="left", on="ID")
    token_data_list = []
    for i in range(len(tokendata)):
        df_instance = tokendata.iloc[i,:]
        empid = df_instance.ID
        params = {}
        try:
            employeeID = Employee.objects.get(pk = empid)
            params.update({"employeeID":employeeID})
        except:
            continue
        employeeID_confirm = empid
        params.update({"employeeID_confirm": employeeID_confirm})
        eval_date = dateRange[1]
        params.update({"eval_date": eval_date})
        start_date = dateRange[0]
        params.update({"start_date": start_date})
        token_send = df_instance.sendCntMean_mon
        params.update({"token_send": token_send})
        token_receive = df_instance.receiveCntMean_mon
        params.update({"token_receive": token_receive})
        token_send_byLevelRatio = df_instance.sendCntMean_mon_byLevel
        params.update({"token_send_byLevelRatio": token_send_byLevelRatio})
        token_receive_byLevelRatio = df_instance.receiveCntMean_mon_byLevel
        params.update({"token_receive_byLevelRatio": token_receive_byLevelRatio})
        token_data = Token_Data(**params)
        token_data_list.append(token_data)
    Token_Data.objects.bulk_create(token_data_list)

