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
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+

   //FLAGS
   bool maBool, macdBool, rsiBool;
   // determine other global variables
   
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
   double MACDCurrent = iMACD(NULL, 0,12,26,9,PRICE_CLOSE,MODE_MAIN,0);
   double MACDSignal = iMACD(NULL,0,12,26,9,PRICE_CLOSE, MODE_SIGNAL,0);
  
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
   if (RSI < 30)
      // Second is if MACD crossed up 
      if ( MACDCurrent < 0 && MACDCurrent < MACDSignal) {
         if (currPrice >= movingAv){
            //BUY
            ticket = OrderSend(Symbol(), OP_BUY, Lots, Ask, 2, 0, Ask+100*_Point, NULL, 0, 0, Green);
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
      else if (RSI > 70) {
         //SELL
         if(!OrderClose(OrderTicket(),OrderLots(),Bid,3,Violet))
            Print("OrderClose error ",GetLastError());
         if(!OrderModify(OrderTicket(),OrderOpenPrice(),Bid-Point,OrderTakeProfit(),0,Green))
            Print("OrderModify error ",GetLastError());
         return;     
      }
      else{
         Print("RSI is 30 or 70");
         return;
         }
   }


   // if (total<1){
   //    //No Open Orders
   //    if(AccountFreeMargin() < (1000*Lots)){
   //       Print("No funds. Free Margin = ", AccountFreeMargin());
   //       return;
   //    }
   //    // BUY CONDITIONS
   //    first flag is if RSI is below 30
   //    if( RSI < 30){
   //       rsiBool = TRUE;
   //    } 
   //    if (rsiBool == TRUE) {
   //    // Second is if MACD crossed up 
   //       if ( MACDCurrent < 0 && MACDCurrent < MACDSignal) {
   //          macdBool = TRUE;
   //       }
   //    }
   //     // third is if price went above MA
   //    if (rsiBool == TRUE && macdBool == TRUE && (currPrice >= movingAv)){
   //       //BUY
   //       ticket = OrderSend(Symbol(), OP_BUY, Lots, Ask, 2, 0, Ask+100*_Point, NULL, 0, 0, Green);
   //       //signal = "buy";
   //       if(ticket>0){
   //          if(OrderSelect(ticket,SELECT_BY_TICKET,MODE_TRADES))
   //             Print("BUY order opened : ",OrderOpenPrice());
   //       }
   //       else{
   //          Print("Error opening BUY order : ",GetLastError());
   //       }
   //       return;
   //      }
   //    }
   //    // SELL CONDITIONS
   //    // RSI crosses down indicating a downward movement
   //    if (RSI > 70) {
   //       //SELL
   //       if(!OrderClose(OrderTicket(),OrderLots(),Bid,3,Violet))
   //          Print("OrderClose error ",GetLastError());
   //       return;
   //       if(!OrderModify(OrderTicket(),OrderOpenPrice(),Bid-Point,OrderTakeProfit(),0,Green))
   //          Print("OrderModify error ",GetLastError());
   //       return;
   //    }
   // }
//
//   if (signal == "buy" && OrdersTotal() == 0){
//      OrderSend(_Symbol,OP_BUY,0.10, Ask, 3,0,Ask+100*_Point, NULL, 0, 0, Green);
//   }
//   if (signal == "sell" && OrdersTotal() == 0){
//      OrderSend(_Symbol,OP_SELL,0.10, Bid, 3,0,Bid-100*_Point, NULL, 0, 0, Red);
//   }
//   Comment("Current signal:", signal);
//  }
//+------------------------------------------------------------------+
