import os
import time
import pandas as pd
import datetime
import os

FETCH_URL = "https://poloniex.com/public?command=returnChartData&currencyPair=%s&start=%d&end=%d&period=300"
#PAIR_LIST = ["BTC_ETH"]
DATA_DIR = "data"
COLUMNS = ["date","high","low","open","close","volume","quoteVolume","weightedAverage"]

def get_data(pairs):
    errors = []
    pairs = pairs[:2]
    for pair in pairs:
        # try:
            datafile = os.path.join(DATA_DIR, pair+".csv")
            end_time = int(datetime.datetime.utcnow().timestamp())
            print(end_time)

            start_time = 1388534400     # 2014.01.01
            end_time = 9999999999#start_time + 86400*30

            url = FETCH_URL % (pair, start_time, end_time)
            # start = datetime.datetime.utcfromtimestamp(int(start_time)).strftime(%Y,%m,%d)
            # stop = datetime.datetime.utcfromtimestamp(int(end_time)).strftime(%Y,%m-%d)
            print("Get %s from %d to %d" % (pair, start_time , end_time ))

            df = pd.read_json(url, convert_dates=False)

            #import pdb;pdb.set_trace()

            if df["date"].iloc[-1] == 0:
                print("No data.")
                return

            end_time = df["date"].iloc[-1]
            outf = open(datafile, "a")
            df.to_csv(outf, index=False, columns=COLUMNS)
            outf.close()
        # except:
        #     print('Error with ' + pair)
        #     errors.append(pair)
    return errors

def main():

    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)

    df = pd.read_json("https://poloniex.com/public?command=return24hVolume")
    pairs = [pair for pair in df.columns if pair.startswith('BTC')]

    today = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    UTCtoday = datetime.datetime.utcnow().timestamp()

    errors = get_data(pairs)


    with open("ErrorLog.txt", "a") as text_file:
        text_file.write('\n' + today + '\n')
        text_file.write(str(int(UTCtoday)) + '\n')
        for error in errors:
            text_file.write(error + '\n')


if __name__ == '__main__':
    main()