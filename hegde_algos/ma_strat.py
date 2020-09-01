import pandas as pd
import backtrader as bt 
import yfinance as y 


data_1d = y.download(tickers = 'AAPL', period = '200d', interval = '1d')
data_1d.to_csv('AAPL_1d.csv')


#***********************************************************************
#	V2 attempts to incorperate multiple secuirties to trade this straegy
# 	on also properly allocate and rebalance the portfolio
#***********************************************************************

data00 = pd.read_csv('AAPL_1d.csv', index_col = 0, parse_dates = True)
data00.drop(columns = ['Adj Close'])

#def get_share_size(account_val, risk, buy_price, stop_price):
	#amount = account_val*risk
	#total = amount/(buy_price - stop_price)
	#return total/2

class movav_50d_200d_swtich(bt.Strategy):

	def __init__(self):

		self.inds = dict()
		for i, d in enumerate(self.datas):
			self.inds[d] = dict()
			self.inds[d]['movav50'] = bt.indicators.SimpleMovingAverage(d.close, period = 50)
			self.inds[d]['movav200'] = bt.indicators.SimpleMovingAverage(d.close, period = 200)
			#self.inds[d]['rsi'] = bt.indicators.RSI_SMA(d.close,plot = False)
			#self.inds[d]['mac'] = bt.indicators.MACD(d.close, plot = False)
			#self.inds[d]['macd'] = self.inds[d]['mac'].lines.macd
			#self.inds[d]['mac_signal'] = self.inds[d]['mac'].lines.signal
			self.inds[d]['movav_cross'] = bt.indicators.CrossOver(self.inds[d]['movav50'], self.inds[d]['movav200'], plot=False) #when movav50 crosses movav200 upwards = +1, 50 crosses 200 downwards = -1
			self.inds[d]['movav50_entry'] = False
			self.inds[d]['movav200_entry'] = False
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
				if self.inds[d]['movav_cross'][0] == 1.0:
					self.inds[d]['stop_price'] = d.close[0] * (1-0.02)
					self.inds[d]['enter_size'] = get_share_size(self.broker.getvalue(), 0.02, d.close[0], self.inds[d]['stop_price'])
					self.order = self.buy(data = d, size = self.inds[d]['enter_size'], exectype = bt.Order.StopTrail, trailpercent= 0.02)
					self.inds[d]['enter_price'] = d.close[0]
					self.inds[d]['movav50_entry'] = False
					self.inds[d]['movav200_entry'] = False
			else:
				#if self.inds[d]['stop_price'] >= self.close_price[0]:
				#	self.close(size = self.inds[d]['enter_price'])
			#		print('STOPPED OUT RSI,MACDENTRY:', self.rsi[0], self.inds[d]['macd_entry'],self.inds[d]['enter_size'])
				if self.inds[d]['movav_cross'] == -1.0:
					self.close(data = d, size = 10) 


cerebro = bt.Cerebro()
cerebro.broker.setcash(1000000.00)
cerebro.broker.setcommission(commission = 0.0)
data0 = bt.feeds.PandasData(dataname = data00, name ='AAPL')
#data1.plotinfo.plotmaster = data0
cerebro.adddata(data0)
cerebro.addstrategy(movav_50d_200d_swtich)
cerebro.run()
cerebro.plot(style = 'line')