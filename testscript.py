import pandas as pd

def test():
	l_1 = ['key1', 'key2', 'key3']
	l_2 = ['value1', 'val2', 'val3']

	data = dict(zip(l_1, l_2))
	f = open("testout.txt", "w")
	f.write(str(data))
    

if __name__ == '__main__':
	test()

