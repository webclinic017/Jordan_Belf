//+------------------------------------------------------------------+
//|                                                      MASON_D.mq4 |
//|                        Copyright 2021, MetaQuotes Software Corp. |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, MetaQuotes Software Corp."
#property link      ""
#property version   "1.00"
#property strict

input double Lots = 0.1;
input double TrailingStart = 300.0;
input double TrailingStep = 10.0;
input double TrailingStop = 50.0;
input double StopLossPoints = 20.0;
input double AccountRisk = .01;
input double PipRisk = 50;

//FLAGS
bool maBool, macdBool, rsiBool, maSellBool, macdSellBool, rsiSellBool;
int stopLevel;
double stopLoss;
datetime currentBuyTime;
// determine other global variables

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
   //init FLAGS
   //Setting Open buy conditions to false
   maBool = macdBool = rsiBool = False;
   //Setting open sell conditions to false
   maSellBool = macdSellBool = rsiBool = False;
   stopLevel = MarketInfo(Symbol(), MODE_STOPLEVEL);
   stopLoss = 0;
   currentBuyTime = TimeCurrent();

   return (INIT_SUCCEEDED);
}
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
   // TODO
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {


   int ticket = 0;
   int ticketSell = 0;
   //Moving Average (current chart symbol, current chart timeframe, 9 period, no shift, simple, close, most recent)
   double movingAv = iMA(NULL, 0, 9, 0, 0, 0, 0);

   //MACD (Current Symbol, current timeframe, 12 fast, 26 slow
   double MacdCurrent = iMACD(NULL, 0, 12, 26, 9, PRICE_CLOSE, MODE_MAIN, 0);
   double MacdSignal = iMACD(NULL, 0, 12, 26, 9, PRICE_CLOSE, MODE_SIGNAL, 0);
   double MacdPrevious = iMACD(NULL, 0, 12, 26, 9, PRICE_CLOSE, MODE_MAIN, 1);
   double MacdSignalPrevious = iMACD(NULL, 0, 12, 26, 9, PRICE_CLOSE, MODE_SIGNAL, 1);
   //RSI native set up
   double RSI = iRSI(NULL, 0, 14, 0, 0);
   //Current Price
   double currPrice = iClose(NULL, 0, 0);

   int total = OrdersTotal();
   //Order Accounting section designed to check all open positions' trailing stop loss status

   if (AccountFreeMargin() < (1000 * Lots)) {
      Print("No funds. Free Margin = ", AccountFreeMargin());
      return;
   }

   if (TimeCurrent() > currentBuyTime + 1800){
   //RSI Check
      if (RSI < 30) {
         rsiBool = True;
      }
      //RSI Reset
      if (RSI >= 50) {
         rsiBool = False;
      }
      // Second is if MACD crossed up
      if (MacdCurrent < 0 && MacdCurrent > MacdSignal && MacdPrevious < MacdSignalPrevious && MathAbs(MacdCurrent) > 3 * Point) {
         macdBool = True;
      }
      if (MacdCurrent > 0) {
         macdBool = False;
      }
      if (currPrice > movingAv) {
         maBool = True;
      }
      if (currPrice <= movingAv) {
         maBool = False;
      }
      if (maBool && macdBool && rsiBool) {
    
         double lots = LotSize(AccountRisk, PipRisk, 2);
         currentBuyTime = TimeCurrent();
         if(lots == -1){
            Print("Error getting lot size");
            lots = Lots;
         }
         else{
            //stopLoss = StopLoss_V2(StopLossPoints);
            ticket = OrderSend(Symbol(), OP_BUY, lots, Ask, 2, stopLoss, NULL, NULL, 0, 0, Green);
            maBool = false;
            macdBool = false;
            rsiBool = false;
         }  
         if (ticket > 0) {
            if (OrderSelect(ticket, SELECT_BY_TICKET, MODE_TRADES))
               Print("BUY order opened new : ", OrderOpenPrice());
         }
         else {
            Print("Error opening BUY order : ", GetLastError());
         }
         return;
      }

      //Checking Opening Sell Conditions
      if(RSI > 70){
         rsiSellBool = true;
      }
      if(RSI <= 50){
         rsiSellBool = false;
      }
      if(MacdCurrent > 0 && MacdCurrent < MacdSignal && MacdPrevious > MacdSignalPrevious && MathAbs(MacdCurrent) > 3 * Point) {
         macdSellBool = True;
      }
      if(MacdCurrent < 0) {
         macdSellBool = False;
      }
      if(currPrice < movingAv) {
         maSellBool = True;
      }
      if(currPrice >= movingAv) {
         maSellBool = False;
      }
      if(rsiSellBool && macdSellBool && maSellBool){
         
         double lots = LotSize(AccountRisk, PipRisk, 2);
         currentBuyTime = TimeCurrent();
         if(lots == -1){
            Print("Error getting lot size");
            lots = Lots;
         }
         else{
            //stopLoss = StopLoss_V2(StopLossPoints);
            ticketSell = OrderSend(Symbol(), OP_SELL, lots, Bid, 2, 10000 * _Point + Ask, NULL, NULL, 0, 0, Green);
            maSellBool = false;
            macdSellBool = false;
            rsiSellBool = false;
         }
         if (ticketSell > 0) {
            if (OrderSelect(ticketSell, SELECT_BY_TICKET, MODE_TRADES))
               Print("Sell order opened new : ", OrderOpenPrice());
         }
         else {
            Print("Error opening BUY order : ", GetLastError());
         }
         return;
      } 
   }
   //Closing positions
   RefreshRates();
   if(OrdersTotal() > 0){
      for(int i = total-1; i >= 0; i--){
         //Print("Total: ", total);
         //Error checking; making Sure we can select the order
         OrderSelect(i,SELECT_BY_POS, MODE_TRADES);
         if(OrderType() <= OP_SELL && OrderSymbol() == Symbol()){
            //StopLoss_V1(OrderTicket(), StopLossPoints);
            // Trailing Stop Loss
            double tStopLoss = NormalizeDouble(OrderStopLoss(), Digits);
            double sl = OrderStopLoss();
            if(OrderType() == OP_BUY){
               if ( Ask > NormalizeDouble(OrderOpenPrice() + TrailingStart * _Point, Digits) && tStopLoss < NormalizeDouble(Bid - (TrailingStop + TrailingStep)* _Point, Digits)) {
                  tStopLoss = NormalizeDouble(Bid - TrailingStop * _Point, Digits);
                  Print(tStopLoss);
                  ticket = OrderModify(OrderTicket(), OrderOpenPrice(), tStopLoss, OrderTakeProfit(), 0, Blue);
                  if (ticket > 0) {
                       //Print ("TrailingStop #1 Activated: ", OrderSymbol(), ": SL", tStopLoss, ": Bid", Bid);
                       return;
                  }
                  //return;
               }
            }
            if (OrderType() == OP_SELL) {
                if ((Bid < NormalizeDouble(OrderOpenPrice() - TrailingStart * _Point, Digits) && (sl > (NormalizeDouble(Ask + (TrailingStop + TrailingStep)*_Point, Digits)))) || (OrderStopLoss() == 0)) {
                  tStopLoss = NormalizeDouble(Ask + TrailingStop * _Point, Digits);
                  Print("sl: ", tStopLoss);
                  ticketSell = OrderModify(OrderTicket(), OrderOpenPrice(), tStopLoss, OrderTakeProfit(), 0, Red);
                  if (ticketSell > 0) {
                    Print ("Trailing #2 Activated: ", OrderSymbol(), ": SL ",tStopLoss, ": Ask ", Ask);
                    return ;
                  }
               }
            }
         }
      }
   }
      //Stop Loss
   else{
      return;
   } 
}
   


