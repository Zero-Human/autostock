import sys
from stock import *
from PyQt5.QtWidgets import *
class Main():
    def __init__(self):
        print("메인 클래스입니다.")
        self.app = QApplication(sys.argv)
        self.Kiwoom = Kiwoom() 
        self.app.exec() # 이벤트 루프 실행.

if __name__ == "__main__":
    Main()



