from yahoofinancials import YahooFinancials

ticker = 'AAPL'
yahoo_financials = YahooFinancials(ticker)

########################################################################################################
######FINANCIAL STATEMENT##########

#income = yahoo_financials.get_financial_stmts('annual', 'income')
#cash = yahoo_financials.get_financial_stmts('annual', 'cash')
balance = yahoo_financials.get_financial_stmts('annual', 'balance')
shares = yahoo_financials.get_key_statistics_data()

######REVENUE######################
#R0 is most recent reporting, R4 is oldest reporting

#R0 = income['incomeStatementHistory']['AAPL'][0]['2020-09-26']['totalRevenue']
#R1 = income['incomeStatementHistory']['AAPL'][1]['2019-09-28']['totalRevenue']
#R2 = income['incomeStatementHistory']['AAPL'][2]['2018-09-29']['totalRevenue']
#R3 = income['incomeStatementHistory']['AAPL'][3]['2017-09-30']['totalRevenue']

######EXPENSES####################

#E0 = income['incomeStatementHistory']['AAPL'][0]['2020-09-26']['totalOperatingExpenses']
#E1 = income['incomeStatementHistory']['AAPL'][1]['2019-09-28']['totalOperatingExpenses']
#E2 = income['incomeStatementHistory']['AAPL'][2]['2018-09-29']['totalOperatingExpenses']
#E3 = income['incomeStatementHistory']['AAPL'][3]['2017-09-30']['totalOperatingExpenses']

######EBIT########################

#EBIT0 = income['incomeStatementHistory']['AAPL'][0]['2020-09-26']['ebit']
#EBIT1 = income['incomeStatementHistory']['AAPL'][1]['2019-09-28']['ebit']
#EBIT2 = income['incomeStatementHistory']['AAPL'][2]['2018-09-29']['ebit']
#EBIT3 = income['incomeStatementHistory']['AAPL'][3]['2017-09-30']['ebit']

######TAX EXPENSE#################

#TE0 = income['incomeStatementHistory']['AAPL'][0]['2020-09-26']['incomeTaxExpense']
#TE1 = income['incomeStatementHistory']['AAPL'][1]['2019-09-28']['incomeTaxExpense']
#TE2 = income['incomeStatementHistory']['AAPL'][2]['2018-09-29']['incomeTaxExpense']
#TE3 = income['incomeStatementHistory']['AAPL'][3]['2017-09-30']['incomeTaxExpense']

######TAX RATE####################

#TR0 = (1-((EBIT0 - TE0)/(EBIT0)))
#TR1 = (1-((EBIT1 - TE1)/(EBIT1)))
#TR2 = (1-((EBIT2 - TE2)/(EBIT2)))
#TR3 = (1-((EBIT3 - TE3)/(EBIT3)))

######DEPRECIATION################

#D0 = cash['cashflowStatementHistory']['AAPL'][0]['2020-09-26']['depreciation']
#D1 = cash['cashflowStatementHistory']['AAPL'][1]['2019-09-28']['depreciation']
#D2 = cash['cashflowStatementHistory']['AAPL'][2]['2018-09-29']['depreciation']
#D3 = cash['cashflowStatementHistory']['AAPL'][3]['2017-09-30']['depreciation']

######CAPEX#######################

#C0 = cash['cashflowStatementHistory']['AAPL'][0]['2020-09-26']['capitalExpenditures']
#C1 = cash['cashflowStatementHistory']['AAPL'][1]['2019-09-28']['capitalExpenditures']
#C2 = cash['cashflowStatementHistory']['AAPL'][2]['2018-09-29']['capitalExpenditures']
#C3 = cash['cashflowStatementHistory']['AAPL'][3]['2017-09-30']['capitalExpenditures']

######CURRENT ASSETS##############

#CA0 = balance['balanceSheetHistory']['AAPL'][0]['2020-09-26']['totalCurrentAssets']
#CA1 = balance['balanceSheetHistory']['AAPL'][1]['2019-09-28']['totalCurrentAssets']
#CA2 = balance['balanceSheetHistory']['AAPL'][2]['2018-09-29']['totalCurrentAssets']
#CA3 = balance['balanceSheetHistory']['AAPL'][3]['2017-09-30']['totalCurrentAssets']

######Current LIABLILITES#########

#CL0 = balance['balanceSheetHistory']['AAPL'][0]['2020-09-26']['totalCurrentLiabilities']
#CL1 = balance['balanceSheetHistory']['AAPL'][1]['2019-09-28']['totalCurrentLiabilities']
#CL2 = balance['balanceSheetHistory']['AAPL'][2]['2018-09-29']['totalCurrentLiabilities']
#CL3 = balance['balanceSheetHistory']['AAPL'][3]['2017-09-30']['totalCurrentLiabilities']

######WORKING CAPITAL#############

#WC0 = CA0 - CL0
#WC1 = CA1 - CL1
#WC2 = CA2 - CL2
#WC3 = CA3 - CL3

######DEBT########################

DEBT = (balance['balanceSheetHistory']['AAPL'][0]['2020-09-26']['shortLongTermDebt']) + (balance['balanceSheetHistory']['AAPL'][0]['2020-09-26']['longTermDebt'])

######CASH########################

CASH = balance['balanceSheetHistory']['AAPL'][0]['2020-09-26']['cash']

######TOTAL NUMBER OF SHARES######

SHARES = shares['AAPL']['sharesOutstanding']


print(SHARES)
