import pandas as pd

df = pd.read_csv("data/punts/punts-mesura-ste.csv")

# select only needed columns
df = df[["planta-numero", "id_vell", "id"]]

df.columns = ["Punt", "Ubicació", "ID"]

latex = df.to_latex(
    index=False,
    escape=True,
    column_format="lll"
)

print(latex)