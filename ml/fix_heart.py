import pandas as pd

df = pd.read_csv(
    "D:/medisimplify/ml/data/heart_cleveland.csv",
    header=None,
    names=[
        "age",
        "sex",
        "cp",
        "trestbps",
        "chol",
        "fbs",
        "restecg",
        "thalach",
        "exang",
        "oldpeak",
        "slope",
        "ca",
        "thal",
        "target",
    ],
)

df = df.replace("?", pd.NA)
df["target"] = (df["target"].astype(float) > 0).astype(int)

df.to_csv("D:/medisimplify/ml/data/heart-selected-columns.csv", index=False)
print("Done!")
print(df.columns.tolist())
print(df.shape)
print(df.head())
