import backtrader as bt
import pandas as pd
import numpy as np
from rework_backtrader.simulation import SimulationEngine
import math
import matplotlib.pyplot as plt
from tabulate import tabulate
import get_live_data
import time


class ManipulationDetection():
    def __init__(self, df, last_matched_price, last_matched_vol, vol_buy_cancelled):
        self.params = dict(
        threshold1 = 0.5,
        threshold2 =  1.5,
        threshold3 = 2,
    )
        self.df = df
        self.last_matched_price = last_matched_price
        self.last_matched_vol = last_matched_vol
        self.vol_buy_cancelled = vol_buy_cancelled

    # get selling price and selling volume which have been matched for 5 minutes
    def getPsellVsellMatched(self):
        price_sell_matched = []
        vol_sell_matched =[]
        for i in range(1,len(self.last_matched_price)):
            if self.last_matched_price[i] != self.last_matched_price[i-1]:
                ask_price = [df[i-1]['ask_price_1'], df[i-1]['ask_price_2'],
                             df[i-1]['ask_price_3'],
                             df[i-1]['ask_price_4'], df[i-1]['ask_price_5'], df[i-1]['ask_price_6'],
                             df[i-1]['ask_price_7'],
                             df[i-1]['ask_price_8'], df[i-1]['ask_price_9'], df[i-1]['ask_price_10']]
                if (self.last_matched_price[i] in ask_price):
                    price_sell_matched.append(self.last_matched_price[i])
                    vol_sell_matched.append(self.last_matched_vol[i])
        return price_sell_matched, vol_sell_matched

    # get buying price and buying volume which have been matched for 5 minutes
    def getPbidVbidmatched(self):
        price_bid_matched = []
        vol_bid_matched =[]
        for i in range(1,len(self.last_matched_price)):
            if self.last_matched_price[i] != self.last_matched_price[i-1]:
                bid_price = [df[i - 1]['bid_price_1'], df[i - 1]['bid_price_2'],
                             df[i - 1]['bid_price_3'],
                             df[i - 1]['bid_price_4'], df[i - 1]['bid_price_5'], df[i - 1]['bid_price_6'],
                             df[i - 1]['bid_price_7'],
                             df[i - 1]['bid_price_8'], df[i - 1]['bid_price_9'], df[i - 1]['bid_price_10']]
                if (self.last_matched_price[i] in bid_price):
                    price_bid_matched.append(self.last_matched_price[i])
                    vol_bid_matched.append(self.last_matched_vol[i])
        return price_bid_matched, vol_bid_matched

    #Check pump and dump
    def detect_pump_and_dump(self):
        check = 0
        vol_buy_cancelled_at_t = self.vol_buy_cancelled[-2]
        vol_buy_matched = MD.getPbidVbidmatched[0:len(df)-1][1]
        if len(vol_buy_matched) >0:
            mean_vol_buy_matched_t = np.mean(vol_buy_matched)
            if vol_buy_cancelled_at_t > mean_vol_buy_matched_t * self.params["threshold1"]:
                if len(MD.getPsellVsellMatched[0:len(df)-1]) > 0:
                    price_sell_max_matched_t = max(MD.getPsellVsellMatched[0:len(df)-1][0])
                    price_sell_min_matched_t_add_1 = min(MD.getPsellVsellMatched[0:len(df)][0])
                    # print(f"Price_sell_max_matched_t: {price_sell_max_matched_t}")
                    # print(f"Price_sell_min_matched_t + 1: {price_sell_min_matched_t_add_1}")
                    if price_sell_max_matched_t-price_sell_min_matched_t_add_1 > self.params["threshold2"]:
                        print("Detected dumping state!")
                        check = 1
                        price_bid_max_matched_t_minus_1 = max(MD.getPbidVbidmatched[0: len(df)-2][0])
                        price_bid_min_matched_t_minus_4 = min(MD.getPbidVbidmatched[0: len(df)-5][0])
                        if price_bid_max_matched_t_minus_1 - price_bid_min_matched_t_minus_4 > self.params["threshold3"]:
                            print("Detected pumping state!")
                            check =2
        return check


    # Check spoofing
    def spoofing(self):
        pass



if __name__ == '__main__':
    # df = pd.read_csv('/home/thanhnhan/Desktop/HFT_Strategy/HFT/VN30F1M.csv', index_col=0, parse_dates=['Date'])
    data = []
    connector = get_live_data.HFTExternalConnector("VN30F1M", data)
    df = []
    last_matched_price = []
    last_matched_vol = []
    vol_buy_cancelled = []
    while True:
        snapshot = connector.get_orderbook_snapshot()
        if snapshot != None:
            if len(df)==0 or df[-1] != snapshot:
                df.append(snapshot)
                last_matched_price.append(snapshot['last_matched_price'])
                last_matched_vol.append(snapshot['last_matched_vol'])
                vol_buy_cancelled.append(snapshot['cancelled_bid'])
                print(snapshot['Date'])
        dumping = []
        pumping = []
        if len(df) > 200:
            df = df[-200:]
            MD = ManipulationDetection(df, last_matched_price, last_matched_vol, vol_buy_cancelled)
            if MD.detect_pump_and_dump() ==1:
                print("Detected dumping state!")
                dumping.append(df[-1]['Date'])
            if MD.detect_pump_and_dump() ==2:
                print("Detected pumping and dumping state!")
            if MD.detect_pump_and_dump() ==0:
                print("Do not appear pump and dump state yet!")













    # i=200
    # pump_and_dump = []
    # while i <8000:
    #     detect = MD.detect_pump_and_dump(i-200, i)
    #     if detect ==1:
    #         print(f"Detected pump-and-dump state! {i}")
    #         pump_and_dump.append(i)
    #     i+=1
    #
    # print(pump_and_dump)
    # plt.plot(df[0:8000]['ask_price'])
    # plt.show()

    # print(MD.detect_bump_and_dump(232,432))
    # print(tabulate(df[0:200], tablefmt='pipe', headers='keys'))
    # print(tabulate(df[200:555], tablefmt='pipe', headers='keys'))
    # print(tabulate(df[555:755], tablefmt='pipe', headers='keys'))