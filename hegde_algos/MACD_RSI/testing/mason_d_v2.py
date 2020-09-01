import pandas as pd
import backtrader as bt 
import yfinance as y 


#data_30m = y.download(tickers = 'TWTR', period = '30d', interval = '30m')
#data_30m.to_csv('TWTR_30d.csv')


#***********************************************************************
#	V2 attempts to incorperate multiple secuirties to trade this straegy
# 	on also properly allocate and rebalance the portfolio
#***********************************************************************

data00 = pd.read_csv('TWTR_30m.csv', index_col = 0, parse_dates = True)
data00.drop(columns = ['Adj Close'])
data01 = pd.read_csv('SQ_30m.csv', index_col = 0, parse_dates = True)
data01.drop(columns = ['Adj Close'])
data02 = pd.read_csv('FB_30m.csv', index_col = 0, parse_dates = True)
data02.drop(columns = ['Adj Close'])
data03 = pd.read_csv('TSLA_30m.csv', index_col = 0, parse_dates = True)
data03.drop(columns = ['Adj Close'])
data04 = pd.read_csv('AMZN_30m.csv', index_col = 0, parse_dates = True)
data04.drop(columns = ['Adj Close'])


def get_share_size(account_val, risk, buy_price, stop_price):
	amount = account_val*risk
	total = amount/(buy_price - stop_price)
	return total/2

class macd_rsi_ma_swtich(bt.Strategy):

	def __init__(self):

		self.inds = dict()
		for i, d in enumerate(self.datas):
			self.inds[d] = dict()
			self.inds[d]['movav'] = bt.indicators.SimpleMovingAverage(d.close, period = 9)
			self.inds[d]['rsi'] = bt.indicators.RSI_SMA(d.close,plot = False)
			self.inds[d]['mac'] = bt.indicators.MACD(d.close, plot = False)
			self.inds[d]['macd'] = self.inds[d]['mac'].lines.macd
			self.inds[d]['mac_signal'] = self.inds[d]['mac'].lines.signal
			self.inds[d]['macd_cross'] = bt.indicators.CrossOver(self.inds[d]['macd'], self.inds[d]['mac_signal'], plot=False)
			self.inds[d]['rsi_entry'] = False
			self.inds[d]['macd_entry'] = False
			self.inds[d]['stop_price'] = 0
			self.inds[d]['enter_size'] = 0
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
				if self.inds[d]['rsi'][0] <= 30:
					self.inds[d]['rsi_entry'] = True
				if self.inds[d]['rsi_entry'] == True:
					if self.inds[d]['macd_cross'][0] == 1.0:
						self.inds[d]['macd_entry'] = True
				if self.inds[d]['rsi_entry'] == True and self.inds[d]['macd_entry'] == True and d.close[0] >= self.inds[d]['movav']:
					#self.inds[d]['stop_price'] = d.close[0] * (1-0.02)
					#self.inds[d]['enter_size'] = get_share_size(self.broker.getvalue(), 0.02, d.close[0], self.inds[d]['stop_price'])
					self.order = self.buy(data = d, size = 10, exectype = bt.Order.StopTrail, trailpercent= 0.02)
					self.inds[d]['enter_price'] = d.close[0]
					self.inds[d]['rsi_entry'] = False
					self.inds[d]['macd_entry'] = False
			else:
				#if self.inds[d]['stop_price'] >= self.close_price[0]:
				#	self.close(size = self.inds[d]['enter_price'])
			#		print('STOPPED OUT RSI,MACDENTRY:', self.rsi[0], self.inds[d]['macd_entry'],self.inds[d]['enter_size'])
				if self.inds[d]['macd_cross'] == -1.0:
					self.close(data = d, size = 10) 


cerebro = bt.Cerebro()
cerebro.broker.setcash(1000000.00)
cerebro.broker.setcommission(commission = 0.0)
data0 = bt.feeds.PandasData(dataname = data00, name ='TWTR')
data1 = bt.feeds.PandasData(dataname = data01, name = 'SQ')
data2 = bt.feeds.PandasData(dataname = data02, name ='FB')
data3 = bt.feeds.PandasData(dataname = data03, name = 'TSLA')
data4 = bt.feeds.PandasData(dataname = data04, name ='AMZN')
#data5 = bt.feeds.PandasData(dataname = data05, name ='TWTR_30d')

#data1.plotinfo.plotmaster = data0
cerebro.adddata(data0)
cerebro.adddata(data1)
cerebro.adddata(data2)
cerebro.adddata(data3)
cerebro.adddata(data4)
#cerebro.adddata(data5)
cerebro.addstrategy(macd_rsi_ma_swtich)
cerebro.run()
cerebro.plot(style = 'line')