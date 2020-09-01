import os, sys, argparse
import pandas as pd 
import backtrader as bt 
import yfinance as y
import math
import numpy as np
import backtrader.indicator as btind
from backtrader.feeds import PandasData 
from VBE_calculations import *


#data_30m = y.download(tickers= 'T', period = "60d", interval="60m")
#data_30m.to_csv('T_60m.csv')
data_prices = pd.read_csv('hist_data\\large_cap\\AAPL_60m.csv', index_col=0, parse_dates=True)

#VBE_upper(21,data_prices, data_prices['Close'].values)
#VBE_lower(21,data_prices,data_prices['Close'].values)
data_prices.drop(columns = ['Adj Close'])
#amd_prices['Date'] = pd.to_datetime(amd_prices['Date'],format='%Y-%m-%d %H:%M:%S')  

#def get_slope(y1, y2, x):
#	slope = (y2 - y1)/ (x-0)
#	return slope

def get_share_size(account_val, risk, buy_price, stop_price):
	amount = account_val*risk
	total = amount/(buy_price - stop_price)
	return total/2

def get_reward(stop_price, buy_price):
	return (stop_price - buy_price) * 1.1


class vbe_indicator_wrapper(bt.Indicator):
	lines = ('upperband','lowerband',)
	params = (('period', 21),)

	def __init__(self):
		#self.addminperiod(self.p.period)
		self.pc = []
		self.mu = []
		self.sd = []
		self.raw_upper = []
		self.raw_lower = []
		self.upper = []
		self.lower = []


	def next(self):
		d = self.data.get(size = 21)
		self.pc.append((percent_change(d)))
		if len(self.pc) >= 21:
			self.mu.append(get_mu(21,self.pc))
			self.sd.append(std_rolling(21,self.pc))
		if len(self.mu) >= 21:
			self.raw_upper.append(raw_VBE_upper(self.pc,self.sd,d,self.mu))
			self.raw_lower.append(raw_VBE_lower(self.pc,self.sd,d,self.mu))
		if len(self.raw_upper) >= 63:
			self.upper.append((lag(wma(21, self.raw_upper), self.raw_upper))[-1])
			self.lower.append((lag(wma(21,self.raw_lower), self.raw_lower))[-1])
			self.upperband[0] = self.upper[-1]
			self.lowerband[0] = self.lower[-1]
			


class vbeStrategy(bt.Strategy):

	def __init__(self):
		self.cclose = self.datas[0].close
		self.clow = self.datas[0].low
		self.vbe_u = vbe_indicator_wrapper(self.data.close).upperband
		self.vbe_l =  vbe_indicator_wrapper(self.data.close).lowerband
		self.data_live = False
		self.stop_price = 0
		#self.arcsin = [0,0,0,0]
		self.crossover = bt.ind.CrossUp(self.clow, self.vbe_l)
		self.crossfromabove = bt.ind.CrossDown(self.cclose, self.vbe_u )
		self.sineoutl = 0
		self.sineoutu = 0 
		self.enter_size = 1
		self.target = 0
		#self.graphupper = bt.indicators.SimpleMovingAverage(self.vbe_u, period=1)
		#self.graphlower = bt.indicators.SimpleMovingAverage(self.vbe_l, period=1)
		self.order = None

	def logdata(self):
		txt = []
		txt.append('{}'.format(len(self)))
		txt.append('{}'.format(self.data.datetime.datetime(0).isoformat()))
		txt.append('{:.2f}'.format(self.data.open[0]))
		txt.append('{:.2f}'.format(self.data.high[0]))
		txt.append('{:.2f}'.format(self.data.low[0]))
		txt.append('{:.2f}'.format(self.data.close[0]))
		print(','.join(txt))

	def notify_data(self,data,status,*args, **kwargs):
		print('*' * 5, 'DATA NOTIFY', data._getstatusname(status), *args)
		if status == data.LIVE:
			self.data_live = True 

	def notify_order(self, order):
		if order.status == order.Completed:
			buysell = 'Buy' if order.isbuy() else 'Sell'
			txt = '{} {}@{}'.format(buysell, order.executed.size, order.executed.price)
			print(txt)

	def next(self):
		self.logdata()
		if not self.data_live:
			pass
			#return
		self.sineoutu = math.sin(self.vbe_u[0])
		#self.arcsin.append(np.arcsin(self.sineoutu))
		self.sineoutl = math.sin(self.vbe_l[0])
		if not self.position:	
			if self.crossover and self.sineoutl >= .65:
				self.stop_price = self.cclose[0] * (1-0.02)
				self.target = self.cclose[0] * (1+0.10)
				self.enter_size = get_share_size(self.broker.getvalue(), 0.02, self.cclose[0], self.stop_price)
				self.order = self.buy(size = self.enter_size)
				self.enter_price = self.cclose[0]
				#print('BOUGHT AT: ', self.cclose[0], ', SIZE: ', self.enter_size)
		else:
			if self.crossover and self.sineoutl <= 0.65:
				self.buy(size = self.enter_size)
				#print('bought')
			if self.crossfromabove and self.sineoutu > 0.8:
				self.close(size = self.enter_size)
				#print('Sold')
			elif self.crossfromabove and self.sineoutu <= 0.65:
				return
			elif self.cclose[0] >= self.target:
				self.close(size = self.enter_size)
				#print('Sold')
			elif self.cclose[0] < self.stop_price:
				self.close(size = self.enter_size)
				#print('Sold')



class newPandas(PandasData):
	lines = ('upperband','lowerband',)
	params = (('upperband', 6), ('lowerband', 7),)


def run(args = None):
	cerebro = bt.Cerebro(stdstats = False)
	ibstore = bt.stores.IBStore(host = '127.0.0.1', port = '7497', clientId = 35)
	ibdata = ibstore.getdata(dataname = 'AAPL-STK-SMART-USD' , timeframe = bt.TimeFrame.Ticks)
	cerebro.resampledata(ibdata, timeframe = bt.TimeFrame.Minutes, compression = 60)
	cerebro.broker = ibstore.getbroker()
	cerebro.addstrategy(vbeStrategy)
	cerebro.run()




#Broker and test data from backtesting
cerebro = bt.Cerebro(cheat_on_open = True)
cerebro.broker.setcash(1000000.0)
cerebro.broker.setcommission(commission = 0.0)
#cerebro.addsizer(bt.sizers.FixedSize, stake=10)
#data = bt.feeds.PandasData(dataname=amd_prices)
'''
data = newPandas(dataname=data_prices,
                     #dtformat=('%Y-%m-%d %H:%M:%S'),
                     #timeframe=bt.TimeFrame.Minutes,
                     #tmformat=('%H:%M:%S'),
                     datetime=-1,
                     open=1,
                     high=2,
                     low=3,
                     close=4,
                     volume=5,
                     upperband=6,
                     lowerband=7,
                     #openinterest=-1
                     #fromdate=date(2017,1,1),
                     #todate=date(2017,1,10)
                    )
'''
data = bt.feeds.PandasData(dataname=data_prices)
cerebro.adddata(data)
cerebro.addstrategy(vbeStrategy)
cerebro.run()
cerebro.plot(style='line')