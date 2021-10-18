
int EXPERT_MAGIC = 9977;

int OnInit()
{
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{

}

double LotSize(double Ask, double Percent)
{
   double required_margin = 0;
   if(OrderCalcMargin(ORDER_TYPE_BUY,Symbol(),1.0,Ask,required_margin))
   {
     if(NormalizeDouble(AccountInfoDouble(ACCOUNT_FREEMARGIN)/required_margin,2))
     {
       double trade_volume=NormalizeDouble((AccountInfoDouble(ACCOUNT_FREEMARGIN)/required_margin)*Percent,2);
       return trade_volume;
     }
   }
   return -1;
}

double OpenOrder(int OrderType, double Price, double Lot)
{
   MqlTradeRequest request={};
   request.action = TRADE_ACTION_DEAL;
   request.magic = EXPERT_MAGIC;
   request.symbol = Symbol();
   request.type = OrderType;
   request.price = Price;
   request.deviation = 1;
   request.volume = Lot;
   MqlTradeResult result={};
   if(!OrderSend(request,result)){
      PrintFormat("OrderSend error %d",GetLastError());
      return -1;
   }
   return result.price;
}

#include <Trade\Trade.mqh>
CTrade m_trade;
void ClosePosition()
{
   for(int i=PositionsTotal()-1; i>=0; i--){
      ulong  position_ticket=PositionGetTicket(i);
      m_trade.PositionClose(position_ticket);
   }
}

int dir = 0;
bool active = false;
double last = 0;
void OnTick()
{
   int time = (int)TimeCurrent();
   double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
   double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
   double avg = ((ask-bid)/2)+bid;
   if(last==0){
      last = avg;
      return;
   }
   bool buy = avg > last && (avg - last) > 0.1;
   bool sell = avg < last && (last - avg) > 0.1;
   bool finish = true;
   if(buy && dir <= 0)
      dir = 1;
   else if(sell && dir >= 0)
      dir = -1;
   else
      finish = false;
   if(active && finish){
      if(sell){
         ClosePosition();
      }else if(buy){
         ClosePosition();
      }
      active = false;
   }
   if(!active && (buy || sell)){
      if(buy){
         OpenOrder(ORDER_TYPE_BUY, ask, LotSize(bid, 0.5));
      }else if(sell){
         OpenOrder(ORDER_TYPE_SELL, bid, LotSize(bid, 0.5));
      }
      active = true;
   }
   last = avg;
}
