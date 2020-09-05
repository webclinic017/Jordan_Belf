import pandas as pd
import backtrader as bt 
import yfinance as y 
import math

#data_1d = y.download(tickers = 'SQ', period = '5y', interval = '1d')
#data_1d.to_csv('SQ_1d.csv')


data00 = pd.read_csv('AAPL_1d.csv', index_col = 0, parse_dates = True)
data00.drop(columns = ['Adj Close'])
data01 = pd.read_csv('MSFT_1d.csv', index_col = 0, parse_dates = True)
data01.drop(columns = ['Adj Close'])
data02 = pd.read_csv('WMT_1d.csv', index_col = 0, parse_dates = True)
data02.drop(columns = ['Adj Close'])
data03 = pd.read_csv('AMD_1d.csv', index_col = 0, parse_dates = True)
data03.drop(columns = ['Adj Close'])
data04 = pd.read_csv('TSLA_1d.csv', index_col = 0, parse_dates = True)
data04.drop(columns = ['Adj Close'])
data05 = pd.read_csv('PG_1d.csv', index_col = 0, parse_dates = True)
data05.drop(columns = ['Adj Close'])
data06 = pd.read_csv('CRM_1d.csv', index_col = 0, parse_dates = True)
data06.drop(columns = ['Adj Close'])
data07 = pd.read_csv('PYPL_1d.csv', index_col = 0, parse_dates = True)
data07.drop(columns = ['Adj Close'])

class movav_50d_200d_swtich(bt.Strategy):

	def __init__(self):

		self.inds = dict()
		for i, d in enumerate(self.datas):
			self.inds[d] = dict()
			self.inds[d]['movav50'] = bt.indicators.EMA(d.close, period = 44)
			self.inds[d]['movav200'] = bt.indicators.EMA(d.close, period = 203)
			self.inds[d]['movav_cross'] = bt.indicators.CrossOver(self.inds[d]['movav50'], self.inds[d]['movav200'], plot=False) #when movav50 crosses movav200 upwards = +1, 50 crosses 200 downwards = -1	
			self.inds[d]['movav50_entry'] = False
			self.inds[d]['movav200_entry'] = False
			self.inds[d]['enter_price'] = 0

	def notify_order(self, order):
		if order.status == order.Completed:
			buysell = 'Buy' if order.isbuy() else 'Sell'
			txt = '{} {}@{}'.format(buysell, order.executed.size, order.executed.price)
			print(txt)

	def notify_trade(self, trade):
		if not trade.isclosed:
			return
		print('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

	def next(self):
		for i, d in enumerate(self.datas):
			dn = d._name
			pos = self.getposition(d).size
			
			if not pos:
				if self.inds[d]['movav_cross'][0] == 1.0:
					self.inds[d]['movav50_entry'] = True
					self.inds[d]['movav200_entry'] = True
					if self.inds[d]['movav_cross'][0] == 1.0:
						self.order = self.buy(data = d, size = 10, exectype = bt.Order.StopTrail, trailpercent= 0)
						self.inds[d]['enter_price'] = d.close[0]
						self.inds[d]['movav50_entry'] = False
						self.inds[d]['movav200_entry'] = False
				
			
			else:
					if self.inds[d]['movav_cross'] == -1.0:
						self.close(data = d, size = 10)
						 

cerebro = bt.Cerebro()
cerebro.broker.setcash(1000000.00)
cerebro.broker.setcommission(commission = 0.0)
data0 = bt.feeds.PandasData(dataname = data00, name ='AAPL')
data1 = bt.feeds.PandasData(dataname = data01, name ='MSFT')
data2 = bt.feeds.PandasData(dataname = data02, name = 'WMT')
data3 = bt.feeds.PandasData(dataname = data03, name = 'AMD')
data4 = bt.feeds.PandasData(dataname = data04, name ='TSLA')
data5 = bt.feeds.PandasData(dataname = data05, name ='PG')
data6 = bt.feeds.PandasData(dataname = data06, name = 'CRM')
data7 = bt.feeds.PandasData(dataname = data07, name = 'PYPL')

cerebro.adddata(data0)
cerebro.adddata(data1)
cerebro.adddata(data2)
cerebro.adddata(data3)
cerebro.adddata(data4)
cerebro.adddata(data5)
cerebro.adddata(data6)
cerebro.adddata(data7)

cerebro.addstrategy(movav_50d_200d_swtich)
cerebro.run()
#cerebro.plot(style = 'line')
print(cerebro.broker.getvalue())