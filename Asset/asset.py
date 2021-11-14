"""
TODO: central information of the opened position is stored here. Gets instantiated if a new announcement is detected.
   - starts buy-thread (maybe also a class)
   - handles accumulated position and stops buy-thread if the desired position is reached
   - with the first successful buy of a coin a Instance of TrailingStopLoss gets opened and executed in its own thread
   - if TrailingStopLoss-thread stops, the position is closed and the asset is not active anymore
   - -> logging, handling of accumulated positions when bot gets restarted (decorators, json export to local machine)

   The idea is, to construct this class with every detected listing (-> easy multi-listing support)
"""
