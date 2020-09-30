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
        print(self)
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
    df = pd.read_csv('/home/thanhnhan/Desktop/pthnhan_quant/HFT_strategies/HFT/VN30F1M.csv', index_col=0, parse_dates=['Date'])
    MD = ManipulationDetection(df)

    i=200
    s = 0
    dump = []
    pump_and_dump = []
    while i <4650:
        bid_price = df[i:i+1]["bid_price"]
        print(f"bid_price: {bid_price}")
        ask_price = df[i:i+1]["ask_price"]
        print(f"ask_price: {ask_price}")
        detect = MD.detect_pump_and_dump(i - 200, i)
        if detect == "dump":
            dump.append(i)
            print(f"Detected dumping state at the following times!")
        if detect == "pump and dump":
            pump_and_dump.append(i)
            print(f"Detected pumping and dumping state at the following times!")
        if len(dump) > 0:
            pump_and_dump = []
            if len(dump) == 3:
                s += bid_price
                print(f"s: {s}")
        if len(pump_and_dump) > 0:
            dump = []
            if len(pump_and_dump) == 3:
                s -= ask_price
                print(f"s: {s}")
        i+=1
    #
    # print(pump_and_dump)
    # plt.plot(df[0:8000]['ask_price'])
    # plt.show()

    # print(MD.detect_bump_and_dump(232,432))
    # print(tabulate(df[4650:4651], tablefmt='pipe', headers='keys'))
    # print(tabulate(df[200:555], tablefmt='pipe', headers='keys'))
    # print(tabulate(df[555:755], tablefmt='pipe', headers='keys'))