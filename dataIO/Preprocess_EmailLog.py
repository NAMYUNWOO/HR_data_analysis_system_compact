import numpy as np
import datetime
from django.db.models import Q
from functools import reduce
from index.models import Employee
from .Edge import *

def isIn_q1_sub_3iqr(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.76)
    iqr = q3 - q1
    # print("q1:{}\nq2:{}\niqr:{}".format(q1,q3,iqr))
    return lambda x: x >= (q1 - 3 * iqr)


def mean_with_option(opt_func):
    def mean(series):
        opt = opt_func(series)
        return round(np.mean(series.where(opt).dropna()), 2)
    return mean

def mean_last6mon(series):
    len_ = len(series)
    return np.mean(series[-min(6,len_):])


def get_nodes_sizes_df(dt, temp):
    if type(dt) == pd.core.frame.DataFrame:
        return dt
    tempdf = temp[temp.year_x_month == dt].edge.iloc[0].nodes_sizes()
    tempdf["month"] = pd.Series([dt] * len(tempdf))
    return tempdf



def preprocess_EmailLog(EmailLog,EmailData,dateRange):
    rows = list ( EmailLog.objects.filter(Q(eval_date__gte=dateRange[0]) & Q(eval_date__lte=dateRange[1] + datetime.timedelta(days=1))).values_list("sendID_id","receiveID_id","eval_date","nwh") )
    emaillog_v2 = pd.DataFrame(rows,columns=["senderID","receiverID","send_dt","isOverTime_email"])
    del rows
    emaillog_v2["year_x_month"] = emaillog_v2.send_dt.map(lambda x: x.month + x.year * 12)
    idExist = pd.Series(emaillog_v2.senderID.unique().tolist() + emaillog_v2.receiverID.unique().tolist()).unique()
    temp = emaillog_v2[["senderID", "year_x_month"]].groupby(["senderID", "year_x_month"]).size().reset_index(name="monthly_send")[["senderID", "monthly_send"]]
    sendCount_total_df = temp.groupby("senderID").monthly_send.agg(mean_with_option(isIn_q1_sub_3iqr)).reset_index(name="sendCount_total")
    temp = emaillog_v2[emaillog_v2.isOverTime_email]
    temp = temp[["senderID", "year_x_month"]].groupby(["senderID", "year_x_month"]).size().reset_index(name="monthly_send")[["senderID", "monthly_send"]]
    sendCount_overtime_df = temp.groupby("senderID").monthly_send.agg(mean_with_option(isIn_q1_sub_3iqr)).reset_index(name="sendCount_overtime")
    temp = emaillog_v2[["receiverID", "year_x_month"]].groupby(["receiverID", "year_x_month"]).size().reset_index(name="monthly_receive")[["receiverID", "monthly_receive"]]
    receiveCount_total_df = temp.groupby("receiverID").monthly_receive.agg(mean_with_option(isIn_q1_sub_3iqr)).reset_index(name="receiveCount_total")
    receiveCount_total_df.columns = ["senderID", "receiveCount_total"]
    count_df = reduce(lambda df1, df2: pd.merge(df1, df2, how="outer", on="senderID"),[sendCount_total_df, sendCount_overtime_df, receiveCount_total_df])
    count_df.columns = ["ID"] + list(count_df.columns)[1:]
    emp_info = pd.DataFrame( list(Employee.objects.values_list("bu" ,"id","level")) , columns= ["group","ID","level"])
    emp_info.group = emp_info.group.fillna("null_group")
    emp_info.level = emp_info.level.fillna("null_level")
    email_v0 = pd.merge(emp_info[emp_info.ID.isin(idExist)], count_df, how="left", on="ID").fillna(0)
    mean_by_level = email_v0[['level', 'sendCount_total', 'sendCount_overtime', 'receiveCount_total']].groupby("level").transform("mean")
    temp = round(100 * email_v0[['sendCount_total', 'sendCount_overtime', 'receiveCount_total']] / mean_by_level, 2)
    temp.columns = temp.columns.map(lambda x: x + "_by_level")
    email_v1 = pd.concat([email_v0, temp], axis=1)

    temp = emaillog_v2.groupby(["senderID", "year_x_month"]).size().reset_index(name="sendCnt")
    q1_iqr_df = temp[["senderID", "sendCnt"]].groupby("senderID").transform(q1_3iqr)
    temp["q1_3iqr"] = q1_iqr_df["sendCnt"]

    temp = temp[temp.sendCnt >= temp.q1_3iqr][["senderID", "year_x_month", "sendCnt"]]

    temp = pd.merge(emaillog_v2, temp, how="left", on=["senderID", "year_x_month"])
    temp = temp[~temp.sendCnt.isnull()]
    temp = temp[temp.columns[:-1]]
    temp = temp.groupby(["year_x_month", "senderID", "receiverID"]).size().reset_index(name="sendCnt")
    temp.head()
    temp.index = range(len(temp))

    temp2 = np.array(temp[["senderID", "receiverID", "sendCnt"]])
    temp["edge"] = pd.Series(map(lambda x: Edge(n_from=x[0], n_to=x[1], weight=x[2]), temp2))

    temp = temp[["year_x_month", "edge"]].groupby("year_x_month").agg(monthly_node_size)

    temp["year_x_month"] = temp.index

    temp.index = range(len(temp))
    uniqueMon = temp.year_x_month.unique()
    if len(uniqueMon) == 1:
        temp = get_nodes_sizes_df(uniqueMon[0],temp)
    else:
        temp = reduce(lambda dt1,dt2:  pd.concat([get_nodes_sizes_df(dt1,temp),get_nodes_sizes_df(dt2,temp)],axis=0),uniqueMon)
    temp = temp.sort_values(["node_1", "month", "conn_size"])[["node_1", "node_2", "conn_size"]].groupby(
        ["node_1", "node_2"]).agg(mean_last6mon)

    temp_mean_last6mon = temp.reset_index()
    temp_mean_last6mon = temp_mean_last6mon[temp_mean_last6mon.conn_size >= 2.0]
    temp_mean_last6mon.index = range(len(temp_mean_last6mon))
    temp_nodesize = temp_mean_last6mon.groupby("node_1").size().reset_index(name="node_size")
    temp_nodesize.columns = ["ID", "node_size"]
    email_v2 = pd.merge(emp_info[emp_info.ID.isin(idExist)], temp_nodesize, how="left", on="ID").fillna(0)
    mean_by_level = email_v2[['level', 'node_size']].groupby("level").transform("mean")
    temp = round(100 * email_v2[['node_size']] / mean_by_level, 2)
    temp.columns = temp.columns.map(lambda x: x + "_by_level")
    email_v2 = pd.concat([email_v2, temp], axis=1)
    emp_info2 = emp_info.copy()
    emp_info2.index = emp_info2.ID

    def treatNan(x):
        try:
            return emp_info2.loc[x, "level"]
        except:
            return "nulll_level"

    temp_mean_last6mon["node_1_level"] = temp_mean_last6mon.node_1.map(lambda x: treatNan(x))
    temp_mean_last6mon["node_2_level"] = temp_mean_last6mon.node_2.map(lambda x: treatNan(x))
    temp_nodesize = temp_mean_last6mon[temp_mean_last6mon.node_1_level != temp_mean_last6mon.node_2_level].groupby("node_1").size().reset_index(name="node_size_other_group")
    temp_nodesize.columns = ["ID"] + list(temp_nodesize.columns[1:])
    email_v3 = pd.merge(emp_info[emp_info.ID.isin(idExist)], temp_nodesize, how="left", on="ID").fillna(0)
    email_v123M = reduce(lambda x, y: pd.merge(x, y, how="outer", on=["ID", "group", "level"]),[emp_info,email_v1, email_v2, email_v3])
    EmailData_list = []
    for i in range(len(email_v123M)):
        df_instance = email_v123M.iloc[i,:]
        try:
            employeeID = Employee.objects.get(pk=df_instance.ID)
        except:
            continue
        employeeID_confirm = df_instance.ID
        eval_date = dateRange[1]
        start_date = dateRange[0]
        sendCnt = df_instance.sendCount_total
        sendCnt_nwh = df_instance.sendCount_overtime
        receiveCnt = df_instance.receiveCount_total
        sendCnt_byLevelRatio = df_instance.sendCount_total_by_level
        sendCnt_nwh_byLevelRatio = df_instance.sendCount_overtime_by_level
        receiveCnt_byLevelRatio = df_instance.receiveCount_total_by_level
        nodeSize = df_instance.node_size
        nodeSize_byLevelRatio = df_instance.node_size_by_level
        nodeSize_byGroupRatio = df_instance.node_size_other_group
        emailData = EmailData(employeeID=employeeID,employeeID_confirm=employeeID_confirm,eval_date=eval_date,start_date=start_date,
                              sendCnt=sendCnt,sendCnt_nwh=sendCnt_nwh,receiveCnt=receiveCnt,sendCnt_byLevelRatio=sendCnt_byLevelRatio,
                              sendCnt_nwh_byLevelRatio=sendCnt_nwh_byLevelRatio,receiveCnt_byLevelRatio=receiveCnt_byLevelRatio,
                              nodeSize=nodeSize,nodeSize_byLevelRatio=nodeSize_byLevelRatio,nodeSize_byGroupRatio=nodeSize_byGroupRatio)
        EmailData_list.append(emailData)
    EmailData.objects.bulk_create(EmailData_list)
