#property description "Easy Ultimate Capital. Slide Exchange Wave. High-Leverage, No-Commission, Low-Spread."
#property copyright "MaxiPrimo 2021"
#property link      "http://www.linkedin.com/in/ms84"
#property version   "1.1"

input double INPUT_TradeLotSize = 0.5; // Trade Capital Usage
input double INPUT_MaxTradeVolume = 47.5; // Maximum Trade Volume
input int INPUT_MaxCapital = 10*1000; // Maximum Capital In Currency
input int INPUT_MaxRunMinutes = 10000; // Maximal Minutes To Run
input double INPUT_CapitalFallback = 0.35; // Maximal Capital Lost Fallback

int max_error = 5;
int error_count = 0;

bool CheckError(bool NoError){
   if(!NoError){
      error_count++;
      if(error_count >= max_error){
         ExitTrader("Max Error.");
         return NoError;
      }
   }else{
      error_count = 0;
   }
   return NoError;
}

void ExitTrader(string Msg){
   ClosePosition();
   Print("Exit Trader: "+Msg);
   ExpertRemove();
}

double LotSize(ENUM_ORDER_TYPE OrderType, double Price, double Percent)
{
   double required_margin = 0;
   if(OrderCalcMargin(OrderType,Symbol(),1.0,Price,required_margin)){
     double trade_volume=NormalizeDouble((AccountInfoDouble(ACCOUNT_FREEMARGIN)/required_margin)*Percent,2);
     if(trade_volume)
       return trade_volume;
   }
   return -1;
}

#include <Trade\Trade.mqh>
CTrade m_trade;

bool OpenOrder(ENUM_ORDER_TYPE OrderType, double Price, double Lot)
{
   bool NoError = m_trade.PositionOpen(Symbol(), OrderType, Lot, Price, 0, 0, NULL);
   return NoError;
}

bool ClosePosition()
{
   bool NoError = true;
   for(int i=PositionsTotal()-1; i>=0; i--){
      if(!m_trade.PositionClose(PositionGetTicket(i))){
         NoError = false;
      }
   }
   return NoError;
}

void PrepareBuffer(int Index, double& Array[]){
   ZeroMemory(Array);
   CopyBuffer(handle, Index, 0, 3, Array);
   ArraySetAsSeries(Array, true);
}

int file=0;
int handle=0;
int OnInit()
{
   ClosePosition();
   file = FileOpen("market.txt", FILE_WRITE|FILE_TXT, "", CP_UTF8);
   handle = iCustom(Symbol(), PERIOD_CURRENT, "binarywave");
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
   FileFlush(file);
   FileClose(file);
   ExitTrader("Unload.");
}

int dir = 0;
bool active = false;
int start = 0;
double capital = 0;
void OnTick()
{
   int time = (int)TimeCurrent();
   if(start == 0)
      start = time;
   if(time >= start + (INPUT_MaxRunMinutes*60))
      ExitTrader("Run Time Ended.");
   double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
   double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
   double avg = ((ask-bid)/2)+bid;
   FileWriteString(file, time+"|"+bid+"|"+ask+"|"+ iLow(Symbol(), PERIOD_M1, 0)+"|"+ iHigh(Symbol(), PERIOD_M1, 0)+" \n");
   FileFlush(file);
   double Buffer[];
   PrepareBuffer(0, Buffer);
   bool buy = Buffer[1] > Buffer[2];
   bool sell = Buffer[1] < Buffer[2];
   bool finish = true;
   if(buy && dir <= 0)
      dir = 1;
   else if(sell && dir >= 0)
      dir = -1;
   else
      finish = false;
   if(active && finish){
      if(CheckError(ClosePosition()))
         active = false;
   }
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   if(balance >= INPUT_MaxCapital)
      ExitTrader("Maximal Capital Reached.");
   if(capital == 0)
      capital = balance;
   if(balance <= capital * INPUT_CapitalFallback)
      ExitTrader("Capital Fallback.");
   if(!active && (buy || sell)){
      ENUM_ORDER_TYPE type = (buy?ORDER_TYPE_BUY:ORDER_TYPE_SELL);
      double price = (buy?ask:bid);
      double lot = LotSize(type, price, INPUT_TradeLotSize);
      if(lot>INPUT_MaxTradeVolume)
         lot = INPUT_MaxTradeVolume;
      if(CheckError(OpenOrder(type, price, lot)))
         active = true;
   }
}
