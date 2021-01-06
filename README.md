# Trading_Bot
This bot is created to trade Bitcoin on trality.com

<br>

<dl>
  <dt> What trality.com offered:</dt>
  <dd> - a framework for backtesting</dd>
  <dd> - decorator schedule function that executes code at certain intervals and provides determined trading information</dd>
  <dd> - state class that saves global variables between execution intervals *</dd>
  <dd> - data class that stores trading information regarding a specific asset (Bitcoin) **</dd>
<br>   
   
  <dt> What my program does:</dt>
  <dd> - defines 4h candles from agregated 1m interval data, and assigns each with markers that are used in the trading strategy</dd>
  <dd> - sets 3 different markers that indicate when to buy Bitcoin</dd>
  <dd> - sets 3 different conditions for selling Bitcoin in case it goes down</dd>
  <dd> - sets 1 condition for raising the sell price in case Bitcoin goes up</dd>
  <dd> - buys & sells bitcoin according to the strategy</dd>
  
  <br>
  
  <dt> The logic:</dt>
  <dd> - 
  
  
       * very limited because it can only store low level data
       ** prone to errors at times when it is missing data, makes backtesting very difficult
  
</dl>
