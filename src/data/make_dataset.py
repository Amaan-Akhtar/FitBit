import pandas as pd
from glob import glob 

files = glob("../../data/raw/MetaMotion/*.csv")

def read_data_from_files(files):
    data_path = "../../data/raw/MetaMotion\\"
    acc_df = pd.DataFrame()
    gyr_df = pd.DataFrame()
    acc_set = 1
    gyr_set = 1
    for f in files:
        participant = f.split("-")[0].replace(data_path,"")
        label = f.split("-")[1]
        category = f.split("-")[2].rstrip("1234567890").rstrip("_MetaWear_").rstrip("1234567890")
        
        df = pd.read_csv(f)
        df["participant"] = participant
        df["label"] = label
        df["category"] = category
        
        if "Accelerometer" in f:
            df["set"] = acc_set
            acc_df = pd.concat([acc_df,df])
            acc_set+=1
        else:
            df["set"] = gyr_set
            gyr_df = pd.concat([gyr_df,df])
            gyr_set+=1

    acc_df.index = pd.to_datetime(acc_df["epoch (ms)"],unit="ms")
    gyr_df.index = pd.to_datetime(gyr_df["epoch (ms)"],unit="ms")
    del acc_df["epoch (ms)"]
    del acc_df["time (01:00)"]
    del acc_df["elapsed (s)"]

    del gyr_df["epoch (ms)"]
    del gyr_df["time (01:00)"]
    del gyr_df["elapsed (s)"]
    return acc_df,gyr_df

acc_df,gyr_df = read_data_from_files(files)

# --------------------------------------------------------------
# Merging datasets
# --------------------------------------------------------------
data_merged = pd.concat([acc_df.iloc[:,:3],gyr_df],axis=1)
data_merged.columns = [
    "acc_x",
    "acc_y",
    "acc_z",
    "gyr_x",
    "gyr_y",
    "gyr_z",
    "participant",
    "label",
    "category",
    "set",
]


# --------------------------------------------------------------
# Resample data (frequency conversion)
# --------------------------------------------------------------

# Accelerometer:    12.500HZ
# Gyroscope:        25.000Hz

sampling = {
    "acc_x" : "mean",
    "acc_y" : "mean",
    "acc_z" : "mean",
    "gyr_x" : "mean",
    "gyr_y" : "mean",
    "gyr_z" : "mean",
    "participant" : "last",
    "label" : "last",
    "category" : "last",
    "set" : "last",
}

days = [g for n,g in data_merged.groupby(pd.Grouper(freq="D"))]

data_resampled = pd.concat([df.resample(rule="200ms").apply(sampling).dropna() for df in days])

data_resampled.info()
data_resampled["set"] = data_resampled['set'].astype('int')
# --------------------------------------------------------------
# Export dataset
# --------------------------------------------------------------
data_resampled.to_pickle("../../data/interim/01_data_processed.pkl")  #pickle will not change the indexing but csv files will add their own indexing