//-------------STOP LOSS FUNCTIONS------------------------------


void StopLoss_V1(int ticket, double stopPoints) {
// Stop Loss Code for Sell Modifaction 
      double sLoss;
      datetime checkTime = TimeCurrent() - 30;
      double stopPrice = 0.0;
      if (OrderOpenTime() > checkTime){
         sLoss = stopPoints*SymbolInfoDouble(OrderSymbol(), SYMBOL_POINT); 
         stopPrice = OrderOpenPrice() - sLoss;
         stopPrice = NormalizeDouble(stopPrice, (int)SymbolInfoInteger(OrderSymbol(), _Point));
         Print("Stop Loss Triggered in Sell");
         ticket = OrderModify(OrderTicket(), OrderOpenPrice(), stopPrice, OrderTakeProfit(), OrderExpiration());
      }
      return;
}

double StopLoss_V2(double stopPoints){
   double sLoss;
   // Stop Loss Code for buy modifcation
   if(Bid - stopPoints < stopLevel * _Point){
      sLoss = Bid - stopPoints * _Point;
      Print("Stop Loss set: ", sLoss);
   }
   else {
      sLoss = 0;
      Print("Stop Loss set: ", sLoss);
   }
   return sLoss;
}


//+-------------------------------Position Size Function--------------------------------+

//Function will dynmacally size lots to trade per trade based off the total account value
//and the amount of risk
//Risk: Percentage of account willing to trade per trade
//Pips At Risk: Number of pips before exiting a trade for a loss  
//Lot Mode: Type of lots being traded; 0 = micro, 1 = mini, 2 = standard
double LotSize(double risk, double pipsAtRisk, int lotMode){

   //Initalizing Varibles for calculations
   double accountVal = AccountBalance();
   double accountFree = AccountFreeMargin();
   double lotMargin = MarketInfo(Symbol(), MODE_MARGINREQUIRED);
   double minLot = MarketInfo(Symbol(), MODE_MINLOT);
   double lotStep = MarketInfo(Symbol(), MODE_LOTSTEP);
   double pipLotValue = 0;

   //Calculating the pipLotValue based off the 
   switch(lotMode){
      case 0:
         pipLotValue = .1;
         break;
      case 1:
         pipLotValue = 1;
         break;
      case 2:
         pipLotValue = 10;
         break;
      default:
         Print("Lot size must be 0: Micro, 1: Mini, 2: Standard");
         return -1;
   }
   //Calculating the lots to be traded
   double pipValue = pipLotValue * Ask;
   double dollarRisk = accountVal  * risk;
   double lotsToTrade = MathFloor(dollarRisk/(pipsAtRisk * pipValue));
   //Error Checking
   if(lotsToTrade < minLot){
      lotsToTrade = minLot;
   }
   if(lotsToTrade * lotMargin > accountFree){
      Print("Not enough money for the trade");
      return(-1);
   }
   else{
      Print("lotsToTrade: ", lotsToTrade);
      return(lotsToTrade);
   }
}
