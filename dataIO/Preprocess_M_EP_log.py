import pandas as pd
import re
import datetime
import numpy as np
from django.db.models import Q
from index.models import Employee
from .models import ifexistDel
N_IQR = 3

def mean_except_outlier(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    series2 = series[series > q1 - N_IQR*iqr]
    if len(series2) == 0:
        return np.mean(series)
    return np.mean(series2)


def preprocess_M_EP_log(M_EP_log,M_EPData,dateRange):
    late = [20, 3]
    early = [5, 8]

    rows = list(M_EP_log.objects.filter(
        Q(eval_date__gte=dateRange[0]) & Q(eval_date__lte=dateRange[1] + datetime.timedelta(days=1))).values_list(
        "eval_date", "employeeID_id"))
    df = pd.DataFrame(rows, columns=["dt", "ID"])
    del rows
    df.index = range(len(df))

    df = df[~ df.ID.isin([i for i in df.ID.unique() if bool(re.search("[^0-9]", str(i)))])]

    df.ID = df.ID.astype(int)

    df["month"] = df.dt.map(lambda x: x.year * 12 + x.month)

    df["hour"] = df.dt.map(lambda x: x.hour)

    df["late"] = (late[0] <= df.hour) | (df.hour <= late[1])

    df["early"] = (early[0] <= df.hour) & (df.hour <= early[1])

    df["normal"] = (early[1] < df.hour) & (df.hour < late[0])

    df.index = range(len(df))

    df_late = df.drop(["early", "normal"], axis=1)
    df_early = df.drop(["late", "normal"], axis=1)
    df_normal = df.drop(["late", "early"], axis=1)
    df_lateCnt = df_late[df_late.late].groupby(["ID", "month"]).size().reset_index(name="lateCnt_mon")

    df_earlyCnt = df_early[df_early.early].groupby(["ID", "month"]).size().reset_index(name="earlyCnt_mon")

    df_normalCnt = df_normal[df_normal.normal].groupby(["ID", "month"]).size().reset_index(name="normalCnt_mon")

    df_lateCntAvg = df_lateCnt.groupby("ID").agg({"lateCnt_mon": mean_except_outlier}).reset_index()

    df_earlyCntAvg = df_earlyCnt.groupby("ID").agg({"earlyCnt_mon": mean_except_outlier}).reset_index()

    df_normalCntAvg = df_normalCnt.groupby("ID").agg({"normalCnt_mon": mean_except_outlier}).reset_index()

    keydf = pd.DataFrame(df.ID.unique())
    keydf.columns = ["ID"]

    normal_early_late_df = pd.merge(df_normalCntAvg, pd.merge(df_earlyCntAvg, df_lateCntAvg, on="ID", how="outer"),
                                    on="ID", how="outer")

    df_normalLateEarlyCntAvg = pd.merge(keydf, normal_early_late_df, how="left", on="ID")

    df_normalLateEarlyCntAvg = df_normalLateEarlyCntAvg.fillna(0)

    df_normalLateEarlyCntAvg = df_normalLateEarlyCntAvg.applymap(lambda x: round(x, 2))
    empinfo = pd.DataFrame(list(Employee.objects.values_list("id", "level")), columns=["ID", "level"])

    mepdata = pd.merge(empinfo, df_normalLateEarlyCntAvg, on="ID", how="left").dropna()

    mepdata.index = range(len(mepdata))

    mepdata.columns = ["ID", "level", "normalCntAvg_mon", "earlyCntAvg_mon", "lateCntAvg_mon"]

    levelmean = mepdata.drop("ID", 1).groupby("level").agg(mean_except_outlier).reset_index()

    levelmean = pd.merge(pd.DataFrame(mepdata.level), levelmean, how="left", on="level").drop("level", 1)

    for c in levelmean.columns:
        mepdata[c + "_byLevel"] = round(100 * mepdata[c] / levelmean[c], 2)

    print("null size", mepdata.earlyCntAvg_mon_byLevel.isnull().sum())

    mepdata.index = range(len(mepdata))

    mepdata = pd.merge(empinfo, mepdata, how="left", on="ID")
    M_EPData_list = []
    for i in range(len(mepdata)):
        df_instance = mepdata.iloc[i, :]
        empid = df_instance.ID
        params = {}
        try:
            employeeID = Employee.objects.get(pk=empid)
            params.update({"employeeID":employeeID})
        except:
            continue
        employeeID_confirm = empid
        params.update({"employeeID_confirm": employeeID_confirm})
        eval_date = dateRange[1]
        params.update({"eval_date": eval_date})
        start_date = dateRange[0]
        ifexistDel(M_EPData,employeeID,eval_date,start_date)
        params.update({"start_date": start_date})
        mep_normal = df_instance.normalCntAvg_mon
        params.update({"mep_normal": mep_normal})
        mep_early = df_instance.earlyCntAvg_mon
        params.update({"mep_early": mep_early})
        mep_late = df_instance.lateCntAvg_mon
        params.update({"mep_late": mep_late})
        mep_normal_byLevelRatio = df_instance.normalCntAvg_mon_byLevel
        params.update({"mep_normal_byLevelRatio": mep_normal_byLevelRatio})
        mep_early_byLevelRatio = df_instance.earlyCntAvg_mon_byLevel
        params.update({"mep_early_byLevelRatio": mep_early_byLevelRatio})
        mep_late_byLevelRatio = df_instance.lateCntAvg_mon_byLevel
        params.update({"mep_late_byLevelRatio": mep_late_byLevelRatio})
        mep_Data = M_EPData(**params)
        M_EPData_list.append(mep_Data)
    M_EPData.objects.bulk_create(M_EPData_list)