import pandas as pd
import glob

# path = "data/*-1h.csv"
path = "data/binance-BNBUSDT-1m.csv"
for file in glob.glob(path):
    print(file)
    df = pd.read_csv(file, sep=',', header=None)

    print(df)
    filtered_data = df.iloc[:,0]
    print(filtered_data)

    # filtered_data.replace('\d+\.\d*','00',regex=True, inplace = True)
    # filtered_data.replace('\d+\.\d*','00',regex=True, inplace = True)
    print(filtered_data)
    print(df)
    # df.reset_index(drop=True, inplace=True)
    # df.to_csv(file, header=None, index=False)
    print('---------- DONE ----------')