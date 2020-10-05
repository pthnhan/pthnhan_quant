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
        threshold2 =  1,
        threshold3 = 1.5,
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
                        detect = "dump"
                        price_bid_max_matched_t_minus_1 = max(MD.getPbidVbidmatched(start, end-2)[0])
                        price_bid_min_matched_t_minus_4 = min(MD.getPbidVbidmatched(start, end-5)[0])
                        if price_bid_max_matched_t_minus_1 - price_bid_min_matched_t_minus_4 > self.params["threshold3"]:
                            detect = "pump and dump"
        return detect

if __name__ == '__main__':
    df = pd.read_csv('/home/thanhnhan/Desktop/pthnhan_quant/HFT_strategies/strategies/VN30F1M.csv', index_col="Date", parse_dates=['Date'])
    df = df[df.index.isnull() == False]
    date =[]
    s = 1000
    point = [s]
    for i in range(1,31):
        if i<10:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-0"+str(i)])]
        if 10<=i<20:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-1"+str(i%10)])]
        if 20<=i<30:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-2"+str(i%10)])]
        if 30<=i:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-3"+str(i%10)])]

        df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-30"])]
        df_date_hour_morning = pd.concat(
            [df_date[df_date.index.strftime("%H").isin(["02"])], df_date[df_date.index.strftime("%H").isin(["03"])],
             df_date[df_date.index.strftime("%H").isin(["04"])]])
        df_date_hour_afternoon = pd.concat(
            [df_date[df_date.index.strftime("%H").isin(["06"])], df_date[df_date.index.strftime("%H").isin(["07"])]])

        df_date_hour_morning_or_afternoon = df_date_hour_morning
        MD = ManipulationDetection(df_date_hour_morning_or_afternoon)
        count = 1
        while count <3:
            l = 0
            check = []
            dump = []
            pump_and_dump = []
            while l < len(df_date_hour_morning_or_afternoon) - 200:
                print(l)
                bid_price = df_date_hour_morning_or_afternoon[l:l + 200]["bid_price"]
                ask_price = df_date_hour_morning_or_afternoon[l:l + 200]["ask_price"]
                detect = MD.detect_pump_and_dump(l, l + 200)

                if detect == "dump":
                    check.append("dump")
                    print(f"Detected dumping state at the following times!")
                    bidprice = bid_price[-1]
                    print(f"bid_price: {bidprice}")
                    if len(dump) < len(pump_and_dump):
                        sum_dump = sum(i for i in dump)
                        sump_pump_and_dump = sum(i for i in pump_and_dump)
                        if bidprice + sum_dump > sump_pump_and_dump:
                            dump.append(bidprice)
                            s = s + bidprice - 0.054
                            point.append(s)
                    if len(dump) < len(pump_and_dump):
                        if check[-6:] == ["pump and dump", "pump and dump", "pump and dump", "dump","dump","dump"]:
                            dump.append(bidprice)
                            s = s + bidprice - 0.054
                            point.append(s)

                if detect == "pump and dump":
                    check.append("pump and dump")
                    print(f"Detected pumping and dumping state at the following times!")
                    if len(dump) == len(pump_and_dump) and l < len(df_date_hour_morning_or_afternoon) - 1000:
                        if len(pump_and_dump) == 0 and check[-3:] == ["pump and dump", "pump and dump", "pump and dump"]:
                            askprice = ask_price[-1]
                            print(f"ask_price: {askprice}")
                            pump_and_dump.append(askprice)
                            s = s - askprice - 0.054
                        elif check[-6:] == ["dump", "dump", "dump", "pump and dump", "pump and dump", "pump and dump"]:
                            askprice = ask_price[-1]
                            print(f"ask_price: {askprice}")
                            pump_and_dump.append(askprice)
                            s = s - askprice - 0.054

                # if l == len(df_date_hour_morning_or_afternoon) - 400 and len(pump_and_dump) > len(dump):
                #         print(f"bid_price: {bid_price[-1]}")
                #         s = s + bid_price[-1] -0.054
                print(f"s: {s}")
                l += 1
            print(f"sell: {dump}")
            print(f"buy: {pump_and_dump}")
            df_date_hour_morning_or_afternoon = df_date_hour_afternoon
            MD = ManipulationDetection(df_date_hour_morning_or_afternoon)
            count +=1
        date.append(point[-1])
    print(date)
    for i in range(0,30):
        print(f"Ngay {i+1}/9/2020: {date[i]}")
    plt.plot(point)
    plt.show()
