import backtrader as bt
import pandas as pd
import numpy as np
from rework_backtrader.simulation import SimulationEngine
import math
import matplotlib.pyplot as plt
from tabulate import tabulate


class ManipulationDetection():
    def __init__(self, df):
        self.params = dict(
        threshold1 = 0.5,
        threshold2 = 1.5,
        threshold3 = 2
    )
        self.df = df

    def getPsellVsellMatched(self, start, end):
        df = self.df[start:end]
        last_matched_price = df['last_matched_price']
        last_matched_vol = df['last_matched_vol']
        price_sell_matched = []
        vol_sell_matched =[]
        for i in range(1,len(last_matched_price)):
            if last_matched_price[i] != last_matched_price[i-1]:
                ask_price = [df['ask_price_1'][i - 1], df['ask_price_2'][i - 1],
                             df['ask_price_3'][i - 1],
                             df['ask_price_4'][i - 1], df['ask_price_5'][i - 1], df['ask_price_6'][i - 1],
                             df['ask_price_7'][i - 1],
                             df['ask_price_8'][i - 1], df['ask_price_9'][i - 1], df['ask_price_10'][i - 1]]
                if (last_matched_price[i] in ask_price):
                    price_sell_matched.append(last_matched_price[i])
                    vol_sell_matched.append(last_matched_vol[i])
        return price_sell_matched, vol_sell_matched

    def getPbidVbidmatched(self, start, end):
        df = self.df[start:end]
        last_matched_price = df['last_matched_price']
        last_matched_vol = df['last_matched_vol']
        price_bid_matched = []
        vol_bid_matched =[]
        for i in range(1,len(last_matched_price)):
            if last_matched_price[i] != last_matched_price[i-1]:
                bid_price = [df['bid_price_1'][i - 1], df['bid_price_2'][i - 1],
                             df['bid_price_3'][i - 1],
                             df['bid_price_4'][i - 1], df['bid_price_5'][i - 1], df['bid_price_6'][i - 1],
                             df['bid_price_7'][i - 1],
                             df['bid_price_8'][i - 1], df['bid_price_9'][i - 1], df['bid_price_10'][i - 1]]
                if (last_matched_price[i] in bid_price):
                    price_bid_matched.append(last_matched_price[i])
                    vol_bid_matched.append(last_matched_vol[i])
        return price_bid_matched, vol_bid_matched

    #Check pump and dump
    def detect_pump_and_dump(self, start, end):
        df = self.df[start:end]
        vol_buy_cancelled = df['cancelled_bid']
        detect = ""
        vol_buy_cancelled_at_t = vol_buy_cancelled.iloc[-2]
        vol_buy_matched = MD.getPbidVbidmatched(start, end-1)[1]
        if len(vol_buy_matched) >0:
            mean_vol_buy_matched_t = np.mean(vol_buy_matched)
            if vol_buy_cancelled_at_t > mean_vol_buy_matched_t * self.params["threshold1"]:
                if len(MD.getPsellVsellMatched(start, end-1)[0]) > 0:
                    price_sell_max_matched_t = max(MD.getPsellVsellMatched(start, end-1)[0])
                    price_sell_min_matched_t_add_1 = min(MD.getPsellVsellMatched(start, end)[0])
                    if price_sell_max_matched_t-price_sell_min_matched_t_add_1 > self.params["threshold2"]:
                        price_bid_max_matched_t_minus_1 = max(MD.getPbidVbidmatched(start, end-2)[0])
                        price_bid_min_matched_t_minus_4 = min(MD.getPbidVbidmatched(start, end-5)[0])
                        if price_bid_max_matched_t_minus_1 - price_bid_min_matched_t_minus_4 > self.params["threshold3"]:
                            detect = "pump and dump"
                            print("Detected pumping and dumping state!")
        return detect

def max_drawdown(booksize,point):
    mdd = 0
    peak = point[0]
    for x in point:
        if x > peak:
            peak = x
        dd = (peak - x) / booksize
        if dd > mdd:
            mdd = dd
    return mdd

def sharpe_ratio(date):
    returnSeries = []
    for i in range(1, len(date)):
        returnSeries.append(date[i]-date[i-1])
    return (np.mean(returnSeries)/np.std(returnSeries))* np.sqrt(252)

