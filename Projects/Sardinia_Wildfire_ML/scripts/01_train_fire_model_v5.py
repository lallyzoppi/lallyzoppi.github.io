import pandas as pd
import numpy as np
import joblib
import json


from lightgbm import LGBMClassifier


from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve
)



# ======================================================
# FILE
# ======================================================

INPUT_FILE = "SARDINIA_FIRE_DAILY_ML.csv"

MODEL_FILE = "SARDINIA_FIRE_NEXT14_MODEL_FINAL.pkl"

METRIC_FILE = "SARDINIA_FIRE_MODEL_METRICS.json"




# ======================================================
# LOAD DATA
# ======================================================

df = pd.read_csv(INPUT_FILE)


df["date"] = pd.to_datetime(
    df["date"]
)


df = df.sort_values(
    [
        "date",
        "latitude",
        "longitude"
    ]
)


print("\nDATASET INIZIALE")
print(df.shape)





# ======================================================
# FEATURES
# ======================================================


df["month"] = (
    df["date"].dt.month
)


df["month_sin"] = np.sin(
    2*np.pi*df["month"]/12
)


df["month_cos"] = np.cos(
    2*np.pi*df["month"]/12
)



df["vpd"] = (
    df["t2m"]/10
)



df["dryness"] = (

    df["vpd"] *
    (df["wind_speed"]+1)

)





df["dry_days"] = (

    df.groupby(
        [
            "latitude",
            "longitude"
        ]
    )["tp"]
    .transform(

        lambda x:

        (x==0)
        .astype(int)
        .groupby(
            (x!=0).cumsum()
        )
        .cumsum()

    )

)






for lag in [1,3,7]:


    df[f"wind_lag_{lag}"] = (

        df.groupby(
            ["latitude","longitude"]
        )["wind_speed"]
        .shift(lag)

    )


    df[f"temp_lag_{lag}"] = (

        df.groupby(
            ["latitude","longitude"]
        )["t2m"]
        .shift(lag)

    )






for days in [7,14,30]:


    df[f"rain_{days}d"] = (

        df.groupby(
            ["latitude","longitude"]
        )["tp"]
        .rolling(days)
        .sum()
        .reset_index(
            level=[0,1],
            drop=True
        )

    )







# ======================================================
# TARGET
# ======================================================


def future_fire(x):

    values=x.values

    out=np.zeros(
        len(values)
    )


    for i in range(len(values)):

        end=min(
            i+15,
            len(values)
        )


        if i+1 < end:

            if values[i+1:end].sum() >= 1:

                out[i]=1


    return pd.Series(
        out,
        index=x.index
    )




df["fire_next14"] = (

    df.groupby(
        [
            "latitude",
            "longitude"
        ]
    )["fire"]
    .transform(
        future_fire
    )

)





df=df.dropna()



print("\nDATASET FINALE")
print(df.shape)






FEATURES=[


"latitude",
"longitude",

"month",
"month_sin",
"month_cos",

"u10",
"v10",

"t2m",
"tp",
"wind_speed",

"vpd",
"dryness",
"dry_days",

"wind_lag_1",
"wind_lag_3",
"wind_lag_7",

"temp_lag_1",
"temp_lag_3",
"temp_lag_7",

"rain_7d",
"rain_14d",
"rain_30d"

]







# ======================================================
# TRAIN TEST
# ======================================================


train = (
    df["date"] < "2024-01-01"
)


test = (
    df["date"] >= "2024-01-01"
)



X_train=df.loc[
    train,
    FEATURES
]


y_train=df.loc[
    train,
    "fire_next14"
]



X_test=df.loc[
    test,
    FEATURES
]


y_test=df.loc[
    test,
    "fire_next14"
]





print("\nTRAIN")
print(X_train.shape)


print("\nTEST")
print(X_test.shape)



print("\nCLASSI")

print(
    y_train.value_counts()
)






# ======================================================
# MODEL
# ======================================================


PARAMS={

"n_estimators":1500,

"learning_rate":0.015,

"num_leaves":96,

"max_depth":-1,

"min_child_samples":80,

"subsample":0.85,

"colsample_bytree":0.85,

"class_weight":"balanced",

"random_state":42,

"n_jobs":-1,

"verbosity":-1

}




print("\nPARAMETRI")

for k,v in PARAMS.items():
    print(k,":",v)






model=LGBMClassifier(
    **PARAMS
)





print("\nTRAINING...")


model.fit(
    X_train,
    y_train
)



print("\nTRAINING COMPLETATO")






# ======================================================
# PROBABILITA'
# ======================================================


prob=model.predict_proba(
    X_test
)[:,1]






# ======================================================
# THRESHOLD OTTIMALE
# ======================================================


precision,recall,thresholds = precision_recall_curve(
    y_test,
    prob
)



best_t=0.5

best_p=0

best_r=0




for p,r,t in zip(
    precision[:-1],
    recall[:-1],
    thresholds
):

    if r >= 0.50 and p > best_p:

        best_p=p
        best_r=r
        best_t=t






pred = (
    prob >= best_t
).astype(int)






# ======================================================
# RISCHIO
# ======================================================


def risk_level(p):

    if p >= 0.85:
        return "HIGH"

    elif p >= 0.60:
        return "MEDIUM"

    else:
        return "LOW"








# ======================================================
# REPORT
# ======================================================


cm=confusion_matrix(
    y_test,
    pred
)


roc=roc_auc_score(
    y_test,
    prob
)


pr=average_precision_score(
    y_test,
    prob
)



print("\nSOGLIA")
print("threshold:",best_t)
print("precision:",best_p)
print("recall:",best_r)



print(
    classification_report(
        y_test,
        pred,
        zero_division=0
    )
)



print(
    "ROC AUC:",
    roc
)


print(
    "PR AUC:",
    pr
)



print("\nMATRICE")

print(cm)



print("\nTP:",cm[1,1])
print("FN:",cm[1,0])
print("FP:",cm[0,1])
print("TN:",cm[0,0])






# ======================================================
# SAVE
# ======================================================


metrics={

"threshold":float(best_t),

"precision":float(best_p),

"recall":float(best_r),

"roc_auc":float(roc),

"pr_auc":float(pr),

"matrix":cm.tolist()

}



with open(
    METRIC_FILE,
    "w"
) as f:

    json.dump(
        metrics,
        f,
        indent=4
    )






joblib.dump(

{

"model":model,

"features":FEATURES,

"threshold":best_t,

"risk_levels":

{
"LOW":"<0.60",
"MEDIUM":"0.60-0.85",
"HIGH":">=0.85"
},

"params":PARAMS

},

MODEL_FILE

)





print("\nMODELLO FINALE SALVATO:")

print(
    MODEL_FILE
)

print(
    METRIC_FILE
)
