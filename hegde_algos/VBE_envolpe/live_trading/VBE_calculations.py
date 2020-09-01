import yfinance as y 
import statistics 
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
from matplotlib import style
from decimal import *
plt.style.use('fivethirtyeight')

"""
ticker = 'MCD'
#downloading the ticker data

data_30m = y.download(tickers=ticker, period = "30d", interval="30m")
data_daily = y.download(ticker, '2019-04-05')
data_1m = y.download(tickers=ticker, period = "5d", interval = "1m")
#this is for the graph to adjust for the weird gaps when there is no data
s = pd.date_range('2020-06-29', '2020-07-07', freq = 'M').to_series()

#Adjusting data to remove weekends
data_daily[data_daily.index.dayofweek<5]
data_30m[data_30m.index.dayofweek<5]
data_daily_adj_close = data_daily['Adj Close']
data_30m_adj_close = data_30m['Adj Close']
data_1m_adj_close = data_1m['Adj Close']
"""
#####################################################

					#GETTERS#

####################################################

def get_coef(corcof):
	return corcof[0][1]

####################################################

				#METHODS

####################################################

def wma(p,data):
	d = p*(p/2+.5)
	weights = np.zeros(p)
	for i in range(p):
		weights[i] = ((i+1)/d)
	a = np.zeros(p)
	out = np.zeros(len(data))
	n = len(weights)

	front_half = weights[:n//2]
	rev = np.flipud(front_half)
	if len(weights)%2 != 0:
		center = (weights[(n//2)])
		temp_front = np.append(front_half, center)
	else:
		temp_front = [0.5]
		rev = [0.5]

	weights = np.concatenate((temp_front,rev))
	for i in range(len(data)):
		if i < p-1:
			out[i] = np.nan
		else:
			for m in range(p):
				a[(p-1)-m] = data[i-m]
			out[i] = (np.sum((a*weights))/(weights.sum()))
	return out	

####################################################

def std_rolling(p,data):
	std = np.zeros(len(data))
	temp = np.zeros(p)
	for i in range(len(data)):
		if i < p-1:
			std[i] = np.nan
		else:
			for j in range(p):
				temp[(p-1)-j] = data[i-j]
			std_f = statistics.pstdev(temp)
	return std_f

####################################################

def get_mu(p, percent_change):
	mu = np.zeros(len(percent_change))
	temp = np.zeros(p)
	for i in range(len(percent_change)):
		if i < p-1:
			mu[i] = np.nan
		else:
			for j in range(p):
				temp[(p-1)-j] = percent_change[i-j]
			mu_f = statistics.fmean(temp)
	return mu_f

####################################################

def raw_VBE_upper(percent_change_day,sd,data,mu):
	#calculating raw bands data
	upper_raw_band_f = 0.0
	for i in range(len(data)-1):
		std = Decimal(mu[i]) + Decimal((sd[i]*2))
		upper_raw_band = (Decimal(data[i]) * (1 + (std/100)))
		upper_raw_band_f = float(upper_raw_band)
	return upper_raw_band_f

####################################################

def raw_VBE_lower(percent_change_day,sd,data,mu):
	#calculating raw bands data
	lowerband_raw_band_f = 0.0
	for i in range(len(data)-1):
		std = Decimal(mu[i]) - Decimal((sd[i]*2))
		lower_raw_band = Decimal(data[i]) * (1+(std/100))
		lower_raw_band_f = float(lower_raw_band)
	return lower_raw_band_f

####################################################

def percent_change(data):
	temp_f = 0.0
	for i in range(len(data)):
		temp = (-1*(Decimal(data[i-1]) - Decimal(data[i]))/Decimal(abs(data[i]))) * 100
		temp.normalize()
		temp_f = float(temp)
	return temp_f

####################################################

def percent_change_list(data):
	percent_change_day = []
	for i in range(len(data)):
		temp = (-1*(Decimal(data[i-1]) - Decimal(data[i]))/Decimal(abs(data[i]))) * 100
		temp.normalize()
		temp_f = float(temp)
		percent_change_day.append(temp_f)
	return percent_change_day

####################################################

def lag(data,raw):
	d_list = data.tolist()	
	n = 5
	del d_list[:n]

	wma21 = wma(21,raw)
	wma17 = wma(17,raw)
	wma13 = wma(13,raw)
	wma9 = wma(9,raw)
	wma5 = wma(5,raw)
	wma2 = wma(2,raw)
	#print(wma21)
	wma21_pc = percent_change_list(wma21)
	wma17_pc = percent_change_list(wma17)
	wma13_pc = percent_change_list(wma13)
	wma9_pc = percent_change_list(wma9)
	wma5_pc = percent_change_list(wma5)
	wma2_pc = percent_change_list(wma2)
	#print(wma2_pc)
	wma21_pc = wma21_pc[-63:]
	wma17_pc = wma17_pc[-63:]
	
	corrc17 = get_coef(np.corrcoef(wma21_pc,wma17_pc)) 
	wma13_pc = wma13_pc[-63:]
	corrc13 = get_coef(np.corrcoef(wma21_pc,wma13_pc))
	wma9_pc = wma9_pc[-63:]
	corrc9 = get_coef(np.corrcoef(wma21_pc,wma9_pc))
	wma5_pc = wma5_pc[-63:]
	corrc5 = get_coef(np.corrcoef(wma21_pc,wma5_pc))
	wma2_pc = wma2_pc[-63:]
	corrc2 = get_coef(np.corrcoef(wma21_pc,wma2_pc))

	last_price = wma21[-1]
	print(wma21)
	lag17_price  = Decimal(Decimal(last_price) * Decimal(1 + ((Decimal(corrc17) * Decimal(wma17_pc[-1]))/100)))
	lag13_price  = Decimal((lag17_price * Decimal((1 + ((Decimal(corrc13) * Decimal(wma13_pc[-1])/100))))))
	lag9_price  = Decimal((lag13_price * Decimal((1 + ((Decimal(corrc9) * Decimal(wma9_pc[-1]))/100)))))
	lag5_price  = Decimal((lag9_price * Decimal((1 + ((Decimal(corrc5) * Decimal(wma5_pc[-1]))/100)))))
	lag2_price  = Decimal((lag5_price * Decimal((1 + ((Decimal(corrc2) * Decimal(wma2_pc[-1]))/100)))))
	lag17_price_f = float(lag17_price)
	lag13_price_f = float(lag13_price)
	lag9_price_f = float(lag9_price)
	lag5_price_f = float(lag5_price)
	lag2_price_f = float(lag2_price)
	d_list.append(lag17_price_f)
	d_list.append(lag13_price_f)
	d_list.append(lag9_price_f)
	d_list.append(lag5_price_f)
	d_list.append(lag2_price_f)
	return d_list

####################################################

				#CHANNEL CALCULATIONS

####################################################

def VBE_upper(period, data_adj_close, mu, sd, pc21):
	#STEP 1 
	#CALCULATING THE STANDARD DIV
	#first get the percent change of every day for teh past 21d
	#pc21 = percent_change(data_adj_close)
	#sd = std_rolling(21,pc21)
	#mu = get_mu(21,pc21)

	#STEP 2
	#Calculating the raw bands
	raw_upper = raw_VBE_upper(pc21,sd,data_adj_close,mu)
	#print(len(raw_upper))
	#STEP 3 /4 
	#SMOOTH USING CWMAs and adjusting for lag
	upper = lag(wma(period, raw_upper), raw_upper)
	#Return the most recent point in the vbe
	return upper

def VBE_lower(period, data_adj_close):
	#STEP 1 
	#CALCULATING THE STANDARD DIV
	#first get the percent change of every day for teh past 21d
	pc21 = percent_change(data_adj_close)
	sd = std_rolling(21,pc21)
	mu = get_mu(21,pc21)

	#STEP 2
	#Calculating the raw bands
	raw_lower = raw_VBE_lower(pc21,sd,data_adj_close,mu)

	#STEP 3 /4 
	#SMOOTH USING CWMAs and adjusting for lag
	lower = lag(wma(period,raw_lower), raw_lower) 
	#Return the most recent point in the vbe
	return lower
