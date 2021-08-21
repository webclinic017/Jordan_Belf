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
input double StopLossPoints = 150;

//FLAGS
bool maBool, macdBool, rsiBool;
int stopLevel;
double stopLoss;
// determine other global variables

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
   //init FLAGS
   maBool = macdBool = rsiBool = False;
   stopLevel = MarketInfo(Symbol(), MODE_STOPLEVEL);
   stopLoss = 0;
   // TODO
   // what else needs to be init and what other global variables?
   return (INIT_SUCCEEDED);
}
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
   // TODO
}



void TrailingStopLoss(double Trailingstart, double Trailingstop) {
   return;
}


//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {


   int ticket = 0;
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

   // ORDER
   //string signal = "";

   int total = OrdersTotal();


   if (total < 1) {
      
      //No Open Orders
      if (AccountFreeMargin() < (1000 * Lots)) {
         Print("No funds. Free Margin = ", AccountFreeMargin());
         return;
      }
      if (RSI < 30) {
         rsiBool = True;
      }
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
         //BUY
         //signal = "buy";

         ticket = OrderSend(Symbol(), OP_BUY, Lots, Ask, 2, stopLoss, NULL, NULL, 0, 0, Green);
         
         if (ticket > 0) {
            if (OrderSelect(ticket, SELECT_BY_TICKET, MODE_TRADES))
               Print("BUY order opened new : ", OrderOpenPrice());
         }
         else
            Print("Error opening BUY order : ", GetLastError());
         return;
      }
   }
   else {
      Print("We have an order open order 300");
      // Macd Reversal Sell Conditions
      /*
      if (MacdCurrent > 0 && MacdCurrent < MacdSignal && MacdPrevious < MacdSignalPrevious && MathAbs(MacdCurrent)> 3 * Point){
         Print("OrderClose MACD");
         OrderClose(OrderTicket(),OrderLots(),Bid,3,Violet);
         return;
      }
      */
      /*
      //RSI Sell Conditions
      else if (RSI > 70){
         Print("OrderClose RSI");
         OrderClose(OrderTicket(),OrderLots(),Bid,3,Violet);
         return;
      }
      */
      // Trailing Stop Loss
      double tStopLoss = NormalizeDouble(OrderStopLoss(), Digits);

      if ( Ask > NormalizeDouble(OrderOpenPrice() + TrailingStart * _Point, Digits) && tStopLoss < NormalizeDouble(Bid - (TrailingStop + TrailingStep)* _Point, Digits)) {
         tStopLoss = NormalizeDouble(Bid - TrailingStop * _Point, Digits);
         ticket = OrderModify(OrderTicket(), OrderOpenPrice(), tStopLoss, OrderTakeProfit(), 0, Blue);
         if (ticket > 0) {
              Print ("TrailingStop #2 Activated: ", OrderSymbol(), ": SL", tStopLoss, ": Bid", Bid);
              return;
         }
         return;
      }
      //Stop Loss
      else{
         return;
      }     
   }
}


double StopLoss_V1(double stopLoss, int stopLevel, int ticket) {
// Stop Loss Code for Sell Modifaction 
      datetime checkTime = TimeCurrent() - 30;
      double stopLossPrice = 0.0;
      if (OrderOpenTime() > checkTime){
         stopLoss = StopLossPoints*SymbolInfoDouble(OrderSymbol(), SYMBOL_POINT); 
         stopLossPrice = OrderOpenPrice() - stopLoss;
         stopLossPrice = NormalizeDouble(stopLossPrice, (int)SymbolInfoInteger(OrderSymbol(), _Point));
         Print("Stop Loss Triggered in Sell");
         ticket = OrderModify(OrderTicket(), OrderOpenPrice(), stopLossPrice, OrderTakeProfit(), OrderExpiration());
      }
      return stopLossPrice;
}

double StopLoss_V2(double stopLoss, double StopLossPoints){
   // Stop Loss Code for buy modifcation
   if(Bid - StopLossPoints < stopLevel * _Point){
      stopLoss = Bid - StopLossPoints * _Point;
      Print("Stop Loss set: ", stopLoss);
   }
   else {
      stopLoss = 0;
      Print("Stop Loss set: ", stopLoss);
   }
   return stopLoss;
}
//+------------------------------------------------------------------+