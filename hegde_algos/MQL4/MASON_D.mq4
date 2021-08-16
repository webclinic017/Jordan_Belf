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

   //FLAGS
bool maBool, macdBool, rsiBool;
   // determine other global variables

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit(){
   //init FLAGS
   maBool = macdBool = rsiBool = False;
   // TODO 
   // what else needs to be init and what other global variables?
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason){
   // TODO
   }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick(){
   

   int ticket = 0;
  //Moving Average (current chart symbol, current chart timeframe, 9 period, no shift, simple, close, most recent) 
   double movingAv = iMA(NULL,0,9,0,0,0,0);
   // what about 30 period???
   
  //MACD (Current Symbol, current timeframe, 12 fast, 26 slow
   double MacdCurrent = iMACD(NULL, 0,12,26,9,PRICE_CLOSE,MODE_MAIN,0);
   double MacdSignal = iMACD(NULL,0,12,26,9,PRICE_CLOSE, MODE_SIGNAL,0);
   double MacdPrevious = iMACD(NULL, 0,12,26,9,PRICE_CLOSE,MODE_MAIN,1);
   double MacdSignalPrevious = iMACD(NULL,0,12,26,9,PRICE_CLOSE, MODE_SIGNAL,1);
  //RSI native set up
   double RSI = iRSI(NULL, 0,14,0,0);
  //Current Price
   double currPrice = iClose(NULL,0,0);
  
  // ORDER
  //string signal = "";
   
   int total = OrdersTotal();


   if (total < 1){
      //No Open Orders
      if(AccountFreeMargin() < (1000*Lots)){
         Print("No funds. Free Margin = ", AccountFreeMargin());
         return;
      }
      if (RSI < 30) {
         rsiBool = True;
      }
      if (RSI >= 45){
         rsiBool = False;
      }
      // Second is if MACD crossed up 
      if (MACDCurrent < 0 && MACDCurrent > MACDSignal && MACDPrevious < MACDSignalPrevious && MathAbs(MACDCurrent)> 3 * Point) {
         macdBool = True;
      }
      if (MACDCurrent > 0){
         macdBool = False;
      }
      if (currPrice > movingAv){
         maBool = True;
      }
      if (currPrice <= movingAv){
         maBool = False;
      }
      if (maBool && macdBool && rsiBool) {
            //BUY
            ticket = OrderSend(Symbol(), OP_BUY, Lots, Ask, 2, 0, Ask+10000*_Point, NULL, 0, 0, Green);
            //signal = "buy";
            if(ticket>0){
               if(OrderSelect(ticket,SELECT_BY_TICKET,MODE_TRADES))
                  Print("BUY order opened : ",OrderOpenPrice());
            }
            else
                  Print("Error opening BUY order : ",GetLastError());
            return;  
      }  
   }
   else{
   Print("We have an order open");
      if (RSI>70){
         Print("OrderClose");
         OrderClose(OrderTicket(),OrderLots(),Bid,3,Violet);
         return;
      }
      if((Bid*1.0005) < (OrderOpenPrice())){
      //SELL
         Print("OrderClose");
         OrderClose(OrderTicket(),OrderLots(),Bid,3,Violet);
         return; 
      }
   }
}
//+------------------------------------------------------------------+