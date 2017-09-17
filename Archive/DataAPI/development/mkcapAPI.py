#1 c:/Users/Michael/Anaconda3/python

from coinmarketcap import Market
from pprint import pprint

def start():
	coinmarketcap = Market()
	return coinmarketcap.ticker()
	
stuff = start()
print(stuff)