if __name__ == '__main__':
    df = pd.read_csv('/home/thanhnhan/Desktop/pthnhan_quant/HFT_strategies/strategies/VN30F1M.csv', index_col="Date", parse_dates=['Date'])
    df = df[df.index.isnull() == False]
    date =[]
    s = 1000
    point = [s]
    for i in range(25,31):
        if i<10:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-0"+str(i)])]
        if 10<=i<20:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-1"+str(i%10)])]
        if 20<=i<30:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-2"+str(i%10)])]
        if 30<=i:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-3"+str(i%10)])]

        df_date_hour_morning = pd.concat(
            [df_date[df_date.index.strftime("%H").isin(["02"])], df_date[df_date.index.strftime("%H").isin(["03"])],
             df_date[df_date.index.strftime("%H").isin(["04"])]])
        df_date_hour_afternoon = pd.concat(
            [df_date[df_date.index.strftime("%H").isin(["06"])], df_date[df_date.index.strftime("%H").isin(["07"])]])

        count = 1
        while count <3:
            if count == 1:
                df_date_hour_morning_or_afternoon = df_date_hour_morning
            if count == 2:
                df_date_hour_morning_or_afternoon = df_date_hour_afternoon

            print(df_date_hour_morning_or_afternoon)
            MD = ManipulationDetection(df_date_hour_morning_or_afternoon)
            l = 0
            sell = []
            buy = []
            pump_and_dump = 0
            no_pump = 11
            gd = 0
            while l < len(df_date_hour_morning_or_afternoon) - 200:
                print(l)
                bid_price = df_date_hour_morning_or_afternoon[l:l + 200]["bid_price"]
                ask_price = df_date_hour_morning_or_afternoon[l:l + 200]["ask_price"]
                detect = MD.detect_pump_and_dump(l, l + 200)

                if detect == "pump and dump":
                    if no_pump >10 and gd ==0:
                        print(f" ask_price -1: {ask_price[-1]}")
                        print(f" ask_price -10: {ask_price[-10]}")
                        temp = s
                        print(f"ask_price: {ask_price[-1]}")
                        s = s - ask_price[-1]-0.054
                        print(f"s: {s}")
                        gd = -1
                    no_pump = 0

                if detect != "pump and dump": no_pump += 1

                if gd == -1:
                    if s + bid_price[-1] - temp >= 0.7:
                        print(f"0.7 - bid_price: {bid_price[-1]}")
                        print(f"0.7 - ask_price: {ask_price[-1]}")
                        s = s + bid_price[-1] - 0.054
                        point.append(s)
                        gd = 0
                    if s + bid_price[-1] - temp >= 0.6 and gd ==-1:
                        print(f"0.6 - bid_price: {bid_price[-1]}")
                        print(f"0.6 - ask_price: {ask_price[-1]}")
                        s = s + bid_price[-1] - 0.054
                        point.append(s)
                        gd = 0
                    if s + bid_price[-1] - temp >= 0.5 and gd ==-1:
                        print(f"0.5 - bid_price: {bid_price[-1]}")
                        print(f"0.5 - ask_price: {ask_price[-1]}")
                        s = s + bid_price[-1] - 0.054
                        point.append(s)
                        gd = 0

                    if s + bid_price[-1] - temp >= 0.4 and gd ==-1:
                        print(f"0.4 - bid_price: {bid_price[-1]}")
                        print(f"0.4 - ask_price: {ask_price[-1]}")
                        s = s + bid_price[-1] - 0.054
                        point.append(s)
                        gd = 0

                    if s + bid_price[-1] - temp >= 0.3 and gd ==-1:
                        print(f"0.3 - bid_price: {bid_price[-1]}")
                        print(f"0.3 - ask_price: {ask_price[-1]}")
                        s = s + bid_price[-1] - 0.054
                        point.append(s)
                        gd = 0

                    if s + bid_price[-1] - temp >= 0.2 and gd ==-1:
                        print(f"0.2 - bid_price: {bid_price[-1]}")
                        print(f"0.2 - ask_price: {ask_price[-1]}")
                        s = s + bid_price[-1] - 0.054
                        point.append(s)
                        gd = 0

                    if pump_and_dump == 15 and gd == -1:
                        print(f"bid_price: {bid_price[-1]}")
                        print(f"ask_price: {ask_price[-1]}")
                        s = s + bid_price[-1] - 0.054
                        point.append(s)
                        gd = 0

                    if no_pump >10 and gd == -1:
                        print(f"no_pump - bid_price: {bid_price[-1]}")
                        print(f"no_pump - ask_price: {ask_price[-1]}")
                        s = s + bid_price[-1] - 0.054
                        point.append(s)
                        gd = 0
                if l >len(df_date_hour_morning_or_afternoon)-400 and gd ==-1:
                    print(f"time out - bid_price: {bid_price[-1]}")
                    print(f"time out - ask_price: {ask_price[-1]}")
                    s = s + bid_price[-1] - 0.054
                    l+=400
                print(f"s: {s}")
                l += 1
            print(f"sell: {sell}")
            print(f"buy: {buy}")
            count +=1
        date.append(point[-1])
    print(date)
    for i in range(24,30):
        print(f"Ngay {i+1}/9/2020: {date[i-24]}")

    print(f"max draw down: {max_drawdown(1000, point)}")
    print(f"sharpe ratio: {sharpe_ratio(point)}")
    print(point)
    plt.plot(point)
    plt.show()