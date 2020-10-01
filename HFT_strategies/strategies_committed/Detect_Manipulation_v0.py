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
        threshold2 =  1.5,
        threshold3 = 2,
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
        # while count <len(df)-1:
        #     vol_buy_cancelled_at_t = vol_buy_cancelled.iloc[count]
        #     vol_buy_matched = MD.getPbidVbidmatched(0,count)[1]
        #     # if len(MD.getPsellVsellMatched(0, count)[0]) > 0:
        #     #     price_sell_max_matched_t = max(MD.getPsellVsellMatched(0,count)[0])
        #     #     price_sell_min_matched_t_add_1 = min(MD.getPsellVsellMatched(0,count+1)[0])
        #     #     print(f"P_sell_max_matched_t: {price_sell_max_matched_t}")
        #     #     print(f"P_sell_min_matched_t_add_1: {price_sell_min_matched_t_add_1}")
        #     if len(vol_buy_matched) >0:
        #         mean_vol_buy_matched_t = np.mean(vol_buy_matched)
        #         if vol_buy_cancelled_at_t > mean_vol_buy_matched_t * self.params["threshold1"]:
        #             if len(MD.getPsellVsellMatched(0, count)[0]) > 0:
        #                 price_sell_max_matched_t = max(MD.getPsellVsellMatched(0, count)[0])
        #                 price_sell_min_matched_t_add_1 = min(MD.getPsellVsellMatched(0, count + 1)[0])
        #                 print(f"P_sell_max_matched_t: {price_sell_max_matched_t}")
        #                 print(f"P_sell_min_matched_t_add_1: {price_sell_min_matched_t_add_1}")
        #                 if price_sell_max_matched_t-price_sell_min_matched_t_add_1 > self.params["threshold2"]:
        #                     dump.append(start+count)
        #                     print(f'count_detected: {start+count}')
        #                     break
        #     count+=1
        #     print(f"count: {start+count}")
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


    # Check spoofing
    def spoofing(self):
        pass


    # # Caculate Volume imbalance
    # def volumeimbalance(self, start, end):
    #     df = self.df[start:end]
    #     V_bid_t = df['bid_qty']
    #     V_ask_t = df['ask_qty']
    #     volume_imbalance = []
    #     for i in range(start,end):
    #         print(f"V_bid_t: {V_bid_t[i]}")
    #         print(f"V_ask_t: {V_ask_t[i]}")
    #     #     volume_imbalance.append((V_bid_t[i]-V_ask_t[i])/(V_bid_t[i]+V_ask_t[i]))
    #     # plt.plot(volume_imbalance)
    #     # plt.show()



if __name__ == '__main__':
    df = pd.read_csv('/home/thanhnhan/Desktop/pthnhan_quant/HFT_strategies/strategies/VN30F1M.csv', index_col="Date", parse_dates=['Date'])
    df = df[df.index.isnull() == False]
    df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-29"])]
    # print(df[-len(df_date):-3000])
    index =[]
    MD = ManipulationDetection(df)
    # l=-len(df_date)
    # s = 0
    # check = []
    # dump = []
    # pump_and_dump = []
    # while l < 0:
    #     print(l)
    #     bid_price = df_date[l - 200:l]["bid_price"]
    #     ask_price = df_date[l - 200:l]["ask_price"]
    #     detect = MD.detect_pump_and_dump(l - 200, l)
    #     if detect == "dump":
    #         check.append("dump")
    #         print(f"Detected dumping state at the following times!")
    #         if check[-3:] == ["dump", "dump", "dump"] and abs(len(dump) + 1 - len(pump_and_dump) < 2):
    #             bidprice = bid_price[-1]
    #             print(f"bid_price: {bidprice}")
    #             dump.append(bidprice)
    #             print(f"dump : {dump}")
    #             print(f"pump and dump: {pump_and_dump}")
    #             s += bidprice
    #             print(f"s: {s}")
    #     if detect == "pump and dump":
    #         check.append("pump and dump")
    #         print(f"Detected pumping and dumping state at the following times!")
    #         if check[-3:] == ["pump and dump", "pump and dump", "pump and dump"] and abs(
    #                 len(pump_and_dump) + 1 - len(dump)) < 2:
    #             askprice = ask_price[-1]
    #             print(f"ask_price: {askprice}")
    #             pump_and_dump.append(askprice)
    #             print(f"dump : {dump}")
    #             print(f"pump and dump: {pump_and_dump}")
    #             s -= askprice
    #             print(f"s: {s}")
    #     l += 1
    # if s > 800:
    #     print(s-bidprice)
    # elif s <-800:
    #     print(s+askprice)
    # else: print(s)
    # print(f"sell: {dump}")
    # print(f"buy: {pump_and_dump}")

    for i in range(1,31):
        if i<10:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-0"+str(i)])]
        if 10<=i<20:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-1"+str(i%10)])]
        if 20<=i<30:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-2"+str(i%10)])]
        if 30<=i:
            df_date = df[df.index.strftime("%Y-%m-%d").isin(["2020-09-3"+str(i%10)])]

        MD = ManipulationDetection(df_date)
        l=200
        s = 0
        check = []
        dump = []
        pump_and_dump = []
        while l <len(df_date):
            bid_price = df_date[l-200:l]["bid_price"]
            ask_price = df_date[l-200:l]["ask_price"]
            detect = MD.detect_pump_and_dump(l - 200, l)
            if detect == "dump":
                check.append("dump")
                print(f"Detected dumping state at the following times!")
                if check[-3:] == ["dump", "dump", "dump"] and abs(len(dump) + 1 - len(pump_and_dump) < 2):
                    bidprice = bid_price[-1]
                    print(f"bid_price: {bidprice}")
                    dump.append(bidprice)
                    print(f"dump : {dump}")
                    print(f"pump and dump: {pump_and_dump}")
                    s += bidprice
                    print(f"s: {s}")
            if detect == "pump and dump":
                check.append("pump and dump")
                print(f"Detected pumping and dumping state at the following times!")
                if check[-3:] == ["pump and dump", "pump and dump", "pump and dump"] and abs(
                        len(pump_and_dump) + 1 - len(dump)) < 2:
                    askprice = ask_price[-1]
                    print(f"ask_price: {askprice}")
                    pump_and_dump.append(askprice)
                    print(f"dump : {dump}")
                    print(f"pump and dump: {pump_and_dump}")
                    s -= askprice
                    print(f"s: {s}")
            l+=1
        if s > 800:
            index.append(s-bidprice)
        elif s <-800:
            index.append(s+askprice)
        else: index.append(s)
    for n in range(0,30):
        print(f"Ngay {n+1}/09/2020: {index[n]}")
    print(index)
    #
    # print(pump_and_dump)
    # plt.plot(df[0:8000]['ask_price'])
    # plt.show()

    # print(MD.detect_bump_and_dump(232,432))
    # print(tabulate(df[-7297:-3000], tablefmt='pipe', headers='keys'))
    # print(tabulate(df[200:555], tablefmt='pipe', headers='keys'))
    # print(tabulate(df[555:755], tablefmt='pipe', headers='keys'))