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
  
  <dt> The logic: the program handles a balance, figures out when to sell, when to buy, how much to buy and how much of the asset to risk</dt>
  
  <br>
  
  <dt> Error Handling:</dt>
  <i>because trality.com is still in beta at the time I wrote this program, there is a lot of error handling present in the code</i>
  <dd> - at each interval the candle could be missing from the database, so I've implemented a try and catch</dd>
  <dd> - 4h candles were needed so I've created them from 1m candles, to minimise the missing data that could be offered at any candle interval</dd>
  <dd> - auto-cleanup functions for old stored data, to keep a low memory usage</dd>
  <dd> - used forced market sell function because the documentation was badly written and could not use the more specific sell functions</dd>
  <dd> - set the datetime timestamp for each candle to reflect reality, from a unix timestamp that did not have a timezone.</dd>
</dl> 

<footer> 
  <pre>
* very limited because it can only store low level data<br>
** prone to errors at times when it is missing data, makes backtesting very difficult
  </pre>
</footer>
