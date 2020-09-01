import os, sys, argparse
import pandas as pd 
import backtrader as bt 
import yfinance as y
import math
from backtrader.feeds import PandasData 
from VBE_calculations import *


data_prices = pd.read_csv('hist_data\\AMD_data.csv', index_col=0, parse_dates=True)

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
		self.copen = self.datas[0].open
		self.vbe_u = self.datas[0].upperband
		self.vbe_l = self.datas[0].lowerband
		self.stop_price = 0
		self.n = 0
		self.arcsin = [0,0]
		self.crossover = bt.ind.CrossUp(self.vbe_l, self.cclose)
		self.crossfromabove = bt.ind.CrossUp(self.vbe_u, self.cclose )
		self.sineoutl = 0
		self.sineoutu = 0 
		self.enter_size = 0
		self.graphupper = bt.indicators.SimpleMovingAverage(self.datas[0].upperband, period=1)
		self.graphlower = bt.indicators.SimpleMovingAverage(self.datas[0].lowerband, period=1)
		self.order = None

	def next(self):
		#checking on our order status
		#checking if we are in the market
		if self.crossfromabove:
			self.sineoutu = math.sin(self.vbe_u[0])
			self.arcsin.append(np.arcsin(self.sineoutu))
			print('sine of upperband:', self.sineoutu, ' , Arcsin: ', self.arcsin[-1])
		if self.crossover:
			self.n = self.n + 1
			self.sineoutl = math.sin(self.vbe_l[0])
			print('sine of lowerband:', self.n , ' ', self.sineoutl)

		#Adding to a position
		if self.position and self.crossover and self.sineoutl <= 0.5:
			self.buy(size = self.enter_size/2)
			print("reentered")
		if not self.position:
			if self.crossover and self.sineoutl <= 0.0:
				self.stop_price = self.cclose[0] * (1-0.05)
				self.enter_size = get_share_size(self.broker.getvalue(), 0.05, self.cclose[0], self.stop_price)
				self.order = self.buy(size = self.enter_size)
				print('BOUGHT AT: ', self.cclose[0], ', SIZE: ', self.enter_size)
		else:
			#if self.cclose[0] >= self.vbe_u[0] and self.sineoutl >= 0.01:
			if self.crossfromabove and self.arcsin[-1] >= 0.75: 
				 self.close(size = self.enter_size)





class newPandas(PandasData):
	lines = ('upperband','lowerband',)
	params = (('upperband', 6), ('lowerband', 7),)



cerebro = bt.Cerebro(cheat_on_open = True)
cerebro.broker.setcash(10000.0)
cerebro.broker.setcommission(commission = 0.0)
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
cerebro.run()
cerebro.plot(style='line')