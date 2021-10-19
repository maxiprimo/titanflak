
int OnInit()
{
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{

}

double LotSize(ENUM_ORDER_TYPE OrderType, double Ask, double Percent)
{
   double required_margin = 0;
   if(OrderCalcMargin(OrderType,Symbol(),1.0,Ask,required_margin))
   {
     if(NormalizeDouble(AccountInfoDouble(ACCOUNT_FREEMARGIN)/required_margin,2))
     {
       double trade_volume=NormalizeDouble((AccountInfoDouble(ACCOUNT_FREEMARGIN)/required_margin)*Percent,2);
       return trade_volume;
     }
   }
   return -1;
}

#include <Trade\Trade.mqh>
CTrade m_trade;

bool OpenOrder(ENUM_ORDER_TYPE OrderType, double Price, double Lot)
{
   return m_trade.PositionOpen(Symbol(), OrderType, Lot, Price, 0, 0, NULL);
}

void ClosePosition()
{
   for(int i=PositionsTotal()-1; i>=0; i--){
      m_trade.PositionClose(PositionGetTicket(i));
   }
}

int dir = 0;
bool active = false;
double last = 0;
void OnTick()
{
   int time = (int)TimeCurrent();
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
      ClosePosition();
      active = false;
   }
   if(!active && (buy || sell)){
      double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
      double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
      if(buy){
         OpenOrder(ORDER_TYPE_BUY, ask, LotSize(ORDER_TYPE_BUY, ask, 0.99));
      }else if(sell){
         OpenOrder(ORDER_TYPE_SELL, bid, LotSize(ORDER_TYPE_SELL, bid, 0.99));
      }
      active = true;
   }
   last = avg;
}
