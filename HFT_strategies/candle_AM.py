import backtrader as bt
import backtrader.analyzers as btanalyzers
import backtrader.strategies as btstrats
import numpy as np
import pandas as pd
from glob import glob
import math
# totalTrades = 0
from datetime import datetime
'''
good setup
15-10,20-20, 20-45, 20-50
'''

class LeadLag(bt.Strategy):
    params = dict(
        entryZ=2,
        exitZ=0.2,
        window=5,
    )
    def __init__(self):
        self.side = 0
        self.LastReturn=[]
        self.Last_Vol=[]
        self.mean_score=0
        self.count = 0
        self.currPos = 0
        self.counttrade = 0
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    def next(self):
        available = list(filter(lambda d: len(d), self.datas))
        rets = np.zeros(len(available))
        high_low = np.zeros(len(available))
        for i, d in enumerate(available):
            if d.high[0]-d.low[0]!=0:
                rets[i]=(d.close[0]-d.close[-1])/d.close[-1]
                high_low[i]=(d.high[0]-d.low[0])*d.volume[0]
        ft_ret=rets[0]
        vol_ret=high_low[0]
        if len(self.LastReturn)<self.p.window:
            self.LastReturn.append(ft_ret)
            self.Last_Vol.append(vol_ret)
        else:
            self.LastReturn=self.LastReturn[1:]
            self.Last_Vol=self.Last_Vol[1:]
            self.Last_Vol.append(vol_ret)
            self.LastReturn.append(ft_ret)
            meanvol=np.mean(self.Last_Vol)
            stdvol=np.std(self.Last_Vol)
            mean=np.mean(self.LastReturn)
            std=np.std(self.LastReturn)
            print(std)
            zscore=(self.Last_Vol[-1]-meanvol)/stdvol
            if self.LastReturn[-1]>mean and self.LastReturn[-3]>0 and self.LastReturn[-2]*2>(4*self.LastReturn[-1]+self.LastReturn[-3])/5:
                self.side=1
                self.order_target_size(target=70)
                self.count += abs(70 - self.currPos)
                self.currPos = 70
                self.counttrade += 1
                print(1,'have signal')
            elif self.LastReturn[-1]<mean and (-self.p.exitZ>zscore>-self.p.entryZ or self.p.exitZ<zscore<self.p.entryZ):
                self.order_target_size(target=0)
                self.side = 0
            elif self.LastReturn[-1]<mean and self.LastReturn[-3]<0 and self.LastReturn[-2]*2<(4*self.LastReturn[-1]+self.LastReturn[-3])/5:
                self.order_target_size(target=-70)
                self.count += abs(-70 - self.currPos)
                self.currPos = -70
                self.counttrade += 1
                self.side = -1
                print(-1,'have signal')

            print(self.datetime.datetime(),self.datas[0].close[0],self.side)
    def stop(self):
        pnl = round(self.broker.getvalue() - 1e9, 2)
        print('Final PnL: {:,}'.format(pnl), pnl / self.count, self.counttrade)
from rework_backtrader.simulation import SimulationEngine
if __name__ == '__main__':
    simulation = SimulationEngine()
    OS_or_IS = "OS"
    simulation.adddata("~/repos/rework_backtrader/data/{}/1h".format(OS_or_IS), names=["VN30F1M"])
    # simulation.setcommission(commission=7500, margin=1, mult=100000)
    simulation.set_cash(cash=1e9)
    simulation.addstrategy(LeadLag)
    # simulation.optstrategy(LeadLag,window=(4,6,8,10,12,15))
    # simulation.optstrategy(LeadLag ,window=range(4,15),entryZ=(1.2, 1.4, 1.6, 1.8, 2.0, 2.2,2.4), exitZ=(0.2, 0.4, 0.6,0.8))
    strats = simulation.run(output="/home/nam/repos/rework_backtrader/Strategies/original_alpha_f1m/output/{}_candle_AMm.csv".format(OS_or_IS))
    # strats = simulation.run_opt("../info/bankleadlagStat2.csv")

