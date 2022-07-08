import yfinance as yf
import pandas as pd
import pandas_ta as ta
##import ta-lib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

df = yf.download('BTC-USD', start='2019-01-01', interval='1d')

def EMA_Backtesting(values, n):
    """
    Return exponential moving average of `values`, at
    each step taking into account `n` previous values.
    """
    close = pd.Series(values)
##    return talib.EMA(close, timeperiod=n)
    return close.ewm(span=n, adjust=False).mean()

class EmaCrossStrategy(Strategy):
    
    # Define the two EMA lags as *class variables*
    # for later optimization
    n1 = 8
    n2 = 34
    
    def init(self):
        # Precompute two moving averages
        self.ema1 = self.I(EMA_Backtesting, self.data.Close, self.n1)
        self.ema2 = self.I(EMA_Backtesting, self.data.Close, self.n2)
    
    def next(self):       
        # If ema1 crosses above ema2, buy the asset
        if crossover(self.ema1, self.ema2):
            self.position.close()
            self.buy()

        # Else, if ema1 crosses below ema2, sell it
        elif crossover(self.ema2, self.ema1):
            self.position.close()
            self.sell()



class EmaCross(Strategy):
    n1 = 8
    n2 = 34

    def init(self):
        close = self.data.Close
        self.ema1 = self.I(EMA, close, self.n1)
        self.ema2 = self.I(EMA, close, self.n2)

    def next(self):
        if crossover(self.ema1, self.ema2):
            self.buy()
        elif crossover(self.ema2, self.ema1):
            self.sell()


bt = Backtest(df, EmaCrossStrategy,
              cash=100000, commission=.002,
              exclusive_orders=True)

output = bt.run()
print(output)
bt.plot()


