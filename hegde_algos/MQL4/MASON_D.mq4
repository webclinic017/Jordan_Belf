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
input double StopLossPoints = 200;

//FLAGS
bool maBool, macdBool, rsiBool;
// determine other global variables

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
   //init FLAGS
   maBool = macdBool = rsiBool = False;
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
   // what about 30 period???

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
      if (RSI >= 45) {
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
         ticket = OrderSend(Symbol(), OP_BUY, Lots, Ask, 2, 0, Ask + 10000 * _Point, NULL, 0, 0, Green);
         //signal = "buy";
         if (ticket > 0) {
            if (OrderSelect(ticket, SELECT_BY_TICKET, MODE_TRADES))
               Print("BUY order opened : ", OrderOpenPrice());
         }
         else
            Print("Error opening BUY order : ", GetLastError());
         return;
      }
   }
   else {
      Print("We have an order open order 300");
      /*
      // Macd Reversal Sell Conditions
      if (MacdCurrent > 0 && MacdCurrent < MacdSignal && MacdPrevious < MacdSignalPrevious && MathAbs(MacdCurrent)> 3 * Point){
         Print("OrderClose MACD");
         OrderClose(OrderTicket(),OrderLots(),Bid,3,Violet);
         return;
      }

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
         datetime checkTime = TimeCurrent() - 30;
         if (OrderOpenTime() > checkTime){
            double stopLoss = StopLossPoints*SymbolInfoDouble(OrderSymbol(), SYMBOL_POINT); 
            double stopLossPrice = OrderOpenPrice() - stopLoss;
            stopLossPrice = NormalizeDouble(stopLossPrice, (int)SymbolInfoInteger(OrderSymbol(), _Point));
            Print("Stop Loss Triggered");
            ticket = OrderModify(OrderTicket(), OrderOpenPrice(), stopLossPrice, OrderTakeProfit(), OrderExpiration());
            return;
         }
      }     
   }
}
//+------------------------------------------------------------------+