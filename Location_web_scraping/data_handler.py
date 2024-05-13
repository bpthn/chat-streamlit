import pandas as pd

def save_to_csv(df, file_name):
    df.to_csv(file_name, index=False)
    