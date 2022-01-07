import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *

if __name__ == "__main__":
    stock_list =[{}]


    for i in range(10):
        stock_list.append({"code":i,"name":i,"volume":i})
    del(stock_list[0])
    print(stock_list)