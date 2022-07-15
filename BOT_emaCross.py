import yfinance as yf
import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from datetime import datetime
from backtesting.test import SMA
import time

filename = 'trades.txt'
file = open(filename,'a+')
file.write(str(datetime.now()))
file.write("/n")
file.close

df = yf.download('BTC-USD', start='2019-01-01', interval='1d')

def EMA_Backtesting(values, n):
    """
    Return exponential moving average of `values`, at
    each step taking into account `n` previous values.
    """
    close = pd.Series(values)
    return close.ewm(span=n, adjust=False).mean()

# def SMA(data, n):
#     sma = data.rolling(window = n).mean()
#     return pd.DataFrame(sma)    

class EmaCrossStrategy(Strategy):
    
    # Define the two EMA lags as *class variables*
    # for later optimization
    n1 = 8
    n2 = 34
    n3 = 50
    n4 = 200
    
    def init(self):

        # Precompute two moving averages
        self.ema8 = self.I(EMA_Backtesting, self.data.Close, self.n1)
        self.ema34 = self.I(EMA_Backtesting, self.data.Close, self.n2)
        self.sma50 = self.I(SMA, self.data.Close, self.n3)
        self.sma200 = self.I(SMA, self.data.Close, self.n4)
        # self.ma50 = self.I(SMA, self.data.Close, 50)
    
    def next(self):       
        # current price
        self.price = self.data.Close[-1]

        self.currentTime = self.data.index[-1] 

        
        # if self.closed_trades: # If we have trades
        #     self.lastTradeExitTime = self.closed_trades[-1].exit_time
        #     if self.lastTradeExitTime != self.oldLastTradeExitTime:
        #         print("lastTradeExitTime:", self.lastTradeExitTime)
        #         self.oldLastTradeExitTime = self.lastTradeExitTime
        # else: # If there hasn't been any trades yet
        #     self.lastTradeExitTime = self.data.index[0]
        #     self.oldLastTradeExitTime = self.data.index[0]

        
        # If ema1 crosses above ema2, buy the asset
        # Long entry
        if (not self.position and 
            self.sma50 > self.sma200 and
            crossover(self.ema8, self.ema34)): # and (self.price > self.ema1):
            #  Buy
            # print("self.currentTime="+str(self.currentTime)+ " self.lastTradeExitTime="+str(self.lastTradeExitTime))
            # não quero entrar numa trade no mesmo dia em que saí de outra trade
            # if (self.currentTime > self.lastTradeExitTime + timedelta(days=1) ):
                # self.position.close()
                self.buy()         
        
        # Else, if ema1 crosses below ema2, sell it
        # Long exit
        # elif (self.position and 
        elif crossover(self.ema34, self.ema8):
            # Close any existing long trades, and sell the asset
            self.position.close()
            # self.sell()
            

bt = Backtest(df, EmaCrossStrategy,
              cash=100000, commission=.002,
              exclusive_orders=True)

output = bt.run()

output.to_csv(filename)
print(output)

# If file is not empty then append '\n'
file = open(filename,'a')
file.write("\n")
file.close()

d = bt._results._trades
df = pd.DataFrame(d)
print(df.to_string())
df.to_csv(filename, mode='a')

bt.plot()


