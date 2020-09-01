import os, sys, argparse
import pandas as pd 
import backtrader as bt 
import backtrader.analyzers as btanalyzers
import yfinance as y
import math
from backtrader.feeds import PandasData 
from VBE import *

#data_30m = y.download(tickers= 'T', period = "60d", interval="30m")
#data_30m.to_csv('T_30m.csv')
data_prices = pd.read_csv('hist_data\\large_cap\\AAPL_60m.csv', index_col=0, parse_dates=True)

VBE_upper(21,data_prices, data_prices['Close'].values)
VBE_lower(21,data_prices,data_prices['Close'].values)
data_prices.drop(columns = ['Adj Close'])
#amd_prices['Date'] = pd.to_datetime(amd_prices['Date'],format='%Y-%m-%d %H:%M:%S')  

def get_slope(y1, y2, x):
	slope = (y2 - y1)/ (x-0)
	return slope

def get_share_size(account_val, risk, buy_price, stop_price):
	amount = account_val*risk
	total = amount/(buy_price - stop_price)
	return total/2

def get_reward(stop_price, buy_price):
	return (stop_price - buy_price) * 1.1

class testStrategy(bt.Strategy):
	def __init__(self):
		self.cclose = self.datas[0].close
		self.clow = self.datas[0].low
		self.vbe_u = self.datas[0].upperband
		self.vbe_l = self.datas[0].lowerband
		self.stop_price = 0
		self.n = 0
		self.arcsin = [0,0,0,0]
		self.crossover = bt.ind.CrossUp(self.clow, self.vbe_l)
		self.crossfromabove = bt.ind.CrossDown(self.cclose, self.vbe_u )
		self.sineoutl = 0
		self.sineoutu = 0 
		self.enter_size = 1
		self.target = 0
		self.graphupper = bt.indicators.SimpleMovingAverage(self.datas[0].upperband, period=1)
		self.graphlower = bt.indicators.SimpleMovingAverage(self.datas[0].lowerband, period=1)
		self.order = None


	def next(self):
		#checking on our order status
		#checking if we are in the market
		#We are in a down trend looking for best entry
		"""
		if self.trenddown:
			if self.cclose[0] > self.cclose[-2]:
				print('bought on down trend')
				self.stop_price = self.cclose[0] * (1-0.05)
				self.buy(size = 10)
				self.trenddown = False
		"""
		#Adding to a position
		"""
		if self.position and self.crossover and self.sineoutl <= 0.5:
			self.stop_price = self.cclose[0] * (1-0.05)
			self.buy(size = self.enter_size/2)
			print("reentered")
		"""
		self.sineoutu = math.sin(self.vbe_u[0])
		self.arcsin.append(np.arcsin(self.sineoutu))
		#print('sine of upperband:', self.sineoutu, ' , Arcsin: ', self.arcsin[-1])
		if self.crossover:
			self.n = self.n + 1
			self.sineoutl = math.sin(self.vbe_l[0])
			print('sine of lowerband:', self.n , ' ', self.sineoutl)
		if not self.position:	
			"""
			if self.crossover and self.sineoutl < 1 and self.crossover > 0:
				self.buy(size = self.enter_size)
			elif self.crossover and self.sineoutl < -0.5:
				self.trenddown = True
			"""
			if self.crossover and self.sineoutl >= .65:
				self.stop_price = self.cclose[0] * (1-0.02)
				self.target = self.cclose[0] * (1+0.10)
				self.enter_size = get_share_size(self.broker.getvalue(), 0.02, self.cclose[0], self.stop_price)
				self.order = self.buy(size = self.enter_size)
				self.enter_price = self.cclose[0]
				print('BOUGHT AT: ', self.cclose[0], ', SIZE: ', self.enter_size)
		else:
			#if self.cclose[0] >= self.vbe_u[0] and self.sineoutl >= 0.01:
			if self.crossover and self.sineoutl <= 0.65:
				self.buy(size = self.enter_size)
				print('bought')
			if self.crossfromabove and self.sineoutu > 0.8:
				self.close(size = self.enter_size)
			elif self.crossfromabove and self.sineoutu <= 0.65:
				return
			elif self.cclose[0] >= self.target:
				self.close(size = self.enter_size)
			elif self.cclose[0] < self.stop_price:
				self.close(size = self.enter_size)
			'''
			elif self.crossfromabove and self.arcsin[-1] < 0.5:
				self.close(size = self.enter_size)
			'''
			'''
			if self.crossfromabove and self.arcsin[-1] - self.sineoutu >= 0.2: 
				 self.close(size = 1)
			elif self.crossfromabove and self.arcsin[-1] >= -0.1 and self.arcsin[-1] <= 0.75:
				self.close(size = 1)
			elif self.arcsin[-1] - self.arcsin[-2] < -0.5:
				self.close(size = 1)
			'''



class newPandas(PandasData):
	lines = ('upperband','lowerband',)
	params = (('upperband', 6), ('lowerband', 7),)



cerebro = bt.Cerebro(cheat_on_open = True)
cerebro.broker.setcash(1000000.0)
cerebro.broker.setcommission(commission = 0.00)
#cerebro.addsizer(bt.sizers.FixedSize, stake=10)
#data = bt.feeds.PandasData(dataname=amd_prices)
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
cerebro.adddata(data)
cerebro.addstrategy(testStrategy)
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name = 'mysharpe')
thestrats = cerebro.run()
thestrat = thestrats[0]
print('Sharpe Ratio:' , thestrat.analyzers.mysharpe.get_analysis()) 
cerebro.plot(style = 'line')