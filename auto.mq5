
#include <Arrays\List.mqh>
class TickObject : public CObject
{
public:
   int time;
   double avg;
   TickObject(void){}
   TickObject(int time, double avg){
      this.time = time;
      this.avg = avg;
   }
   ~TickObject(void){}
};

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

double CloseOrder(double Price)
{
  {
   int total=PositionsTotal();
   for(int i=total-1; i>=0; i--)
     {
      ulong  position_ticket=PositionGetTicket(i);
      string position_symbol=PositionGetString(POSITION_SYMBOL);
      int    digits=(int)SymbolInfoInteger(position_symbol,SYMBOL_DIGITS);
      ulong  magic=PositionGetInteger(POSITION_MAGIC);
      double volume=PositionGetDouble(POSITION_VOLUME);
      ENUM_POSITION_TYPE type=(ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      MqlTradeRequest request={};
      MqlTradeResult  result={};
      if(magic==EXPERT_MAGIC)
      {
         request.action   =TRADE_ACTION_DEAL;
         request.position =position_ticket;
         request.symbol   =position_symbol;
         request.volume   =volume;
         request.deviation=1;
         request.magic    =EXPERT_MAGIC;
         if(type==POSITION_TYPE_BUY)
         { 
           request.price=Price;
           request.type =ORDER_TYPE_SELL;
         }
         else if(type==POSITION_TYPE_SELL)
         {
           request.price=Price;
           request.type =ORDER_TYPE_BUY;
         }
         if(!OrderSend(request,result)){
            PrintFormat("OrderSend error %d",GetLastError());
            return -1;
         } 
         return result.price;
       }
     }
  }
  return -1;
}

const int slide=10;
CList ticks;

double GetMean()
{
   double sum=0;
   for(int i=0; i<ticks.Total(); i++){
      sum += ((TickObject*)ticks.GetNodeAtIndex(i)).avg;
   }
   return sum/slide;
}

double last_mean = 0;
int dir = 0;
bool active = false;
void OnTick()
{
   int time = (int)TimeCurrent();
   double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
   double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
   double avg = ((ask-bid)/2)+bid;
   TickObject* tick = new TickObject(time, avg);
   ticks.Add(tick);
   if(ticks.Total()<slide)
      return;
   double curr_mean = GetMean();
   ticks.Delete(0);
   if(last_mean == 0){
      last_mean = curr_mean;
      return;
   }
   bool buy = curr_mean > last_mean;
   bool sell = curr_mean < last_mean;
   bool finish = true;
   if(buy && dir <= 0)
      dir = 1;
   else if(sell && dir >= 0)
      dir = -1;
   else
      finish = false;
   if(active && finish){
      if(sell)
         CloseOrder(bid);
      else if(buy)
         CloseOrder(ask);
      active = false;
   }
   if(!active && (buy || sell)){
      if(buy)
         OpenOrder(ORDER_TYPE_BUY, ask, LotSize(ask, 0.1));
      else if(sell)
         OpenOrder(ORDER_TYPE_SELL, bid, LotSize(bid, 0.1));
      active = true;
   }
   last_mean = curr_mean;
}
