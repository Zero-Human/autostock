from logger import LogManager
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from errorCode import *
KOSPI_CODE = 0
KOSDAQ_CODE = 10

class Kiwoom (QAxWidget) :
    def __init__(self):
        super().__init__()
        print("Kiwoon start")
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1") 
        #이벤트 루프 
        self.login_event_loop = QEventLoop()  # 로그인 이벤트 루프 생성
        self.info_event_loop = QEventLoop()  # 주식 정보 이벤트 루프 생성
        self.set_signal_slot()
        self.CommConnect()
        # 변수모음
        self.account = self.account_Info()
        self.screen_my_info = 1 #계좌 화면 번호
        self.top_stock_list =[]
        

        Kosdaq_list =  self.get_stock_list_name(KOSDAQ_CODE)
        print(Kosdaq_list)
        self.my_Deposit()
        self.top_tr_stock()
    def handler_msg(self, err_code): 
        if err_code == 0: 
            print("로그인 성공", errors(err_code)) 
        else: 
            print("로그인 실패", errors(err_code))
        self.login_event_loop.exit()#로그인 완료 시 loop 탈출
# login
    def CommConnect(self):
        self.dynamicCall("CommConnect()")       
        self.login_event_loop.exec_()         # 프로그램 흐름을 일시중지하고 이벤트만 처리할 수 있는 상태로 만듬
# login 콜백
    def set_signal_slot(self): 
        self.OnEventConnect.connect(self.handler_msg) #로그인 콜백함수 등록
        self.OnReceiveTrData.connect(self.trdata_slot) # TR콜백함수 등록
        self.OnReceiveChejanData.connect(self.chejan_slot) # 매수매도 콜백함수 등록
# 요청 취소
    def tr_cancel(self,sScrNo):
        self.dynamicCall("DisconnectRealData(QString)",sScrNo)       
# 계좌 번호 요청
    def account_Info(self):
        self.account = self.dynamicCall("GetLoginInfo(String)","ACCNO   ").split(';')[0]
        print("계좌번호 : "+self.account)
        return self.account
# 주식정보 요청
    def sotck_info(self, code,sPrevNext="0"):
        self.dynamicCall("SetInputValue(String, String)", "종목번호", code)
        self.dynamicCall("CommRqData(String, String, int, String)","주식기본정보요청","opt10001", sPrevNext, self.screen_my_info)
# 계좌평가잔고내역
    def my_stock(self,sPrevNext="0"):
        print("계좌평가잔고내역 조회")
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)","계좌평가잔고내역","opw00018", sPrevNext, self.screen_my_info)
        self.info_event_loop.exec_()
# 예수금상세현황요청
    def my_Deposit(self,sPrevNext="0"):
        print("예수금상세현황요청 조회")
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", " ")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)","예수금상세현황요청","opw00001", sPrevNext, self.screen_my_info)
        self.info_event_loop.exec_()
# 거래량 상위 종목
    def top_tr_stock(self,sPrevNext="0"):
        print("거래량 상위 종목")
        self.dynamicCall("SetInputValue(String, String)", "시장구분", "000")
        self.dynamicCall("SetInputValue(String, String)", "정렬구분", "1")
        self.dynamicCall("SetInputValue(String, String)", "관리종목포함", "1")
        self.dynamicCall("SetInputValue(String, String)", "신용구분", "0")
        self.dynamicCall("SetInputValue(String, String)", "거래량구분", "0")
        self.dynamicCall("SetInputValue(String, String)", "가격구분", "0")
        self.dynamicCall("SetInputValue(String, String)", "거래대금구분", "0")
        self.dynamicCall("SetInputValue(String, String)", "장운영구분", "0")
        self.dynamicCall("CommRqData(String, String, int, String)","당일거래량상위요청","opt10030", sPrevNext, self.screen_my_info)
        self.info_event_loop.exec_()
# 종목조회 0: 코스피, 10: 코스닥
    def get_stock_list_name(self,code):
        stock_list = self.dynamicCall("GetCodeListByMarket(QString)",[str(code)])
        stock_list = stock_list.split(';')
        code_name_list = []
        for code in stock_list:
            name = self.dynamicCall("GetMasterCodeName(QString)", [code])  # 맨뒤는 종목코드, 코드에 따른 종목명을 가져옴
            code_name_list.append(code + " : " + name)
        return code_name_list
# sScrNo:화면 번호, sRQName: 사용자 구분명, sTrCode: TR이름,
# sRecordName: 레코드 이름, sPrevNext : 연속조회(0:연속X 2:연속 O)
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        if sRQName == "계좌평가잔고내역":
            print("계좌평가잔고내역:")
            self.dynamicCall("GetCommData(String, String, int, String)",sTrCode, sRQName, 0, "총수익률(%)")
        elif sRQName == "예수금상세현황요청":
            print("예수금상세현황요청:")
            deposit = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode, sRQName, 0, "예수금")
            print("예수금상세현황요청:"+ deposit.lstrip('0'))
        elif sRQName == "당일거래량상위요청":           
            print("당일거래량상위요청")
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)",sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName, i, "종목코드")
                name = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName, i, "종목명")
                volume = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName, i, "거래량")
                self.top_stock_list.append({"code":code.strip(),"name-":name.strip(),"volume":volume.strip()})
                for item in self.top_stock_list:
                    print(item)
        elif sRQName == "주식기본정보요청":
            print("주식기본정보요청")
            price = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode, sRQName, 0, "현재가")
            print("현재가: "+price)
        self.info_event_loop.exit()
        pass























