import numpy as np

from .BaseTRRT import BaseTR, BaseRealtime
from .ParameterBooks import InputParameterBook as Ibook
from .ParameterBooks import OutputParameterBook as Obook
from . import Logger
from . import APIErrors


class AccountList(BaseTR):
	NAME, DESCRIPTION = "AccountList", "계좌목록조회"
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),
		('계좌명', 'U20')
	])


class stock_mst(BaseTR):
	NAME, DESCRIPTION = 'stock_mst', '현물종목정보조회(전종목)'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),
		('단축코드', 'U6'),
		('장구분',   'U1'),
		('종목명',   'U40'),
		('KOSPI200세부업종', 'U1'),
		('결산월일', 'U4'),
		('거래정지구분', 'U1'),
		('관리구분', 'U1'),
		('시장경보구분코드', 'U1'),
		('락구분', 'U2'),
		('불성실공시지정여부', 'U1'),
		('증거금구분', 'U1'),
		('신용증거금구분', 'U1'),
		('ETF구분자', 'U1'),
		('소속구분', 'U2')
	])


class TR_SCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_SCHART', '현물분/일/주/월데이터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),
		('그래프종류', 'U1'),  # 그래프종류.분데이터, 그래프종류.일데이터, 그래프종류.주데이터, 그래프종류.월데이터
		('시간간격', 'U3'),  # 분데이터 : 1 - 30, 일/주/월데이터일 경우 1
		('시작일', 'U8'),  # YYYYMMDD // 갯수지정시 00000000
		('종료일', 'U8'),  # YYYYMMDD // 갯수지정시 99999999
		('조회갯수', 'U4'),  # 1 - 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자',    'U8'),        # 0
		('시간',    'U6'),        # 1
		('시가',    np.uint32),   # 2
		('고가',    np.uint32),   # 3
		('저가',    np.uint32),   # 4
		('종가',    np.uint32),   # 5
		('주가수정계수', np.float32),     # 6
		('거래량수정계수', np.float32),   # 7
		('락구분',   'U4'),              # 8
		('단위거래량', np.uint64),       # 9
		('단위거래대금', np.uint64)       # 10
		])
	
	def _set_input_data(self,
						code6 : str,
						그래프종류=Ibook.그래프종류.일데이터,
						시간간격='1',
						시작일='00000000', 
						종료일='99999999',
						조회갯수='120') -> None:
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 0, str(code6))
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 1, 그래프종류)
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 2, 시간간격)
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 3, 시작일)
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 4, 종료일)
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 5, 조회갯수)

	def _get_rcvd_multi_data(self) -> None:
		'''
		It is an Overriden Method Due to Adjusted Prices.
		'''
		super()._get_rcvd_multi_data()
		nCnt = self.multi_output.shape[0]

		# 주가수정계수에 의한 수정주가(Adj Price) 계산
		gaps_idx = np.where(self.multi_output['주가수정계수'] != 1.0)[0]
		gaps = self.multi_output[gaps_idx]['주가수정계수']
		for idx, gap in zip(gaps_idx, gaps):
			for i in range(idx+1, nCnt):
				for j in ('시가', '고가', '저가', '종가'):
					self.multi_output[i][j] *= gap
		del gaps_idx, gaps

		# 거래량수정계수에 의한 수정거래량(Adj Volume) 계산
		gaps_idx = np.where(self.multi_output['거래량수정계수'] != 1.0)[0]
		gaps = self.multi_output[gaps_idx]['거래량수정계수']
		for idx, gap in zip(gaps_idx, gaps):
			for i in range(idx + 1, nCnt):
				for j in ('단위거래량', ):
					self.multi_output[i][j] *= gap
		del gaps_idx, gaps
		return


class SB(BaseTR):
	NAME, DESCRIPTION = 'SB', '현물 마스터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('장구분', 'U1'),  # (F:02) 0:유가증권, 1:코스닥
		('일련번호', 'U4'),  # (F:03) 
		('입회일자', 'U8'),  # (F:04) 
		('한글종목명', 'U40'),  # (F:05) 
		('영문종목명', 'U40'),  # (F:06) 
		('제조업구분/업종대분류', 'U3'),  # (F:07) 
		('업종중분류', 'U3'),  # (F:08) 
		('업종소분류', 'U3'),  # (F:09) 
		('산업업종코드', 'U6'),  # (F:10) 
		('KOSPI200/KOSDAQ50채용구분', 'U1'),  # (F:11) 0:미분류, 1:건설기계, 2:조선운송, 3:철강소재, 4:에너지화학, 5:정보통신, 6:금융, 7:필수소비재, 8:자유소비재
		('KOSPI100채용구분', 'U1'),  # (F:12) Y/N
		('KOSPI50채용구분', 'U1'),  # (F:13) Y/N
		('정보통신지수채용구분', 'U1'),  # (F:14) 0:미채용
		('시가총액규모/지수업종그룹', 'U1'),  # (F:15) (유가) 0:제외, 1:대, 2:중, 3:소 (코스닥) 0:제외, 1:KOSDAQ100, 2:KOSDAQmid300, 3:KOSDAQsmall
		('KOSDI구분/지배구조우량구분', 'U2'),  # (F:16) (유가) 00:일반, 01:배당지수종목, 03:우량, 04:배당+우량 (코스닥) 00:일반, 01:우량, 02:KOSTAR지수종목, 03:우량+KOSTAR
		('상장구분', 'U2'),  # (F:17) 01:정상, 02:신규, 03:신주상장, 04:기준가산출후거래무, 05:상장폐지, 06:주식병합, 07:기준가조정
		('상장주식수', 'U15'),  # (F:18) 
		('소속구분', 'U2'),  # (F:19) ST:주식, MF:증권투자회사, RT:리츠, SC:선박투자회사, IF:인프라투융자회사, DR:예탁증서, SW:신주인수권증권, SR:신주인수권증서, BW:주식워런트증권(ELW), FU:선물, OP:옵션, EF:상장지수펀드(ETF), BC:수익증권, FE:해외ETF, FS:해외원주, EN: ETN
		('결산월일', 'U4'),  # (F:20) 상장사의 회계결산일(12월 31일, 6월 30일, 3월 31일) 결산기나 결산월일 경우는 12월일 경우 '1200'로 표시
		('액면가', 'U9'),  # (F:21) 외국주권일 경우 소숫점셋째자리까지 표현가능
		('액면가변경구분코드', 'U2'),  # (F:22) 00:해당없음, 01:액면분할, 02:액면병합, 99:기타
		('전일종가', 'U9'),  # (F:23) 
		('전일거래량', 'U12'),  # (F:24) 
		('전일거래대금', 'U18'),  # (F:25) 
		('기준가', 'U9'),  # (F:26) 
		('상한가', 'U9'),  # (F:27) 
		('하한가', 'U9'),  # (F:28) 
		('대용가', 'U9'),  # (F:29) 
		('거래정지구분', 'U1'),  # (F:30) 0:정상, 1:정지, 5:CB발동
		('관리구분', 'U1'),  # (F:31) 0:정상, 1:관리
		('감리구분', 'U1'),  # (F:32) 0:정상, 1:주의, 2:경고, 3:위험
		('락구분', 'U2'),  # (F:33) 00:발생안함, 01:권리락, 02:배당락, 03:분배락, 04:권배락, 05:중간배당락, 06:권리중간배당락, 99:기타 ※미해당의 경우 SPACE
		('불성실공시지정여부', 'U1'),  # (F:34) 0:정상, 1:불성실공시지정
		('평가가격', 'U9'),  # (F:35) 
		('최고호가가격', 'U9'),  # (F:36) 
		('최저호가가격', 'U9'),  # (F:37) 
		('매매구분', 'U1'),  # (F:38) 1:보통, 2:신규상장, 3:관리지정, 4:관리해제, 5:정리매매, 6:30일간거래정지후재개, 7:시가기준가산출, 8:단일가매매
		('정리매매시작일', 'U8'),  # (F:39) 
		('정리매매종료일', 'U8'),  # (F:40) 
		('투자유의구분', 'U1'),  # (F:41) 
		('REITs구분', 'U1'),  # (F:42) 1:일반리츠, 2:CRV리츠
		('매매수량단위', 'U5'),  # (F:43) 
		('시간외매매수량단위', 'U5'),  # (F:44) 
		('자본금', 'U18'),  # (F:45) 
		('배당수익율', 'U8'),  # (F:46) 9(6)V9(1)
		('ETF분류', 'U1'),  # (F:47) 0:일반형, 1:투자회사형, 2:수익증권형
		('ETF관련지수업종대', 'U1'),  # (F:48) 1:유가증권, 2:코스닥, 3:섹터, 4:GICS, 8:MF(매경), 9:해외
		('ETF관련지수업종중', 'U3'),  # (F:49) 
		('ETF CU단위', 'U8'),  # (F:50) 
		('ETF 구성종목수', 'U4'),  # (F:51) 
		('ETF 순자산총액', 'U15'),  # (F:52) 
		('ETF관련지수대비비율', 'U12'),  # (F:53) 9(5)V9(6) ETF대상지수 대비 Etf종목 종가의 비율
		('최종NAV', 'U10'),  # (F:54) 9(7)V9(2) 송신일자의 최종NAV 자료
		('매매방식 구분', 'U1'),  # (F:55) 0 : 일반 1: 시초동시 임의종료 지정 2: 시초동시 임의종료 해제 3: 마감동시 임의종료 지정 4: 마감동시 임의종료 해제 5: 시간외단일가 임의종료 지정 6: 시간외단일가 임의종료 해제
		('통합지수종목구분', 'U1'),  # (F:56) 0:일반종목, 1:통합지수종목
		('매매개시일', 'U8'),  # (F:57) 
		('KRX 섹터지수 자동차구분', 'U1'),  # (F:58) 0:일반종목, 1:KRX섹터지수 자동차구분
		('KRX 섹터지수 반도체구분', 'U1'),  # (F:59) 0:일반종목, 1:KRX섹터지수 반도체구분
		('KRX 섹터지수 바이오구분', 'U1'),  # (F:60) 0:일반종목, 1:KRX섹터지수 바이오구분
		('KRX 섹터지수 금융구분', 'U1'),  # (F:61) 0:일반종목, 1:KRX섹터지수 금융구분
		('KRX 섹터지수 정보통신구분', 'U1'),  # (F:62) 0:일반종목, 1:KRX섹터지수 정보통신구분
		('우회상장구분', 'U'),  # (F:63) 
		('KOSPI여부', 'U'),  # (F:64) 
		('KRX섹터지수화학에너지구분', 'U'),  # (F:65) 
		('KRX섹터지수철강구분', 'U'),  # (F:66) 
		('KRX섹터지수필수소비재구분', 'U'),  # (F:67) 
		('KRX섹터지수미디어통신구분', 'U'),  # (F:68) 
		('KRX섹터지수건설구분', 'U'),  # (F:69) 
		('KRX섹터지수비은행금융구분', 'U'),  # (F:70) 
		('국가코드', 'U'),  # (F:71) 
		('적용화폐단위', 'U'),  # (F:72) 
		('적용환율', 'U'),  # (F:73) 
		('투자위험예고여부', 'U'),  # (F:74) 
		('ETF유통주식수', 'U'),  # (F:75) 
		('ETF자산기준통화', 'U'),  # (F:76) 
		('ETF순자산총액(외화)', 'U'),  # (F:77) 
		('ETF유통순자산총액(원화)', 'U'),  # (F:78) 
		('ETF유통순자산총액(외화)', 'U'),  # (F:79) 
		('ETF최종NAV(외화)', 'U'),  # (F:80) 
		('KRX섹터지수증권구분', 'U'),  # (F:81) 
		('KRX섹터지수조선구분', 'U'),  # (F:82) 
		('장전시간외시장가능여부', 'U'),  # (F:83) 
		('공매도가능여부', 'U1'),  # (F:84) 1: 가능, 0: N or 공매도과열종목지정
		('ETF추적기초자산단위코드', 'U'),  # (F:85) 
		('ETF추적수익률배수부호', 'U'),  # (F:86) 
		('ETF추적수익률배수', 'U'),  # (F:87) 
		('ETF장외파생상품편입여부', 'U'),  # (F:88) 
		('ETF추적기초자산국내외구분코드', 'U'),  # (F:89) 
		('상장일자', 'U'),  # (F:90) 
		('발행가격', 'U'),  # (F:91) 
		('SRI지수여부', 'U'),  # (F:92) 
		('ETF참고지수소속시장구분코드', 'U'),  # (F:93) 
		('ETF참고지수업종코드', 'U'),  # (F:94) 
		('KRX섹터지수보험구분', 'U'),  # (F:95) 
		('KRX섹터지수운송구분', 'U'),  # (F:96) 
		('REGULATIONS적용여부', 'U'),  # (F:97) 
		('일련번호8자리', 'U'),  # (F:98) 
		])
	MULTI_OUTPUT_DTYPE = None

	def _set_input_data(self, code6) -> None:
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 0, code6)
	


class SC(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'SC', '현물현재가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', np.float32),  # (F:06) 
		('누적거래량', np.uint64),  # (F:07) 
		('누적거래대금', np.uint64),  # (F:08) 
		('단위체결량', 'U12'),  # (F:09) 
		('시가', np.uint32),  # (F:10) 
		('고가', np.uint32),  # (F:11) 
		('저가', np.uint32),  # (F:12) 
		('시가시간', 'U6'),  # (F:13) 
		('고가시간', 'U6'),  # (F:14) 
		('저가시간', 'U6'),  # (F:15) 
		('매매구분', 'U1'),  # (F:16) 1:보통                 3:신고대량 5:장종료후시간외종가   6:장종료후시간외대량 7:장종료후시간외바스켓 8:장개시전시간외종가   9:장개시전시간외대량 A:장개시전시간외바스켓 B:장중바스켓           V:장중대량
		('장구분', 'U1'),  # (F:17) 1: 장중 5: 장종료후시간외종가  6: 장종료후시간외대량  7: 장종료후시간외바스켓  8: 장개시전시간외종가  9: 장개시전시간외대량  A: 장개시전시간외바스켓  B: 장중바스켓  V: 장중대량
		('호가체결구분', 'U1'),  # (F:18) 0:시초가 1:매도호가 2:매수호가
		('가중평균가', np.uint32),  # (F:19) 
		('매도1호가', np.uint32),  # (F:20) 
		('매수1호가', np.uint32),  # (F:21) 
		('거래강도', np.float32),  # (F:22) 
		('매매구분별거래량', np.uint64),  # (F:23) 17번 장구분별 거래량
		('체결강도', np.float32),  # (F:24) 
		('체결매도매수구분', 'U1'),  # (F:25) 
		])
	MULTI_OUTPUT_DTYPE = None

	def _set_input_data(self, code6) -> None:
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 0, code6)
	

class SH(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'SH', '현물 호가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])  # (F:00) 
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('호가접수시간', 'U6'),  # (F:02) 
		('장구분', 'U1'),  # (F:03) 
		('매도1호가', np.uint32),  # (F:04) 
		('매수1호가', np.uint32),  # (F:05) 
		('매도1호가수량', np.uint64),  # (F:06) 
		('매수1호가수량', np.uint64),  # (F:07) 
		('매도2호가', np.uint32),  # (F:08) 
		('매수2호가', np.uint32),  # (F:09) 
		('매도2호가수량', np.uint64),  # (F:10) 
		('매수2호가수량', np.uint64),  # (F:11) 
		('매도3호가', np.uint32),  # (F:12) 
		('매수3호가', np.uint32),  # (F:13) 
		('매도3호가수량', np.uint64),  # (F:14) 
		('매수3호가수량', np.uint64),  # (F:15) 
		('매도4호가', np.uint32),  # (F:16) 
		('매수4호가', np.uint32),  # (F:17) 
		('매도4호가수량', np.uint64),  # (F:18) 
		('매수4호가수량', np.uint64),  # (F:19) 
		('매도5호가', np.uint32),  # (F:20) 
		('매수5호가', np.uint32),  # (F:21) 
		('매도5호가수량', np.uint64),  # (F:22) 
		('매수5호가수량', np.uint64),  # (F:23) 
		('매도6호가', np.uint32),  # (F:24) 
		('매수6호가', np.uint32),  # (F:25) 
		('매도6호가수량', np.uint64),  # (F:26) 
		('매수6호가수량', np.uint64),  # (F:27) 
		('매도7호가', np.uint32),  # (F:28) 
		('매수7호가', np.uint32),  # (F:29) 
		('매도7호가수량', np.uint64),  # (F:30) 
		('매수7호가수량', np.uint64),  # (F:31) 
		('매도8호가', np.uint32),  # (F:32) 
		('매수8호가', np.uint32),  # (F:33) 
		('매도8호가수량', np.uint64),  # (F:34) 
		('매수8호가수량', np.uint64),  # (F:35) 
		('매도9호가', np.uint32),  # (F:36) 
		('매수9호가', np.uint32),  # (F:37) 
		('매도9호가수량', np.uint64),  # (F:38) 
		('매수9호가수량', np.uint64),  # (F:39) 
		('매도10호가', np.uint32),  # (F:40) 
		('매수10호가', np.uint32),  # (F:41) 
		('매도10호가수량', np.uint64),  # (F:42) 
		('매수10호가수량', np.uint64),  # (F:43) 
		('매도총호가수량', np.uint64),  # (F:44) 
		('매수총호가수량', np.uint64),  # (F:45) 
		('시간외매도호가수량', np.uint64),  # (F:46) 
		('시간외매수호가수량', np.uint64),  # (F:47) 
		('동시구분', 'U1'),  # (F:48) 1: 동시, 2: 동시 연장,  0: 접속
		('예상체결가격', np.uint32),  # (F:49) 
		('예상체결수량', np.uint64),  # (F:50) 
		])
	MULTI_OUTPUT_DTYPE = None

	def _set_input_data(self, code6) -> None:
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 0, code6)
	

class SK(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'SK', '현물 거래원'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('체결시간', 'U6'),  # (F:02) 
		('매도거래원번호1', 'U4'),  # (F:03) 
		('매수거래원번호1', 'U4'),  # (F:04) 
		('매도수량1', np.uint64),  # (F:05) 
		('매수수량1', np.uint64),  # (F:06) 
		('매도대금1', np.uint64),  # (F:07) 
		('매수대금1', np.uint64),  # (F:08) 
		('매도거래원번호2', 'U4'),  # (F:09) 
		('매수거래원번호2', 'U4'),  # (F:10) 
		('매도수량2', np.uint64),  # (F:11) 
		('매수수량2', np.uint64),  # (F:12) 
		('매도대금2', np.uint64),  # (F:13) 
		('매수대금2', np.uint64),  # (F:14) 
		('매도거래원번호3', 'U4'),  # (F:15) 
		('매수거래원번호3', 'U4'),  # (F:16) 
		('매도수량3', np.uint64),  # (F:17) 
		('매수수량3', np.uint64),  # (F:18) 
		('매도대금3', np.uint64),  # (F:19) 
		('매수대금3', np.uint64),  # (F:20) 
		('매도거래원번호4', 'U4'),  # (F:21) 
		('매수거래원번호4', 'U4'),  # (F:22) 
		('매도수량4', np.uint64),  # (F:23) 
		('매수수량4', np.uint64),  # (F:24) 
		('매도대금4', np.uint64),  # (F:25) 
		('매수대금4', np.uint64),  # (F:26) 
		('매도거래원번호5', 'U4'),  # (F:27) 
		('매수거래원번호5', 'U4'),  # (F:28) 
		('매도수량5', np.uint64),  # (F:29) 
		('매수수량5', np.uint64),  # (F:30) 
		('매도대금5', np.uint64),  # (F:31) 
		('매수대금5', np.uint64),  # (F:32) 
		('총매도수량', np.uint64),  # (F:33) 
		('총매수수량', np.uint64),  # (F:34) 
		('총매도대금', np.uint64),  # (F:35) 
		('총매수대금', np.uint64),  # (F:36) 
		('국내총매도수량', np.uint64),  # (F:37) 
		('국내총매수수량', np.uint64),  # (F:38) 
		('국내총매도대금', np.uint64),  # (F:39) 
		('국내총매수대금', np.uint64),  # (F:40) 
		('국내총순매수수량', np.uint64),  # (F:41) 
		('국내총순매수대금', np.uint64),  # (F:42) 
		('외국계총매도수량', np.uint64),  # (F:43) 
		('외국계총매수수량', np.uint64),  # (F:44) 
		('외국계총매도대금', np.uint64),  # (F:45) 
		('외국계총매수대금', np.uint64),  # (F:46) 
		('외국계순매수수량', np.uint64),  # (F:47) 
		('외국계순매수대금', np.uint64),  # (F:48) 
		('전체총매도수량', np.uint64),  # (F:49) 
		('전체총매수수량', np.uint64),  # (F:50) 
		('전체총매도대금', np.uint64),  # (F:51) 
		('전체총매수대금', np.uint64),  # (F:52) 
		('전체순매수수량', np.uint64),  # (F:53) 
		('전체순매수대금', np.uint64),  # (F:54) 
		('매도증가수량1', np.uint64),  # (F:55) 
		('매수증가수량1', np.uint64),  # (F:56) 
		('매도증가수량2', np.uint64),  # (F:57) 
		('매수증가수량2', np.uint64),  # (F:58) 
		('매도증가수량3', np.uint64),  # (F:59) 
		('매수증가수량3', np.uint64),  # (F:60) 
		('매도증가수량4', np.uint64),  # (F:61) 
		('매수증가수량4', np.uint64),  # (F:62) 
		('매도증가수량5', np.uint64),  # (F:63) 
		('매수증가수량5', np.uint64),  # (F:64) 
		])
	MULTI_OUTPUT_DTYPE = None


class EB(BaseTR):
	NAME, DESCRIPTION = 'EB', '현물 마스터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('시장구분', 'U1'),  # (F:02) 
		('일련번호', 'U4'),  # (F:03) 
		('입회일자', 'U8'),  # (F:04) 
		('한글종목명', 'U20'),  # (F:05) 
		('영문종목명', 'U20'),  # (F:06) 
		('기준가', np.uint32),  # (F:07) 
		('전일종가', np.uint32),  # (F:08) 
		('전일거래량', np.uint64),  # (F:09) 
		('전일거래대금', np.uint64),  # (F:10) 
		('정규시장거래량', np.uint64),  # (F:11) 
		('정규시장거래대금', np.uint64),  # (F:12) 
		('상한가', np.uint32),  # (F:13) 
		('하한가', np.uint32),  # (F:14) 
		])
	MULTI_OUTPUT_DTYPE = None


class EC(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'EC', '현물 시간외단일가 현재가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('체결시간', 'U6'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', np.float32),  # (F:06) 
		('정규장대비구분', 'U1'),  # (F:07) 
		('정규장대비', np.uint32),  # (F:08) 
		('정규장대비율', np.float32),  # (F:09) 
		('누적거래량', np.uint64),  # (F:10) 
		('누적거래대금', np.uint64),  # (F:11) 
		('단위체결량', 'U12'),  # (F:12) 
		('시가', np.uint32),  # (F:13) 
		('고가', np.uint32),  # (F:14) 
		('저가', np.uint32),  # (F:15) 
		('호가체결구분', 'U1'),  # (F:16) 
		('매도호가', np.uint32),  # (F:17) 
		('매수호가', np.uint32),  # (F:18) 
		])
	MULTI_OUTPUT_DTYPE = None


class EH(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'EH', '현물호가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('호가접수시간', 'U6'),  # (F:02) 
		('시간외단일가매매장구분', 'U1'),  # (F:03) 
		('매도1호가', np.uint32),  # (F:04) 
		('매수1호가', np.uint32),  # (F:05) 
		('매도1호가수량', np.uint64),  # (F:06) 
		('매수1호가수량', np.uint64),  # (F:07) 
		('매도2호가', np.uint32),  # (F:08) 
		('매수2호가', np.uint32),  # (F:09) 
		('매도2호가수량', np.uint64),  # (F:10) 
		('매수2호가수량', np.uint64),  # (F:11) 
		('매도3호가', np.uint32),  # (F:12) 
		('매수3호가', np.uint32),  # (F:13) 
		('매도3호가수량', np.uint64),  # (F:14) 
		('매수3호가수량', np.uint64),  # (F:15) 
		('매도4호가', np.uint32),  # (F:16) 
		('매수4호가', np.uint32),  # (F:17) 
		('매도4호가수량', np.uint64),  # (F:18) 
		('매수4호가수량', np.uint64),  # (F:19) 
		('매도5호가', np.uint32),  # (F:20) 
		('매수5호가', np.uint32),  # (F:21) 
		('매도5호가수량', np.uint64),  # (F:22) 
		('매수5호가수량', np.uint64),  # (F:23) 
		('매도6호가', np.uint32),  # (F:24) 
		('매수6호가', np.uint32),  # (F:25) 
		('매도6호가수량', np.uint64),  # (F:26) 
		('매수6호가수량', np.uint64),  # (F:27) 
		('매도7호가', np.uint32),  # (F:28) 
		('매수7호가', np.uint32),  # (F:29) 
		('매도7호가수량', np.uint64),  # (F:30) 
		('매수7호가수량', np.uint64),  # (F:31) 
		('매도8호가', np.uint32),  # (F:32) 
		('매수8호가', np.uint32),  # (F:33) 
		('매도8호가수량', np.uint64),  # (F:34) 
		('매수8호가수량', np.uint64),  # (F:35) 
		('매도9호가', np.uint32),  # (F:36) 
		('매수9호가', np.uint32),  # (F:37) 
		('매도9호가수량', np.uint64),  # (F:38) 
		('매수9호가수량', np.uint64),  # (F:39) 
		('매도10호가', np.uint32),  # (F:40) 
		('매수10호가', np.uint32),  # (F:41) 
		('매도10호가수량', np.uint64),  # (F:42) 
		('매수10호가수량', np.uint64),  # (F:43) 
		('매도총호가수량', np.uint64),  # (F:44) 
		('매수총호가수량', np.uint64),  # (F:45) 
		('동시구분', 'U1'),  # (F:46) 
		('예상체결가격', np.uint32),  # (F:47) 
		('예상체결수량', np.uint64),  # (F:48) 
		])
	MULTI_OUTPUT_DTYPE = None


class SY(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'SY', '현물 종목상태정보 (VI)'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('장구분', 'U1'),  # (F:02) 
		('매매체결처리시각', 'U9'),  # (F:03) 
		('VI해제시각', 'U9'),  # (F:04) 
		('VI적용구분코드', 'U1'),  # (F:05) 1: 발동, 2: 해제
		('VI종류코드', 'U1'),  # (F:06) 1: 정적vi, 2:동적vi
		('정적VI 발동기준가격', 'U9'),  # (F:07) 
		('VI발동가격', "U9"),  # (F:08) 
		('정적VI 발동괴리율', 'U14'),  # (F:09) 
		('동적VI 발동기준가격', 'U9'),  # (F:10) 
		('동적VI 발동괴리율', 'U14'),  # (F:11) 
		])
	MULTI_OUTPUT_DTYPE = None


class SJ(BaseTR):
	NAME, DESCRIPTION = 'SJ', '현물 마스터–기타'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('장구분', 'U1'),  # (F:01) 
		('KRX섹터지수소비자유통여부', 'U1'),  # (F:02) 
		('KRX섹터지수레저엔터테인먼트여부', 'U1'),  # (F:03) 
		('SRI환경책임투자지수', 'U1'),  # (F:04) 
		('녹색산업지수여부', 'U1'),  # (F:05) 
		('투자주의환기종목여부', 'U1'),  # (F:06) 
		('유:지배구조지수종목여부', 'U1'),  # (F:07) 
		('매입인도기준가', np.uint32),  # (F:08) 
		('매입인도상한가', np.uint32),  # (F:09) 
		('매입인도하한가', np.uint32),  # (F:10) 
		('일반매입인도실행수량', np.uint64),  # (F:11) 
		('당일매입인도실행수량', np.uint64),  # (F:12) 
		('과세유형코드', 'U1'),  # (F:13) 
		('SRI지배구조책임투자지수종목여부', 'U1'),  # (F:14) 
		('단기과열종목코드', 'U1'),  # (F:15) 2: 지정, 3: 지정연장
		('ETF복제방법구분코드', 'U1'),  # (F:16) 
		('ETF상품유형코드', 'U1'),  # (F:17) 
		('K200고배당지수여부', 'U1'),  # (F:18) 
		('K200저변동성지지수여부', 'U1'),  # (F:19) 
		('만기일자', 'U8'),  # (F:20) 
		('ETN상품분류코드', 'U3'),  # (F:21) 
		('분배금형태코드', 'U2'),  # (F:22) 
		('만기상환가격결정시작일자', 'U8'),  # (F:23) 
		('만기상환가격결정종료일자', 'U8'),  # (F:24) 
		('외국주권액면가', np.uint32),  # (F:25) 
		('ETP상품구분코드', 'U1'),  # (F:26) 
		('지수산출기관코드', 'U1'),  # (F:27) 
		('지수시장분류ID', 'U6'),  # (F:28) 
		('지수일련번호', 'U3'),  # (F:29) 
		('추적지수레버리지인버스구분코드', 'U2'),  # (F:30) 
		('참고지수레버리지인버스구분코드', 'U2'),  # (F:31) 
		('지수자산분류코드1', 'U6'),  # (F:32) 
		('지수자산분류코드2', 'U6'),  # (F:33) 
		('LP주문가능여부', 'U1'),  # (F:34) 
		('KOSDAQ150지수종목여부', 'U1'),  # (F:35) 
		('저유동성여부', 'U1'),  # (F:36) 
		('이상급등여부', 'U1'),  # (F:37) 
		('KRX300지수여부', 'U1'),  # (F:38) 
		('상한수량', np.uint64),  # (F:39) 
		('상장주식수부족종목여부', 'U1'),  # (F:40) 
		])
	MULTI_OUTPUT_DTYPE = None


class FB(BaseTR):
	NAME, DESCRIPTION = 'FB', '선물 마스터'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('일련번호', 'U4'),  # (F:02) 
		('입회일자', 'U8'),  # (F:03) 
		('한글종목명', 'U30'),  # (F:04) 
		('영문종목명', 'U30'),  # (F:05) 
		('축약종목명', 'U15'),  # (F:06) 
		('종목보조코드', 'U6'),  # (F:07) 
		('상장일', 'U8'),  # (F:08) 
		('최초거래일', 'U8'),  # (F:09) 
		('최종거래일', 'U8'),  # (F:10) 
		('기준일수', 'U3'),  # (F:11) 
		('잔존일수', 'U3'),  # (F:12) 
		('CD금리', np.float32),  # (F:13) 
		('배당지수미래가치', np.float32),  # (F:14) 
		('기준가', np.float32),  # (F:15) 
		('기준가구분', 'U1'),  # (F:16) 
		('상한가', np.float32),  # (F:17) 
		('하한가', np.float32),  # (F:18) 
		('CB적용상한가', np.float32),  # (F:19) 
		('CB적용하한가', np.float32),  # (F:20) 
		('전일정산가', np.float32),  # (F:21) 
		('전일정산가구분', 'U1'),  # (F:22) 
		('전일종가', np.float32),  # (F:23) 
		('전일종가구분', 'U1'),  # (F:24) 
		('전일거래량', np.uint64),  # (F:25) 
		('전일거래대금', np.uint64),  # (F:26) 
		('전일미결제약정수량', 'U8'),  # (F:27) 
		('상장중최고일자', 'U8'),  # (F:28) 
		('상장중최고가', np.float32),  # (F:29) 
		('상장중최저일자', 'U8'),  # (F:30) 
		('상장중최저가', np.float32),  # (F:31) 
		('시장가허용구분', 'U1'),  # (F:32) 
		('조건부지정가허용구분', 'U1'),  # (F:33) 
		('최유리지정가허용구분', 'U1'),  # (F:34) 
		('최종매매시간', 'U8'),  # (F:35) 
		('스프레드근월물표준코드', 'U12'),  # (F:36) 
		('전일근월물종가', np.float32),  # (F:37) 
		('전일근월물체결수량', 'U8'),  # (F:38) 
		('전일근월물체결대금', 'U12'),  # (F:39) 
		('스프레드원월물표준코드', 'U12'),  # (F:40) 
		('전일원월물종가', np.float32),  # (F:41) 
		('전일원월물체결수량', 'U8'),  # (F:42) 
		('전일원월물체결대금', 'U12'),  # (F:43) 
		('장구분', 'U2'),  # (F:44) 
		('거래단위', 'U8'),  # (F:45) 
		('실시간가격제한여부', 'U1'),  # (F:46) Y:실시간 가격제한, N:제한없슴
		('실시간상한가간격', 'U6'),  # (F:47) Ex) 2.65
		('실시간하한가간격', 'U6'),  # (F:48) Ex) 2.65
		('기초자산ID', 'U3'),  # (F:49) 
		('가격제한확대적용방향코드', 'U1'),  # (F:50) 
		('가격제한최종단계', 'U3'),  # (F:51) 
		('가격제한1단계상한가', 'U6'),  # (F:52) 
		('가격제한1단계하한가', 'U6'),  # (F:53) 
		('가격제한2단계상한가', 'U6'),  # (F:54) 
		('가격제한2단계하한가', 'U6'),  # (F:55) 
		('가격제한3단계상한가', 'U6'),  # (F:56) 
		('가격제한3단계하한가', 'U6'),  # (F:57) 
		])
	MULTI_OUTPUT_DTYPE = None


class FC(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'FC', '선물 현재가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('일련번호', 'U6'),  # (F:03) 
		('현재가', np.float32),  # (F:04) 
		('전일대비구분', 'U1'),  # (F:05) 
		('전일대비', np.float32),  # (F:06) 
		('전일대비율', np.float32),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('누적거래대금', np.uint64),  # (F:09) 
		('단위체결량', 'U8'),  # (F:10) 
		('미결제약정수량', 'U8'),  # (F:11) 
		('시가', np.float32),  # (F:12) 
		('고가', np.float32),  # (F:13) 
		('저가', np.float32),  # (F:14) 
		('시가시간', 'U6'),  # (F:15) 
		('고가시간', 'U6'),  # (F:16) 
		('저가시간', 'U6'),  # (F:17) 
		('매도호가', np.float32),  # (F:18) 
		('매수호가', np.float32),  # (F:19) 
		('호가체결구분', 'U1'),  # (F:20) 
		('근월물의약정가', np.float32),  # (F:21) 
		('근월물체결수량', 'U8'),  # (F:22) 
		('근월물거래대금', np.uint64),  # (F:23) 
		('원월물의약정가', np.float32),  # (F:24) 
		('원월물체결수량', 'U8'),  # (F:25) 
		('원월물거래대금', np.uint64),  # (F:26) 
		('매도체결합', 'U8'),  # (F:27) 
		('매수체결합', 'U8'),  # (F:28) 
		('체결강도', 'U6'),  # (F:29) 
		('협의대량누적체결수량', 'U8'),  # (F:30) 
		('실시간상한가', 'U6'),  # (F:31) 
		('실시간하한가', 'U6'),  # (F:32) 
		])
	MULTI_OUTPUT_DTYPE = None


class FL(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'FL', '선물민감도'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('이론가', np.float32),  # (F:03) 
		('델타', np.float32),  # (F:04) 
		('감마', np.float32),  # (F:05) 
		('베가', np.float32),  # (F:06) 
		('로', np.float32),  # (F:07) 
		('세타', np.float32),  # (F:08) 
		])
	MULTI_OUTPUT_DTYPE = None


class FH(BaseTR):
	NAME, DESCRIPTION = 'FH', '선물 호가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('호가접수시간', 'U8'),  # (F:02) 
		('매도1호가', np.float32),  # (F:03) 
		('매수1호가', np.float32),  # (F:04) 
		('매도1호가수량', 'U8'),  # (F:05) 
		('매수1호가수량', 'U8'),  # (F:06) 
		('매도1호가건수', 'U5'),  # (F:07) 
		('매수1호가건수', 'U5'),  # (F:08) 
		('매도2호가', np.float32),  # (F:09) 
		('매수2호가', np.float32),  # (F:10) 
		('매도2호가수량', 'U8'),  # (F:11) 
		('매수2호가수량', 'U8'),  # (F:12) 
		('매도2호가건수', 'U5'),  # (F:13) 
		('매수2호가건수', 'U5'),  # (F:14) 
		('매도3호가', np.float32),  # (F:15) 
		('매수3호가', np.float32),  # (F:16) 
		('매도3호가수량', 'U8'),  # (F:17) 
		('매수3호가수량', 'U8'),  # (F:18) 
		('매도3호가건수', 'U5'),  # (F:19) 
		('매수3호가건수', 'U5'),  # (F:20) 
		('매도4호가', np.float32),  # (F:21) 
		('매수4호가', np.float32),  # (F:22) 
		('매도4호가수량', 'U8'),  # (F:23) 
		('매수4호가수량', 'U8'),  # (F:24) 
		('매도4호가건수', 'U5'),  # (F:25) 
		('매수4호가건수', 'U5'),  # (F:26) 
		('매도5호가', np.float32),  # (F:27) 
		('매수5호가', np.float32),  # (F:28) 
		('매도5호가수량', 'U8'),  # (F:29) 
		('매수5호가수량', 'U8'),  # (F:30) 
		('매도5호가건수', 'U5'),  # (F:31) 
		('매수5호가건수', 'U5'),  # (F:32) 
		('매도총호가수량', 'U8'),  # (F:33) 
		('매수총호가수량', 'U8'),  # (F:34) 
		('매도총호가건수', 'U5'),  # (F:35) 
		('매수총호가건수', 'U5'),  # (F:36) 
		('장상태구분코드', 'U2'),  # (F:37) 00 : 초기(장개시전)    10 : 시가단일가 11 : 시가단일가연장    20 : 장중단일가 21 : 장중단일가연장    30 : 종가단일가 40 : 접속  80 : 단위매매체결(주식관련상품) 90 : 거래정지           99 : 장종료
		('예상체결가격', 'U6'),  # (F:38) 
		])
	MULTI_OUTPUT_DTYPE = None


class TR_FCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_FCHART', '선물 분/일 데이터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U5'),  # (F:00) 
		('그래프종류', 'U1'),  # (F:01) 1:분데이터 		D:일데이터
		('시간간격', 'U3'),  # (F:02) 분데이터일 경우 1 – 5 일데이터일 경우 1
		('시작일', 'U8'),  # (F:03) YYYYMMDD 분 데이터 요청시 : “00000000”
		('종료일', 'U8'),  # (F:04) YYYYMMDD 분 데이터 요청시 : “99999999”
		('조회갯수', 'U4'),  # (F:05) 1 – 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('체결시간', 'U6'),  # (F:01) 
		('시가', np.float32),  # (F:02) 
		('고가', np.float32),  # (F:03) 
		('저가', np.float32),  # (F:04) 
		('종가', np.float32),  # (F:05) 
		('미결제약정수량', np.float32),  # (F:06) 
		('이론가', np.float32),  # (F:07) 
		('기초자산지수', np.float32),  # (F:08) 
		('단위거래량', np.uint64),  # (F:09) 
		('단위거래대금', np.uint64),  # (F:10) 
		])


class TR_FNCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_FNCHART', '연결선물 분/일 데이터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U5'),  # (F:00) 
		('그래프종류', 'U1'),  # (F:01) 1:분데이터 		D:일데이터
		('시간간격', 'U3'),  # (F:02) 분데이터일 경우 1 – 5 일데이터일 경우 1
		('시작일', 'U8'),  # (F:03) YYYYMMDD 분 데이터 요청시 : “00000000”
		('종료일', 'U8'),  # (F:04) YYYYMMDD 분 데이터 요청시 : “99999999”
		('조회갯수', 'U4'),  # (F:05) 1 – 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('체결시간', 'U6'),  # (F:01) 
		('시가', np.float32),  # (F:02) 
		('고가', np.float32),  # (F:03) 
		('저가', np.float32),  # (F:04) 
		('종가', np.float32),  # (F:05) 
		('미결제약정수량', np.float32),  # (F:06) 
		('이론가', np.float32),  # (F:07) 
		('기초자산지수', np.float32),  # (F:08) 
		('단위거래량', np.uint64),  # (F:09) 
		('단위거래대금', np.uint64),  # (F:10) 
		])


class FU(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'FU', '선물 기타(정산가)'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('미결제약정수량', np.uint32),  # (F:02) 
		('정산가', np.float32),  # (F:03) 
		('정산가 구분', 'U1'),  # (F:04) 0 : 정산가 없슴(최초 거래성립전 기세 포함) 1 : 당일 종가(실세) 4 : 당일 이론가(최초 거래성립후 종가 미형성) 7 : 대상자산 종가(이론가없는상품) 8 : 정산기준가격
		])
	MULTI_OUTPUT_DTYPE = None


class FI(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'FI', '지수선물 가격제한폭 확대'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('상한시간', 'U8'),  # (F:02) 
		('하한시간', 'U8'),  # (F:03) 
		('가격제한확대상하단계', 'U2'),  # (F:04) 
		('가격제한확대하한단계', 'U2'),  # (F:05) 
		('상한가', np.float32),  # (F:06) 
		('하한가', np.float32),  # (F:07) 
		('가격제한확대적용방향코드', 'U1'),  # (F:08) U: 상승, D: 하락, B:양방향
		])
	MULTI_OUTPUT_DTYPE = None


class QB(BaseTR):
	NAME, DESCRIPTION = 'QB', '옵션 마스터'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('일련번호', 'U4'),  # (F:02) 
		('조회일련번호', 'U4'),  # (F:03) 
		('입회일자', 'U8'),  # (F:04) 
		('한글종목명', 'U30'),  # (F:05) 
		('영문종목명', 'U30'),  # (F:06) 
		('축약종목명', 'U15'),  # (F:07) 
		('옵션종류', 'U1'),  # (F:08) 
		('거래대상물', 'U2'),  # (F:09) 
		('만기년월', 'U6'),  # (F:10) 
		('행사가격', np.float32),  # (F:11) 
		('권리행사유형구분', 'U1'),  # (F:12) 
		('최근월물구분', 'U1'),  # (F:13) 
		('ATM구분', 'U1'),  # (F:14) 
		('매매구분', 'U1'),  # (F:15) 
		('매매구분지정일', 'U8'),  # (F:16) 
		('상장일', 'U8'),  # (F:17) 
		('최초거래일', 'U8'),  # (F:18) 
		('최종거래일', 'U8'),  # (F:19) 
		('기준일수', 'U3'),  # (F:20) 
		('잔존일수', 'U3'),  # (F:21) 
		('CD금리', np.float32),  # (F:22) 
		('배당지수현재가치', np.float32),  # (F:23) 
		('기준가', np.float32),  # (F:24) 
		('기준가구분', 'U1'),  # (F:25) 
		('매매증거금기준가', np.float32),  # (F:26) 
		('매매증거금기준가구분', 'U1'),  # (F:27) 
		('정상호가범위상한치', np.float32),  # (F:28) 
		('정상호가범위하한치', np.float32),  # (F:29) 
		('전일종가', np.float32),  # (F:30) 
		('전일종가구분', 'U1'),  # (F:31) 
		('전일거래량', np.uint64),  # (F:32) 
		('전일거래대금', np.uint64),  # (F:33) 
		('전일미결제약정수량', 'U8'),  # (F:34) 
		('상장중최고일자', 'U8'),  # (F:35) 
		('상장중최고가', np.float32),  # (F:36) 
		('상장중최저일자', 'U8'),  # (F:37) 
		('상장중최저가', np.float32),  # (F:38) 
		('시장가허용구분', 'U1'),  # (F:39) 
		('조건부지정가허용구분', 'U1'),  # (F:40) 
		('최유리지정가허용구분', 'U1'),  # (F:41) 
		('역사적변동성', np.float32),  # (F:42) 
		('장구분', 'U2'),  # (F:43) 
		('거래단위', 'U8'),  # (F:44) 
		('실시간가격제한여부', 'U1'),  # (F:45) Y:실시간 가격제한, N:제한없슴
		('실시간상한가간격', 'U6'),  # (F:46) Ex) 0.55
		('실시간하한가간격', 'U6'),  # (F:47) Ex) 0.55
		('가격제한확대적용방향코드', 'U1'),  # (F:48) 
		('가격제한최종단계', 'U3'),  # (F:49) 
		('가격제한1단계상한가', 'U6'),  # (F:50) 
		('가격제한1단계하한가', 'U6'),  # (F:51) 
		('가격제한2단계상한가', 'U6'),  # (F:52) 
		('가격제한2단계하한가', 'U6'),  # (F:53) 
		('가격제한3단계상한가', 'U6'),  # (F:54) 
		('가격제한3단계하한가', 'U6'),  # (F:55) 
		])
	MULTI_OUTPUT_DTYPE = None


class QC(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'QC', '옵션 현재가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('일련번호', 'U6'),  # (F:03) 
		('현재가', np.float32),  # (F:04) 
		('전일대비구분', 'U1'),  # (F:05) 
		('전일대비', np.float32),  # (F:06) 
		('전일대비율', np.float32),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('누적거래대금', np.uint64),  # (F:09) 
		('단위체결량', 'U8'),  # (F:10) 
		('미결제약정수량', 'U8'),  # (F:11) 
		('시가', np.float32),  # (F:12) 
		('고가', np.float32),  # (F:13) 
		('저가', np.float32),  # (F:14) 
		('시가시간', 'U6'),  # (F:15) 
		('고가시간', 'U6'),  # (F:16) 
		('저가시간', 'U6'),  # (F:17) 
		('호가체결구분', 'U1'),  # (F:18) 
		('매도호가', np.float32),  # (F:19) 
		('매수호가', np.float32),  # (F:20) 
		('협의대량누적체결수량', 'U8'),  # (F:21) 
		('실시간상한가', 'U6'),  # (F:22) 
		('실시간하한가', 'U6'),  # (F:23) 
		])
	MULTI_OUTPUT_DTYPE = None


class QL(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'QL', '옵션 민감도'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('이론가', np.float32),  # (F:03) 
		('내재변동성', np.float32),  # (F:04) 
		('델타', np.float32),  # (F:05) 
		('감마', np.float32),  # (F:06) 
		('베가', np.float32),  # (F:07) 
		('로', np.float32),  # (F:08) 
		('세타', np.float32),  # (F:09) 
		])
	MULTI_OUTPUT_DTYPE = None


class QH(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'QH', '옵션 호가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('호가접수시간', 'U8'),  # (F:02) 
		('매도1호가', np.float32),  # (F:03) 
		('매수1호가', np.float32),  # (F:04) 
		('매도1호가수량', np.uint32),  # (F:05) 
		('매수1호가수량', np.uint32),  # (F:06) 
		('매도1호가건수', np.uint32),  # (F:07) 
		('매수1호가건수', np.uint32),  # (F:08) 
		('매도2호가', np.float32),  # (F:09) 
		('매수2호가', np.float32),  # (F:10) 
		('매도2호가수량', np.uint32),  # (F:11) 
		('매수2호가수량', np.uint32),  # (F:12) 
		('매도2호가건수', np.uint32),  # (F:13) 
		('매수2호가건수', np.uint32),  # (F:14) 
		('매도3호가', np.float32),  # (F:15) 
		('매수3호가', np.float32),  # (F:16) 
		('매도3호가수량', np.uint32),  # (F:17) 
		('매수3호가수량', np.uint32),  # (F:18) 
		('매도3호가건수', np.uint32),  # (F:19) 
		('매수3호가건수', np.uint32),  # (F:20) 
		('매도4호가', np.float32),  # (F:21) 
		('매수4호가', np.float32),  # (F:22) 
		('매도4호가수량', np.uint32),  # (F:23) 
		('매수4호가수량', np.uint32),  # (F:24) 
		('매도4호가건수', np.uint32),  # (F:25) 
		('매수4호가건수', np.uint32),  # (F:26) 
		('매도5호가', np.float32),  # (F:27) 
		('매수5호가', np.float32),  # (F:28) 
		('매도5호가수량', np.uint32),  # (F:29) 
		('매수5호가수량', np.uint32),  # (F:30) 
		('매도5호가건수', np.uint32),  # (F:31) 
		('매수5호가건수', np.uint32),  # (F:32) 
		('매도총호가수량', np.uint32),  # (F:33) 
		('매수총호가수량', np.uint32),  # (F:34) 
		('매도총호가건수', np.uint32),  # (F:35) 
		('매수총호가건수', np.uint32),  # (F:36) 
		('장상태구분코드', 'U2'),  # (F:37) 00 : 초기(장개시전)    10 : 시가단일가 11 : 시가단일가연장    20 : 장중단일가 21 : 장중단일가연장    30 : 종가단일가 40 : 접속  80 : 단위매매체결(주식관련상품) 90 : 거래정지           99 : 장종료
		('예상체결가격', np.float32),  # (F:38) 
		])
	MULTI_OUTPUT_DTYPE = None


class QI(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'QI', '지수옵션 가격제한폭 확대'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('상한시간', 'U8'),  # (F:02) 
		('하한시간', 'U8'),  # (F:03) 
		('가격제한확대상한단계', 'U2'),  # (F:04) 
		('가격제한확대하한단계', 'U2'),  # (F:05) 
		('상한가', np.float32),  # (F:06) 
		('하한가', np.float32),  # (F:07) 
		('가격제한확대적용방향코드', 'U1'),  # (F:08) U: 상승, D: 하락, B:양방향
		])
	MULTI_OUTPUT_DTYPE = None


class TR_OCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_OCHART', '옵션 분/일 데이터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U8'),  # (F:00) 
		('그래프종류', 'U1'),  # (F:01) 1:분데이터 		D:일데이터
		('시간간격', 'U3'),  # (F:02) 분데이터일 경우 1 – 30 일데이터일 경우 1
		('시작일', 'U8'),  # (F:03) YYYYMMDD 분 데이터 요청시 : “00000000”
		('종료일', 'U8'),  # (F:04) YYYYMMDD 분 데이터 요청시 : “99999999”
		('조회갯수', 'U4'),  # (F:05) 1 – 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('시간', 'U6'),  # (F:01) 
		('시가', np.float32),  # (F:02) 
		('고가', np.float32),  # (F:03) 
		('저가', np.float32),  # (F:04) 
		('종가', np.float32),  # (F:05) 
		('미결제약정수량', np.float32),  # (F:06) 
		('이론가', np.float32),  # (F:07) 
		('기초자산지수', np.float32),  # (F:08) 
		('단위거래량', np.uint64),  # (F:09) 
		('단위거래대금', np.uint64),  # (F:10) 
		])


class WB(BaseTR):
	NAME, DESCRIPTION = 'WB', 'ELW 마스터'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('장구분', 'U1'),  # (F:02) 
		('일련번호', 'U8'),  # (F:03) 
		('입회일자', 'U8'),  # (F:04) 
		('한글종목명', 'U40'),  # (F:05) 
		('영문종목명', 'U40'),  # (F:06) 
		('상장주식수', 'U12'),  # (F:07) 
		('액면가', np.uint32),  # (F:08) 
		('전일종가', np.uint32),  # (F:09) 
		('전일거래량', np.uint64),  # (F:10) 
		('전일거래대금', np.uint64),  # (F:11) 
		('기준가', np.uint32),  # (F:12) 
		('상한가', np.uint32),  # (F:13) 
		('하한가', np.uint32),  # (F:14) 
		('대용가', np.uint32),  # (F:15) 
		('거래정지구분', 'U1'),  # (F:16) 
		('락구분', 'U2'),  # (F:17) 00:발생안함, 01:권리락, 02:배당락, 03:분배락, 04:권배락, 05:중간배당락, 06:권리중간배당락, 99:기타 ※미해당의 경우 SPACE
		('평가가격', np.uint32),  # (F:18) 
		('최고호가가격', np.uint32),  # (F:19) 
		('최저호가가격', np.uint32),  # (F:20) 
		('정리매매시작일', 'U8'),  # (F:21) 
		('정리매매종료일', 'U8'),  # (F:22) 
		('매매수량단위', 'U5'),  # (F:23) 
		('자본금', np.uint64),  # (F:24) 
		('역사적변동성', np.float32),  # (F:25) 
		('ELW LP-회원번호-1', 'U5'),  # (F:26) *7.3절의 거래원번호 참조
		('ELW LP-회원번호-2', 'U5'),  # (F:27) 
		('ELW LP-회원번호-3', 'U5'),  # (F:28) 
		('ELW LP-회원번호-4', 'U5'),  # (F:29) 
		('ELW LP-회원번호-5', 'U5'),  # (F:30) 
		('ELW 스프레드', np.float32),  # (F:31) 
		('ELW 한글발행기관명', 'U40'),  # (F:32) 
		('ELW 영문발행기관명', 'U40'),  # (F:33) 
		('ELW발행시장참가자구분', 'U5'),  # (F:34) 
		('ELW 기초자산1', 'U12'),  # (F:35) 표준코드
		('ELW 기초자산2', 'U12'),  # (F:36) 표준코드
		('ELW 기초자산3', 'U12'),  # (F:37) 표준코드
		('ELW 기초자산4', 'U12'),  # (F:38) 표준코드
		('ELW 기초자산5', 'U12'),  # (F:39) 표준코드
		('ELW 기초자산구성비율1', np.float32),  # (F:40) 
		('ELW 기초자산구성비율2', np.float32),  # (F:41) 
		('ELW 기초자산구성비율3', np.float32),  # (F:42) 
		('ELW 기초자산구성비율4', np.float32),  # (F:43) 
		('ELW 기초자산구성비율5', np.float32),  # (F:44) 
		('ELW 기초가격', np.float32),  # (F:45) 
		('ELW 행사가격', np.float32),  # (F:46) 
		('ELW 권리유형', 'U2'),  # (F:47) 
		('ELW 권리행사방식', 'U2'),  # (F:48) 
		('ELW 결제방법', 'U2'),  # (F:49) 
		('ELW 최종거래일', 'U8'),  # (F:50) 
		('ELW 전환비율', np.float32),  # (F:51) 
		('ELW 가격상승참여율', np.float32),  # (F:52) 
		('ELW 보상율', np.float32),  # (F:53) 
		('ELW 지급일', 'U8'),  # (F:54) 
		('ELW 지급대리인', 'U40'),  # (F:55) 
		('ELW 투자지표 산출여부', 'U2'),  # (F:56) 
		('ELW LP주문가능여부', 'U2'),  # (F:57) 
		('ELW 상장일', 'U8'),  # (F:58) 
		('CD금리', np.float32),  # (F:59) 
		('배당지수현재가치', np.float32),  # (F:60) 
		('LP명', 'U20'),  # (F:61) 
		('LP거래량', np.uint64),  # (F:62) 
		('잔존일수', 'U3'),  # (F:63) 
		('LP거래만기일', 'U8'),  # (F:64) 
		('확정지급액', 'U13'),  # (F:65) 
		('ELW기초자산시장구분', 'U1'),  # (F:66) 1:유가증권, 2:코스닥, 3:섹터, 4:GICS, 8:MF(매경), 9:해외
		])
	MULTI_OUTPUT_DTYPE = None


class WC(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'WC', 'ELW 현재가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', np.float32),  # (F:06) 
		('누적거래량', np.uint64),  # (F:07) 
		('누적거래대금', np.uint64),  # (F:08) 
		('단위체결량', 'U12'),  # (F:09) 
		('시가', np.uint32),  # (F:10) 
		('고가', np.uint32),  # (F:11) 
		('저가', np.uint32),  # (F:12) 
		('시가시간', 'U6'),  # (F:13) 
		('고가시간', 'U6'),  # (F:14) 
		('저가시간', 'U6'),  # (F:15) 
		('매매구분', 'U1'),  # (F:16) 
		('호가체결구분', 'U1'),  # (F:17) 
		('매도1호가', np.uint32),  # (F:18) 
		('매수1호가', np.uint32),  # (F:19) 
		('상한가', np.uint32),  # (F:20) 
		('하한가', np.uint32),  # (F:21) 
		('LP보유수량', 'U16'),  # (F:22) 
		])
	MULTI_OUTPUT_DTYPE = None


class WH(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'WH', 'ELW 호가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('호가접수시간', 'U6'),  # (F:02) 
		('장구분', 'U1'),  # (F:03) 
		('매도1호가', np.uint32),  # (F:04) 
		('매수1호가', np.uint32),  # (F:05) 
		('매도1호가수량', np.uint64),  # (F:06) 
		('매수1호가수량', np.uint64),  # (F:07) 
		('LP매도1호가수량', np.uint64),  # (F:08) 
		('LP매수1호가수량', np.uint64),  # (F:09) 
		('매도2호가', np.uint32),  # (F:10) 
		('매수2호가', np.uint32),  # (F:11) 
		('매도2호가수량', np.uint64),  # (F:12) 
		('매수2호가수량', np.uint64),  # (F:13) 
		('LP매도2호가수량', np.uint64),  # (F:14) 
		('LP매수2호가수량', np.uint64),  # (F:15) 
		('매도3호가', np.uint32),  # (F:16) 
		('매수3호가', np.uint32),  # (F:17) 
		('매도3호가수량', np.uint64),  # (F:18) 
		('매수3호가수량', np.uint64),  # (F:19) 
		('LP매도3호가수량', np.uint64),  # (F:20) 
		('LP매수3호가수량', np.uint64),  # (F:21) 
		('매도4호가', np.uint32),  # (F:22) 
		('매수4호가', np.uint32),  # (F:23) 
		('매도4호가수량', np.uint64),  # (F:24) 
		('매수4호가수량', np.uint64),  # (F:25) 
		('LP매도4호가수량', np.uint64),  # (F:26) 
		('LP매수4호가수량', np.uint64),  # (F:27) 
		('매도5호가', np.uint32),  # (F:28) 
		('매수5호가', np.uint32),  # (F:29) 
		('매도5호가수량', np.uint64),  # (F:30) 
		('매수5호가수량', np.uint64),  # (F:31) 
		('LP매도5호가수량', np.uint64),  # (F:32) 
		('LP매수5호가수량', np.uint64),  # (F:33) 
		('매도6호가', np.uint32),  # (F:34) 
		('매수6호가', np.uint32),  # (F:35) 
		('매도6호가수량', np.uint64),  # (F:36) 
		('매수6호가수량', np.uint64),  # (F:37) 
		('LP매도6호가수량', np.uint64),  # (F:38) 
		('LP매수6호가수량', np.uint64),  # (F:39) 
		('매도7호가', np.uint32),  # (F:40) 
		('매수7호가', np.uint32),  # (F:41) 
		('매도7호가수량', np.uint64),  # (F:42) 
		('매수7호가수량', np.uint64),  # (F:43) 
		('LP매도7호가수량', np.uint64),  # (F:44) 
		('LP매수7호가수량', np.uint64),  # (F:45) 
		('매도8호가', np.uint32),  # (F:46) 
		('매수8호가', np.uint32),  # (F:47) 
		('매도8호가수량', np.uint64),  # (F:48) 
		('매수8호가수량', np.uint64),  # (F:49) 
		('LP매도8호가수량', np.uint64),  # (F:50) 
		('LP매수8호가수량', np.uint64),  # (F:51) 
		('매도9호가', np.uint32),  # (F:52) 
		('매수9호가', np.uint32),  # (F:53) 
		('매도9호가수량', np.uint64),  # (F:54) 
		('매수9호가수량', np.uint64),  # (F:55) 
		('LP매도9호가수량', np.uint64),  # (F:56) 
		('LP매수9호가수량', np.uint64),  # (F:57) 
		('매도10호가', np.uint32),  # (F:58) 
		('매수10호가', np.uint32),  # (F:59) 
		('매도10호가수량', np.uint64),  # (F:60) 
		('매수10호가수량', np.uint64),  # (F:61) 
		('LP매도10호가수량', np.uint64),  # (F:62) 
		('LP매수10호가수량', np.uint64),  # (F:63) 
		('매도총호가수량', np.uint64),  # (F:64) 
		('매수총호가수량', np.uint64),  # (F:65) 
		('LP매도총호가수량', np.uint64),  # (F:66) 
		('LP매수총호가수량', np.uint64),  # (F:67) 
		('시간외매도호가수량', np.uint64),  # (F:68) 
		('시간외매수호가수량', np.uint64),  # (F:69) 
		('동시구분', 'U1'),  # (F:70) 
		('예상체결가격', np.uint32),  # (F:71) 
		('예상체결수량', np.uint64),  # (F:72) 
		])
	MULTI_OUTPUT_DTYPE = None


class WK(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'WK', 'ELW 거래원'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('체결시간', 'U6'),  # (F:02) 
		('매도거래원번호1', 'U4'),  # (F:03) *6.3절 거래원번호 참조
		('매수거래원번호1', 'U4'),  # (F:04) 
		('총매도수량1', np.uint64),  # (F:05) 
		('총매수수량1', np.uint64),  # (F:06) 
		('매도거래원번호2', 'U4'),  # (F:07) 
		('매수거래원번호2', 'U4'),  # (F:08) 
		('총매도수량2', np.uint64),  # (F:09) 
		('총매수수량2', np.uint64),  # (F:10) 
		('매도거래원번호3', 'U4'),  # (F:11) 
		('매수거래원번호3', 'U4'),  # (F:12) 
		('총매도수량3', np.uint64),  # (F:13) 
		('총매수수량3', np.uint64),  # (F:14) 
		('매도거래원번호4', 'U4'),  # (F:15) 
		('매수거래원번호4', 'U4'),  # (F:16) 
		('총매도수량4', np.uint64),  # (F:17) 
		('총매수수량4', np.uint64),  # (F:18) 
		('매도거래원번호5', 'U4'),  # (F:19) 
		('매수거래원번호5', 'U4'),  # (F:20) 
		('총매도수량5', np.uint64),  # (F:21) 
		('총매수수량5', np.uint64),  # (F:22) 
		('총매도수량', np.uint64),  # (F:23) 
		('총매수수량', np.uint64),  # (F:24) 
		])
	MULTI_OUTPUT_DTYPE = None


class WL(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'WL', 'ELW 투자지표'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('체결시간', 'U6'),  # (F:02) 
		('패리티', np.float32),  # (F:03) 
		('기어링비율', np.float32),  # (F:04) 
		('손익분기율', np.float32),  # (F:05) 
		('자본지지점', np.float32),  # (F:06) 
		])
	MULTI_OUTPUT_DTYPE = None


class WS(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'WS', 'ELW 민감도'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('체결시간', 'U6'),  # (F:02) 
		('이론가', np.float32),  # (F:03) 
		('델타', np.float32),  # (F:04) 
		('감마', np.float32),  # (F:05) 
		('세타', np.float32),  # (F:06) 
		('베가', np.float32),  # (F:07) 
		('로', np.float32),  # (F:08) 
		('내재변동성', np.float32),  # (F:09) 
		])
	MULTI_OUTPUT_DTYPE = None


class tr_1771_10(BaseTR):
	NAME, DESCRIPTION = 'tr_1771_10', 'ELW 기초자산'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		])


class TR_WCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_WCHART', 'ELW 분/일 데이터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('그래프종류', 'U1'),  # (F:01) 1:분데이터 		D:일데이터
		('시간간격', 'U3'),  # (F:02) 분데이터일 경우 1 – 30 일데이터일 경우 1
		('시작일', 'U8'),  # (F:03) YYYYMMDD 분 데이터 요청시 : “00000000”
		('종료일', 'U8'),  # (F:04) YYYYMMDD 분 데이터 요청시 : “99999999”
		('조회갯수', 'U4'),  # (F:05) 1 – 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('시간', 'U6'),  # (F:01) 
		('시가', np.uint32),  # (F:02) 
		('고가', np.uint32),  # (F:03) 
		('저가', np.uint32),  # (F:04) 
		('종가', np.uint32),  # (F:05) 
		('이론가', np.float32),  # (F:06) 
		('단위거래량', np.uint64),  # (F:07) 
		('단위거래대금', np.uint64),  # (F:08) 
		('내재변동성', np.float32),  # (F:09) 
		('델타', np.float32),  # (F:10) 
		('감마', np.float32),  # (F:11) 
		('베가', np.float32),  # (F:12) 
		('로', np.float32),  # (F:13) 
		('세타', np.float32),  # (F:14) 
		])


class TR_1771_60(BaseTR):
	NAME, DESCRIPTION = 'TR_1771_60', 'ELW 종목별 종목(현재가조회)2'
	INPUT_DTYPE = np.dtype([
		('기초자산코드', 'U'),  # (F:00) 
		('콜풋구분', 'U'),  # (F:01) 
		('잔존만기', 'U'),  # (F:02) 
		('행사가FromTo', 'U'),  # (F:03) 
		('거래량', np.uint64),  # (F:04) 거래량|호가창 (0:전체, 1:5원, 2:10원, 3:10원이상)
		('LP', 'U'),  # (F:05) 
		('LP비중FromTo', 'U'),  # (F:06) 
		('현재가FromTo', 'U'),  # (F:07) +LP주문종료일
		('LP만기', 'U'),  # (F:08) 
		('틱환산구분', 'U'),  # (F:09) 틱환산구분|KO접근도
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('기초자산한글명', 'U0'),  # (F:02) 
		('옵션종류', 'U1'),  # (F:03) 
		('행사가격', 'U4'),  # (F:04) 
		('만기일', 'U0'),  # (F:05) 
		('현재가', np.uint32),  # (F:06) 
		('전일대비구분', 'U1'),  # (F:07) 
		('전일대비', np.uint32),  # (F:08) 
		('전일대비율', 'U4'),  # (F:09) 
		('내재변동성', 'U4'),  # (F:10) 
		('누적거래량', np.uint64),  # (F:11) 
		('발행기관명', 'U0'),  # (F:12) 
		('전환비율', 'U0'),  # (F:13) 
		('델타', 'U3'),  # (F:14) 
		('기초자산현재가', 'U4'),  # (F:15) 
		('기초자산전일대비구분', 'U1'),  # (F:16) 
		('기초자산전일대비', 'U4'),  # (F:17) 
		('기초자산전일대비율', 'U4'),  # (F:18) 
		('LP명', 'U0'),  # (F:19) 
		('LP비중', 'U0'),  # (F:20) 
		('고객비중', 'U12'),  # (F:21) 
		('이론가', 'U7'),  # (F:22) 
		('세타', 'U5'),  # (F:23) 
		('베가', 'U0'),  # (F:24) 
		('발행물량', 'U0'),  # (F:25) 
		('ELW거래대금', np.uint64),  # (F:26) 
		('LP주문종료일', 'U0'),  # (F:27) 
		('확정액', 'U0'),  # (F:28) 
		('역사적변동성', 'U3'),  # (F:29) 
		('틱환산', 'U2'),  # (F:30) 
		('LP보유수량', 'U12'),  # (F:31) 
		('ISIN코드', 'U0'),  # (F:32) 
		('거래종료일', 'U0'),  # (F:33) 
		('KO접근도', 'U0'),  # (F:34) 
		('LP호가내재변동성', 'U0'),  # (F:35) 
		('손익분기', 'U0'),  # (F:36) 
		('전일거래량', np.uint64),  # (F:37) 
		('매도1차호가', 'U0'),  # (F:38) 
		('매수1차호가', 'U0'),  # (F:39) 
		('잔존일', 'U0'),  # (F:40) 
		])


class LB(BaseTR):
	NAME, DESCRIPTION = 'LB', '주식선물 마스터'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('일련번호', 'U4'),  # (F:02) 
		('입회일자', 'U8'),  # (F:03) 
		('한글종목명', 'U50'),  # (F:04) 
		('영문종목명', 'U50'),  # (F:05) 
		('축약종목명', 'U25'),  # (F:06) 
		('종목보조코드', 'U6'),  # (F:07) 
		('상장일', 'U8'),  # (F:08) 
		('최근월물구분', 'U1'),  # (F:09) 1:해당, 2:비해당
		('최초거래일', 'U8'),  # (F:10) 
		('최종거래일', 'U8'),  # (F:11) 
		('상장일수', 'U3'),  # (F:12) 
		('잔존일수', 'U3'),  # (F:13) 
		('CD금리', np.float32),  # (F:14) (단위:%) 전일 11:00경 호가 수익률
		('배당지수미래가치', np.float32),  # (F:15) 
		('기준가', 'U7'),  # (F:16) 
		('기준가구분', 'U1'),  # (F:17) 1:전일정산가, 2:전일기준가(최초거래성립전 종가미형성), 3:당일이론가(최초거래성립전 종가미형성), 4:전일기세(최초거래성립전 기세형성), 5:당일이론가(최초거래성립전 기세형성), 6:조정된 전일정산가, 7:조정된 전일기준가(거래형성후 종가미형성), 8:조정된 전일기세(기세형성), 9:전일 대상자산 종가
		('상한가', 'U8'),  # (F:18) 
		('하한가', 'U8'),  # (F:19) 
		('CB적용상한가', 'U7'),  # (F:20) 
		('CB적용하한가', 'U7'),  # (F:21) 
		('전일정산가', np.float32),  # (F:22) 
		('전일정산가구분', 'U1'),  # (F:23) 
		('전일종가', np.float32),  # (F:24) 
		('전일종가구분', 'U1'),  # (F:25) 1:실세, 2:기세, 3:무거래
		('전일거래량', np.uint64),  # (F:26) 
		('전일거래대금', np.uint64),  # (F:27) 
		('전일미결제약정수량', 'U8'),  # (F:28) 
		('상장중최고일자', 'U8'),  # (F:29) 
		('상장중최고가', 'U8'),  # (F:30) 
		('상장중최저일자', 'U8'),  # (F:31) 
		('상장중최저가', 'U8'),  # (F:32) 
		('시장가허용구분', 'U1'),  # (F:33) Y:허용, N:불허
		('조건부지정가허용구분', 'U1'),  # (F:34) 
		('최유리지정가허용구분', 'U1'),  # (F:35) 
		('최종매매시간', 'U8'),  # (F:36) 
		('스프레드근월물표준코드', 'U12'),  # (F:37) 
		('전일근월물종가', 'U7'),  # (F:38) 
		('전일근월물체결수량', 'U8'),  # (F:39) 
		('전일근월물체결대금', 'U12'),  # (F:40) 
		('스프레드원월물표준코드', 'U12'),  # (F:41) 
		('전일원월물종가', 'U7'),  # (F:42) 
		('전일원월물체결수량', 'U8'),  # (F:43) 
		('전일원월물체결대금', 'U12'),  # (F:44) 
		('장구분', 'U2'),  # (F:45) 
		('거래단위', 'U16'),  # (F:46) CHAR(8) -> CHAR(16)
		('시장조성종목여부', 'U1'),  # (F:47) 0:미시장조성종목, 1:당일시장조성종목, 2:과거시장조성종목
		('조정구분', 'U1'),  # (F:48) SPACE:정상, 0:미결제조정, C:거래단위조정
		('거래정지여부', 'U1'),  # (F:49) Y:거래정지, N:정상
		('결제방법', 'U1'),  # (F:50) D:인수도결제, C:현금결제
		('매매체결방법', 'U1'),  # (F:51) N:정상, U:단일가체결
		('대상주식코드', 'U12'),  # (F:52) 
		('미결제한도수량', 'U8'),  # (F:53) 
		('실시간가격제한여부', 'U1'),  # (F:54) Y:실시간가격제한, N:제한없슴
		('실시간상한가간격', 'U8'),  # (F:55) 
		('실시간하한간격', 'U8'),  # (F:56) 
		])
	MULTI_OUTPUT_DTYPE = None


class LC(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'LC', '주식선물 현재가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('일련번호', 'U6'),  # (F:03) 
		('현재가', 'U8'),  # (F:04) 
		('전일대비구분', 'U1'),  # (F:05) 상한(1)상승(2)보합(3)하한(4)하락(5)기세상한(6)기세상승(7)기세하한(8)기세하한(9)
		('전일대비', 'U7'),  # (F:06) 
		('전일대비율', np.float32),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('누적거래대금', np.uint64),  # (F:09) (단위:원)
		('단위체결량', 'U6'),  # (F:10) 
		('미결제약정수량', 'U8'),  # (F:11) 
		('시가', 'U8'),  # (F:12) 
		('고가', 'U8'),  # (F:13) 
		('저가', 'U8'),  # (F:14) 
		('시가시간', 'U6'),  # (F:15) 
		('고가시간', 'U6'),  # (F:16) 
		('저가시간', 'U6'),  # (F:17) 
		('매도호가', 'U8'),  # (F:18) 
		('매수호가', 'U8'),  # (F:19) 
		('호가체결구분', 'U1'),  # (F:20) 0:시초가, 1:매도호가, 2:매수호가
		('근월물의약정가', 'U7'),  # (F:21) 
		('근월물체결수량', 'U7'),  # (F:22) 
		('근월물거래대금', np.uint64),  # (F:23) (단위:원)
		('원월물의약정가', 'U7'),  # (F:24) 
		('원월물체결수량', 'U7'),  # (F:25) 
		('원월물거래대금', np.uint64),  # (F:26) (단위:원)
		('실시간상한가', 'U8'),  # (F:27) 
		('실시간하한가', 'U8'),  # (F:28) 
		])
	MULTI_OUTPUT_DTYPE = None


class LH(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'LH', '주식선물 호가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('호가접수시간', 'U8'),  # (F:02) 
		('매도1호가', 'U8'),  # (F:03) 
		('매수1호가', 'U8'),  # (F:04) 
		('매도1호가수량', 'U6'),  # (F:05) 
		('매수1호가수량', 'U6'),  # (F:06) 
		('매도1호가건수', 'U4'),  # (F:07) 
		('매수1호가건수', 'U4'),  # (F:08) 
		('매도2호가', 'U8'),  # (F:09) 
		('매수2호가', 'U8'),  # (F:10) 
		('매도2호가수량', 'U6'),  # (F:11) 
		('매수2호가수량', 'U6'),  # (F:12) 
		('매도2호가건수', 'U4'),  # (F:13) 
		('매수2호가건수', 'U4'),  # (F:14) 
		('매도3호가', 'U8'),  # (F:15) 
		('매수3호가', 'U8'),  # (F:16) 
		('매도3호가수량', 'U6'),  # (F:17) 
		('매수3호가수량', 'U6'),  # (F:18) 
		('매도3호가건수', 'U4'),  # (F:19) 
		('매수3호가건수', 'U4'),  # (F:20) 
		('매도4호가', 'U8'),  # (F:21) 
		('매수4호가', 'U8'),  # (F:22) 
		('매도4호가수량', 'U6'),  # (F:23) 
		('매수4호가수량', 'U6'),  # (F:24) 
		('매도4호가건수', 'U4'),  # (F:25) 
		('매수4호가건수', 'U4'),  # (F:26) 
		('매도5호가', 'U8'),  # (F:27) 
		('매수5호가', 'U8'),  # (F:28) 
		('매도5호가수량', 'U6'),  # (F:29) 
		('매수5호가수량', 'U6'),  # (F:30) 
		('매도5호가건수', 'U4'),  # (F:31) 
		('매수5호가건수', 'U4'),  # (F:32) 
		('매도6호가', 'U8'),  # (F:33) 
		('매수6호가', 'U8'),  # (F:34) 
		('매도6호가수량', 'U6'),  # (F:35) 
		('매수6호가수량', 'U6'),  # (F:36) 
		('매도6호가건수', 'U4'),  # (F:37) 
		('매수6호가건수', 'U4'),  # (F:38) 
		('매도7호가', 'U8'),  # (F:39) 
		('매수7호가', 'U8'),  # (F:40) 
		('매도7호가수량', 'U6'),  # (F:41) 
		('매수7호가수량', 'U6'),  # (F:42) 
		('매도7호가건수', 'U4'),  # (F:43) 
		('매수7호가건수', 'U4'),  # (F:44) 
		('매도8호가', 'U8'),  # (F:45) 
		('매수8호가', 'U8'),  # (F:46) 
		('매도8호가수량', 'U6'),  # (F:47) 
		('매수8호가수량', 'U6'),  # (F:48) 
		('매도8호가건수', 'U4'),  # (F:49) 
		('매수8호가건수', 'U4'),  # (F:50) 
		('매도9호가', 'U8'),  # (F:51) 
		('매수9호가', 'U8'),  # (F:52) 
		('매도9호가수량', 'U6'),  # (F:53) 
		('매수9호가수량', 'U6'),  # (F:54) 
		('매도9호가건수', 'U4'),  # (F:55) 
		('매수9호가건수', 'U4'),  # (F:56) 
		('매도10호가', 'U8'),  # (F:57) 
		('매수10호가', 'U8'),  # (F:58) 
		('매도10호가수량', 'U6'),  # (F:59) 
		('매수10호가수량', 'U6'),  # (F:60) 
		('매도10호가건수', 'U4'),  # (F:61) 
		('매수10호가건수', 'U4'),  # (F:62) 
		('매도총호가수량', 'U7'),  # (F:63) 
		('매수총호가수량', 'U7'),  # (F:64) 
		('매도총호가건수', 'U5'),  # (F:65) 
		('매수총호가건수', 'U5'),  # (F:66) 
		('장상태구분코드', 'U2'),  # (F:67) 00 : 초기(장개시전)    10 : 시가단일가 11 : 시가단일가연장    20 : 장중단일가 21 : 장중단일가연장    30 : 종가단일가 40 : 접속  80 : 단위매매체결(주식관련상품) 90 : 거래정지           99 : 장종료
		('예상체결가격', 'U8'),  # (F:68) 
		])
	MULTI_OUTPUT_DTYPE = None


class LL(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'LL', '주식선물 민감도'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('이론가', 'U7'),  # (F:03) 
		('델타', np.float32),  # (F:04) 
		('감마', np.float32),  # (F:05) 
		('베가', np.float32),  # (F:06) 
		('로', np.float32),  # (F:07) 
		('세타', np.float32),  # (F:08) 
		])
	MULTI_OUTPUT_DTYPE = None


class TR_EFCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_EFCHART', '주식선물 분/일 데이터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('그래프종류', 'U1'),  # (F:01) 1:분데이터 		D:일데이터
		('시간간격', 'U3'),  # (F:02) 분데이터일 경우 1 – 30 일데이터일 경우 1
		('시작일', 'U8'),  # (F:03) YYYYMMDD 분 데이터 요청시 : “00000000”
		('종료일', 'U8'),  # (F:04) YYYYMMDD 분 데이터 요청시 : “99999999”
		('조회갯수', 'U4'),  # (F:05) 1 – 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('시간', 'U6'),  # (F:01) 
		('시가', 'U8'),  # (F:02) 
		('고가', 'U8'),  # (F:03) 
		('저가', 'U8'),  # (F:04) 
		('종가', 'U8'),  # (F:05) 
		('미결제약정', 'U8'),  # (F:06) 
		('이론가', 'U8'),  # (F:07) 
		('기초자산지수', 'U8'),  # (F:08) 
		('단위거래량', np.uint64),  # (F:09) 
		('단위거래대금', np.uint64),  # (F:10) 
		])


class LI(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'LI', '주식선물 가격제한폭확대'
	INPUT_DTYPE = np.dtype([('단축코드', 'U8')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('상한시간', 'U8'),  # (F:02) 
		('하한시간', 'U8'),  # (F:03) 
		('가격제한확대상한단계', 'U2'),  # (F:04) 
		('가격제한확대하한단계', 'U2'),  # (F:05) 
		('상한가', 'U8'),  # (F:06) 
		('하한가', 'U8'),  # (F:07) 
		('가격제한확대적용방향코드', 'U1'),  # (F:08) U: 상승, D: 하락, B:양방향
		])
	MULTI_OUTPUT_DTYPE = None


class MB(BaseTR):
	NAME, DESCRIPTION = 'MB', '상품선물 마스터'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('일련번호', 'U6'),  # (F:02) 
		('입회일자', 'U8'),  # (F:03) 
		('파생상품ID', 'U10'),  # (F:04) 
		('한글종목명', 'U40'),  # (F:05) 
		('한글종목약어명', 'U40'),  # (F:06) 
		('영문종목명', 'U40'),  # (F:07) 
		('영문종목약어명', 'U40'),  # (F:08) 
		('상장일', 'U8'),  # (F:09) 
		('상장폐지일', 'U8'),  # (F:10) 
		('스프레드기준종목구분코드', 'U1'),  # (F:11) 
		('결제방법', 'U1'),  # (F:12) 
		('상한가', np.float32),  # (F:13) 
		('하한가', np.float32),  # (F:14) 
		('기초자산ID', 'U3'),  # (F:15) 
		('스프레드유형코드', 'U2'),  # (F:16) 
		('스프레드근월물표준코드', 'U12'),  # (F:17) 
		('스프레드원월물표준코드', 'U12'),  # (F:18) 
		('최종거래일', 'U8'),  # (F:19) 
		('최종결제일자', 'U8'),  # (F:20) 
		('월물구분코드', 'U1'),  # (F:21) 
		('만기일자', 'U8'),  # (F:22) 
		('거래단위', np.float32),  # (F:23) 
		('거래승수', np.float32),  # (F:24) 
		('상장유형코드1', 'U1'),  # (F:25)   원래 '상장유형코드' 였음. 중복에러 발생하여 숫자 부여.
		('상장유형코드2', 'U12'),  # (F:26)   원래 '상장유형코드' 였음. 중복에러 발생하여 숫자 부여.
		('기초자산종가', np.float32),  # (F:27) 
		('잔존일수', 'U3'),  # (F:28) 
		('기준가', np.float32),  # (F:29) 
		('기준가구분', 'U2'),  # (F:30) 
		('매매용기준가격구분코드', 'U1'),  # (F:31) 
		('협의대량매매대상여부', 'U1'),  # (F:32) 
		('전일정산가', np.float32),  # (F:33) 
		('거래정지여부', 'U1'),  # (F:34) 
		('CB적용상한가', np.float32),  # (F:35) 
		('CB적용하한가', np.float32),  # (F:36) 
		('배당지수미래가치', np.float32),  # (F:37) 
		('전일종가', np.float32),  # (F:38) 
		('전일종가구분', 'U1'),  # (F:39) 
		('최초거래일', 'U8'),  # (F:40) 
		('최종매매시간', 'U8'),  # (F:41) 
		('전일정산가구분', 'U2'),  # (F:42) 
		('전일미결제약정수량', 'U8'),  # (F:43) 
		('상장중최고가', np.float32),  # (F:44) 
		('상장중최저가', np.float32),  # (F:45) 
		('상장중최고일자', 'U8'),  # (F:46) 
		('상장중최저일자', 'U8'),  # (F:47) 
		('기준일수', 'U3'),  # (F:48) 
		('전일거래량', np.uint64),  # (F:49) 
		('전일거래대금', np.uint64),  # (F:50) 
		('CD금리', np.float32),  # (F:51) 
		('지정가호가조건구분코드', 'U1'),  # (F:52) 
		('시장가호가조건구분코드', 'U1'),  # (F:53) 
		('조건부지정가허용구분', 'U1'),  # (F:54) 
		('최유리지정가허용구분', 'U1'),  # (F:55) 
		('장구분', 'U3'),  # (F:56) 
		('EFP거래대상여부', 'U1'),  # (F:57) 
		('FLEX거래대상여부', 'U1'),  # (F:58) 
		('전일협의대량체결수량', 'U7'),  # (F:59) 
		('전일협의대량체결대금', np.uint64),  # (F:60) 
		('전일EFP체결수량', 'U7'),  # (F:61) 
		('전일EFP거래대금', np.uint64),  # (F:62) 
		('휴장여부', 'U1'),  # (F:63) 
		('실시간가격제한여부', 'U1'),  # (F:64) Y:실시간 가격제한, N:제한없슴
		('실시간상한가간격', np.float32),  # (F:65) 
		('실시간하한가간격', np.float32),  # (F:66) 
		])
	MULTI_OUTPUT_DTYPE = None


class MC(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'MC', '상품선물 체결'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('일련번호', 'U6'),  # (F:03) 
		('현재가', np.float32),  # (F:04) 
		('전일대비구분', 'U1'),  # (F:05) 
		('전일대비', np.float32),  # (F:06) 
		('전일대비율', np.float32),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('누적거래대금', np.uint64),  # (F:09) 
		('단위체결량', 'U6'),  # (F:10) 
		('미결제약정수량', 'U8'),  # (F:11) 
		('시가', np.float32),  # (F:12) 
		('고가', np.float32),  # (F:13) 
		('저가', np.float32),  # (F:14) 
		('시가시간', 'U6'),  # (F:15) 
		('고가시간', 'U6'),  # (F:16) 
		('저가시간', 'U6'),  # (F:17) 
		('매도호가', np.float32),  # (F:18) 
		('매수호가', np.float32),  # (F:19) 
		('호가체결구분', 'U1'),  # (F:20) 
		('근월물의 약정가', np.float32),  # (F:21) 
		('원월물의 약정가', np.float32),  # (F:22) 
		('협의대량체결수량', 'U7'),  # (F:23) 
		('EFP누적체결수량', 'U7'),  # (F:24) 
		('실시간상한가', np.float32),  # (F:25) 
		('실시간하한가', np.float32),  # (F:26) 
		])
	MULTI_OUTPUT_DTYPE = None


class MH(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'MH', '상품선물 호가'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('호가접수시간', 'U8'),  # (F:02) 
		('매도1호가', np.float32),  # (F:03) 
		('매수1호가', np.float32),  # (F:04) 
		('매도1호가수량', 'U8'),  # (F:05) 
		('매수1호가수량', 'U8'),  # (F:06) 
		('매도1호가건수', 'U5'),  # (F:07) 
		('매수1호가건수', 'U5'),  # (F:08) 
		('매도2호가', np.float32),  # (F:09) 
		('매수2호가', np.float32),  # (F:10) 
		('매도2호가수량', 'U8'),  # (F:11) 
		('매수2호가수량', 'U8'),  # (F:12) 
		('매도2호가건수', 'U5'),  # (F:13) 
		('매수2호가건수', 'U5'),  # (F:14) 
		('매도3호가', np.float32),  # (F:15) 
		('매수3호가', np.float32),  # (F:16) 
		('매도3호가수량', 'U8'),  # (F:17) 
		('매수3호가수량', 'U8'),  # (F:18) 
		('매도3호가건수', 'U5'),  # (F:19) 
		('매수3호가건수', 'U5'),  # (F:20) 
		('매도4호가', np.float32),  # (F:21) 
		('매수4호가', np.float32),  # (F:22) 
		('매도4호가수량', 'U8'),  # (F:23) 
		('매수4호가수량', 'U8'),  # (F:24) 
		('매도4호가건수', 'U5'),  # (F:25) 
		('매수4호가건수', 'U5'),  # (F:26) 
		('매도5호가', np.float32),  # (F:27) 
		('매수5호가', np.float32),  # (F:28) 
		('매도5호가수량', 'U8'),  # (F:29) 
		('매수5호가수량', 'U8'),  # (F:30) 
		('매도5호가건수', 'U5'),  # (F:31) 
		('매수5호가건수', 'U5'),  # (F:32) 
		('매도총호가수량', 'U8'),  # (F:33) 
		('매수총호가수량', 'U8'),  # (F:34) 
		('매도총호가건수', 'U5'),  # (F:35) 
		('매수총호가건수', 'U5'),  # (F:36) 
		('장상태구분코드', 'U2'),  # (F:37) 
		('예상체결가격', np.float32),  # (F:38) 
		])
	MULTI_OUTPUT_DTYPE = None


class TR_CFCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_CFCHART', '상품선물 분/일 데이터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('그래프종류', 'U1'),  # (F:01) 1:분데이터 		D:일데이터
		('시간간격', 'U3'),  # (F:02) 분데이터일 경우 1 – 30 일데이터일 경우 1
		('시작일', 'U8'),  # (F:03) YYYYMMDD 분 데이터 요청시 : “00000000”
		('종료일', 'U8'),  # (F:04) YYYYMMDD 분 데이터 요청시 : “99999999”
		('조회갯수', 'U4'),  # (F:05) 1 – 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('시간', 'U0'),  # (F:01) 
		('시가', 'U8'),  # (F:02) 
		('고가', 'U8'),  # (F:03) 
		('저가', 'U8'),  # (F:04) 
		('종가', 'U8'),  # (F:05) 
		('미결제약정', 'U8'),  # (F:06) 
		('이론가', 'U8'),  # (F:07) 
		('기초자산지수', 'U8'),  # (F:08) 
		('단위거래량', np.uint64),  # (F:09) 
		('단위거래대금', np.uint64),  # (F:10) 
		])


class PB(BaseTR):
	NAME, DESCRIPTION = 'PB', 'EUREX 마스터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U9'),  # (F:00) E+옵션코드(ex E201FA235)
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('GIC', 'U13'),  # (F:00) E+옵션표준코드(ex EKR4301F62528)
		('단축코드', 'U9'),  # (F:01) E+옵션코드(ex E201FA235)
		('표준코드', 'U12'),  # (F:02) 
		('일련번호', 'U6'),  # (F:03) 
		('입회일자', 'U8'),  # (F:04) 
		('한글명', 'U30'),  # (F:05) 
		('영문명', 'U30'),  # (F:06) 
		('축약종목명', 'U15'),  # (F:07) 
		('옵션종류', 'U1'),  # (F:08) 2:콜, 3:풋
		('행사가격', 'U6'),  # (F:09) 
		('전일종가', 'U6'),  # (F:10) 
		])
	MULTI_OUTPUT_DTYPE = None


class PC(BaseTR):
	NAME, DESCRIPTION = 'PC', 'EUREX 현재가'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U9'),  # (F:00) E+옵션코드(ex E201FA235)
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('GIC', 'U13'),  # (F:00) E+옵션표준코드(ex EKR4301F62528)
		('단축코드', 'U9'),  # (F:01) E+옵션코드(ex E201FA235)
		('표준코드', 'U12'),  # (F:02) 
		('입회일자', 'U8'),  # (F:03) 
		('일자', 'U8'),  # (F:04) 
		('체결시간', 'U8'),  # (F:05) 
		('현재가', np.float32),  # (F:06) 
		('전일대비구분', 'U1'),  # (F:07) 
		('전일대비', np.float32),  # (F:08) 전일대비
		('전일대비율', np.float32),  # (F:09) 전일대비율
		('누적거래량', np.uint64),  # (F:10) 누적거래량
		('누적거래대금', np.uint64),  # (F:11) 누적거래대금
		('단위체결량', 'U8'),  # (F:12) 단위체결량
		('미결제약정수량', 'U8'),  # (F:13) 미결제약정수량
		('시가', np.float32),  # (F:14) 시가
		('고가', np.float32),  # (F:15) 고가
		('저가', np.float32),  # (F:16) 저가
		('시가시간', 'U6'),  # (F:17) 시가시간
		('고가시간', 'U6'),  # (F:18) 고가시간
		('저가시간', 'U6'),  # (F:19) 저가시간
		('매도호가', np.float32),  # (F:20) 매도호가
		('매수호가', np.float32),  # (F:21) 매수호가
		('호가체결구분', 'U1'),  # (F:22) 호가체결구분
		])
	MULTI_OUTPUT_DTYPE = None


class PH(BaseTR):
	NAME, DESCRIPTION = 'PH', 'EUREX 호가'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U9'),  # (F:00) E+옵션코드(ex E201FA235)
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('GIC', 'U13'),  # (F:00) E+옵션표준코드(ex EKR4301F62528)
		('단축코드', 'U9'),  # (F:01) E+옵션코드(ex E201FA235)
		('표준코드', 'U12'),  # (F:02) 
		('입회일자', 'U8'),  # (F:03) 
		('일자', 'U8'),  # (F:04) 
		('호가접수시간', 'U8'),  # (F:05) 
		('매도1호가', np.float32),  # (F:06) 
		('매수1호가', np.float32),  # (F:07) 
		('매도1호가수량', 'U8'),  # (F:08) 
		('매수1호가수량', 'U8'),  # (F:09) 
		('매도1호가건수', 'U5'),  # (F:10) 
		('매수1호가건수', 'U5'),  # (F:11) 
		('매도2호가', np.float32),  # (F:12) 
		('매수2호가', np.float32),  # (F:13) 
		('매도2호가수량', 'U8'),  # (F:14) 
		('매수2호가수량', 'U8'),  # (F:15) 
		('매도2호가건수', 'U5'),  # (F:16) 
		('매수2호가건수', 'U5'),  # (F:17) 
		('매도3호가', np.float32),  # (F:18) 
		('매수3호가', np.float32),  # (F:19) 
		('매도3호가수량', 'U8'),  # (F:20) 
		('매수3호가수량', 'U8'),  # (F:21) 
		('매도3호가건수', 'U5'),  # (F:22) 
		('매수3호가건수', 'U5'),  # (F:23) 
		('매도4호가', np.float32),  # (F:24) 
		('매수4호가', np.float32),  # (F:25) 
		('매도4호가수량', 'U8'),  # (F:26) 
		('매수4호가수량', 'U8'),  # (F:27) 
		('매도4호가건수', 'U5'),  # (F:28) 
		('매수4호가건수', 'U5'),  # (F:29) 
		('매도5호가', np.float32),  # (F:30) 
		('매수5호가', np.float32),  # (F:31) 
		('매도5호가수량', 'U8'),  # (F:32) 
		('매수5호가수량', 'U8'),  # (F:33) 
		('매도5호가건수', 'U5'),  # (F:34) 
		('매수5호가건수', 'U5'),  # (F:35) 
		('매도총호가수량', 'U8'),  # (F:36) 
		('매수총호가수량', 'U8'),  # (F:37) 
		('매도총호가건수', 'U5'),  # (F:38) 
		('매수총호가건수', 'U5'),  # (F:39) 
		])
	MULTI_OUTPUT_DTYPE = None


class TR_ERCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_ERCHART', 'EUREX 분/일 데이터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U9'),  # (F:00) E+옵션코드(ex E201FA235)
		('그래프종류', 'U1'),  # (F:01) 1:분데이터 		D:일데이터
		('시간간격', 'U3'),  # (F:02) 분데이터일 경우 1 – 5 일데이터일 경우 1
		('시작일', 'U8'),  # (F:03) YYYYMMDD 분 데이터 요청시 : “00000000”
		('종료일', 'U8'),  # (F:04) YYYYMMDD 분 데이터 요청시 : “99999999”
		('조회갯수', 'U4'),  # (F:05) 1 – 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('체결시간', 'U6'),  # (F:01) 
		('시가', 'U6'),  # (F:02) 
		('고가', 'U6'),  # (F:03) 
		('저가', 'U6'),  # (F:04) 
		('종가', 'U6'),  # (F:05) 
		('미결제약정수량', 'U6'),  # (F:06) 
		('이론가', 'U6'),  # (F:07) 
		('기초자산지수', 'U6'),  # (F:08) 
		('단위거래량', np.uint64),  # (F:09) 
		('단위거래대금', np.uint64),  # (F:10) 
		])


class VB(BaseTR):
	NAME, DESCRIPTION = 'VB', 'KONEX 마스터'
	INPUT_DTYPE = np.dtype([('표준코드', 'U12')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('장구분', 'U1'),  # (F:02) 
		('일련번호', 'U4'),  # (F:03) 
		('입회일자', 'U8'),  # (F:04) 
		('한글종목명', 'U40'),  # (F:05) 
		('영문종목명', 'U40'),  # (F:06) 
		('제조업구분/업종대분류', 'U3'),  # (F:07) 
		('업종중분류', 'U3'),  # (F:08) 
		('업종소분류', 'U3'),  # (F:09) 
		('산업업종코드', 'U6'),  # (F:10) 
		('KOSPI200/KOSDAQ50채용구분', 'U1'),  # (F:11) 
		('KOSPI100채용구분', 'U1'),  # (F:12) 
		('KOSPI50채용구분', 'U1'),  # (F:13) 
		('정보통신지수채용구분', 'U1'),  # (F:14) 
		('시가총액규모/지수업종그룹', 'U1'),  # (F:15) 
		('KOSDI구분/지배구조우량구분', 'U2'),  # (F:16) 
		('상장구분', 'U2'),  # (F:17) 
		('상장주식수', np.uint64),  # (F:18) 
		('소속구분', 'U2'),  # (F:19) 
		('결산월일', 'U4'),  # (F:20) 
		('액면가', np.uint32),  # (F:21) 
		('액면가변경구분코드', 'U2'),  # (F:22) 
		('전일종가', np.uint32),  # (F:23) 
		('전일거래량', np.uint64),  # (F:24) 
		('전일거래대금', np.uint64),  # (F:25) 
		('기준가', np.uint32),  # (F:26) 
		('상한가', np.uint32),  # (F:27) 
		('하한가', np.uint32),  # (F:28) 
		('대용가', np.uint32),  # (F:29) 
		('거래정지구분', 'U1'),  # (F:30) 
		('관리구분', 'U1'),  # (F:31) 
		('감리구분', 'U1'),  # (F:32) 
		('락구분', 'U2'),  # (F:33) 
		('불성실공시지정여부', 'U1'),  # (F:34) 
		('평가가격', np.uint32),  # (F:35) 
		('최고호가가격', np.uint32),  # (F:36) 
		('최저호가가격', np.uint32),  # (F:37) 
		('매매구분', 'U1'),  # (F:38) 
		('정리매매시작일', 'U8'),  # (F:39) 
		('정리매매종료일', 'U8'),  # (F:40) 
		('투자유의구분', 'U1'),  # (F:41) 
		('REITs구분', 'U1'),  # (F:42) 
		('매매수량단위', 'U5'),  # (F:43) 
		('시간외매매수량단위', 'U5'),  # (F:44) 
		('자본금', 'U18'),  # (F:45) 
		('배당수익율', np.float32),  # (F:46) 
		('ETF분류', 'U1'),  # (F:47) 
		('ETF관련지수업종대', 'U1'),  # (F:48) 
		('ETF관련지수업종중', 'U3'),  # (F:49) 
		('ETF CU단위', 'U8'),  # (F:50) 
		('ETF 구성종목수', 'U4'),  # (F:51) 
		('ETF 순자산총액', np.uint64),  # (F:52) 
		('ETF관련지수대비비율', np.float32),  # (F:53) 
		('최종NAV', np.float32),  # (F:54) 
		('매매방식 구분', 'U1'),  # (F:55) 
		('통합지수종목구분', 'U1'),  # (F:56) 
		('매매개시일', 'U8'),  # (F:57) 
		('KRX 섹터지수 자동차구분', 'U1'),  # (F:58) 
		('KRX 섹터지수 반도체구분', 'U1'),  # (F:59) 
		('KRX 섹터지수 바이오구분', 'U1'),  # (F:60) 
		('KRX 섹터지수 금융구분', 'U1'),  # (F:61) 
		('KRX 섹터지수 정보통신구분', 'U1'),  # (F:62) 
		('우회상장구분', 'U1'),  # (F:63) 
		('KOSPI여부', 'U2'),  # (F:64) 
		('KRX 섹터지수 화학에너지구분', 'U1'),  # (F:65) 
		('KRX 섹터지수 철강구분', 'U1'),  # (F:66) 
		('KRX 섹터지수 필수소비재구분', 'U1'),  # (F:67) 
		('KRX 섹터지수 미디어통신구분', 'U1'),  # (F:68) 
		('KRX 섹터지수 건설구분', 'U1'),  # (F:69) 
		('KRX 섹터지수 비은행금융구분', 'U1'),  # (F:70) 
		('국가코드', 'U3'),  # (F:71) 
		('적용화폐단위', 'U3'),  # (F:72) 
		('적용환율', np.float32),  # (F:73) 
		('투자위험예고여부', 'U1'),  # (F:74) 
		('ETF유통주식수', 'U10'),  # (F:75) 
		('ETF자산기준통화', 'U3'),  # (F:76) 
		('ETF순자산총액(외화)', np.uint64),  # (F:77) 
		('ETF유통순자산총액(원화)', np.uint64),  # (F:78) 
		('ETF유통순자산총액(외화)', np.uint64),  # (F:79) 
		('ETF최종NAV(외화)', np.float32),  # (F:80) 
		('KRX 섹터지수 증권구분', 'U1'),  # (F:81) 
		('KRX 섹터지수 조선구분', 'U1'),  # (F:82) 
		('장전시간외시장가능여부', 'U1'),  # (F:83) 
		('공매도가능여부', 'U1'),  # (F:84) 
		('ETF추적기초자산단위코드', 'U3'),  # (F:85) 
		('ETF추적수익률배수부호', 'U1'),  # (F:86) 
		('ETF추적수익률배수', np.float32),  # (F:87) 
		('ETF장외파생상품편입여부', 'U1'),  # (F:88) 
		('ETF추적기초자산국내외구분코드', 'U1'),  # (F:89) 
		('상장일자', 'U8'),  # (F:90) 
		('발행가격', np.uint32),  # (F:91) 
		('SRI지수여부', 'U1'),  # (F:92) 
		('ETF참고지수소속시장구분코드', 'U1'),  # (F:93) 
		('ETF참고지수업종코드', 'U3'),  # (F:94) 
		('KRX 섹터지수 보험구분', 'U1'),  # (F:95) 
		('KRX 섹터지수 운송구분', 'U1'),  # (F:96) 
		('REGULATION S 적용여부', 'U1'),  # (F:97) 
		('일련번호 8자리', 'U8'),  # (F:98) 
		])
	MULTI_OUTPUT_DTYPE = None


class VC(BaseTR):
	NAME, DESCRIPTION = 'VC', 'KONEX 현재가'
	INPUT_DTYPE = np.dtype([('표준코드', 'U12')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', np.float32),  # (F:06) 
		('누적거래량', np.uint64),  # (F:07) 
		('누적거래대금', np.uint64),  # (F:08) 
		('단위체결량', 'U12'),  # (F:09) 
		('시가', np.uint32),  # (F:10) 
		('고가', np.uint32),  # (F:11) 
		('저가', np.uint32),  # (F:12) 
		('시가시간', 'U6'),  # (F:13) 
		('고가시간', 'U6'),  # (F:14) 
		('저가시간', 'U6'),  # (F:15) 
		('매매구분', 'U1'),  # (F:16) 
		('장구분', 'U1'),  # (F:17) 
		('호가체결구분', 'U1'),  # (F:18) 
		('가중평균가', np.uint32),  # (F:19) 
		('매도1호가', np.uint32),  # (F:20) 
		('매수1호가', np.uint32),  # (F:21) 
		('거래강도', np.float32),  # (F:22) 
		('매매구분별거래량', np.uint64),  # (F:23) 
		('체결강도', np.float32),  # (F:24) 
		('체결매도매수구분', 'U1'),  # (F:25) 
		])
	MULTI_OUTPUT_DTYPE = None


class VH(BaseTR):
	NAME, DESCRIPTION = 'VH', 'KONEX 호가'
	INPUT_DTYPE = np.dtype([('표준코드', 'U12')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('호가접수시간', 'U6'),  # (F:02) 
		('장구분', 'U1'),  # (F:03) 
		('매도1호가', np.uint32),  # (F:04) 
		('매수1호가', np.uint32),  # (F:05) 
		('매도1호가수량', 'U12'),  # (F:06) 
		('매수1호가수량', 'U12'),  # (F:07) 
		('매도2호가', np.uint32),  # (F:08) 
		('매수2호가', np.uint32),  # (F:09) 
		('매도2호가수량', 'U12'),  # (F:10) 
		('매수2호가수량', 'U12'),  # (F:11) 
		('매도3호가', np.uint32),  # (F:12) 
		('매수3호가', np.uint32),  # (F:13) 
		('매도3호가수량', 'U12'),  # (F:14) 
		('매수3호가수량', 'U12'),  # (F:15) 
		('매도4호가', np.uint32),  # (F:16) 
		('매수4호가', np.uint32),  # (F:17) 
		('매도4호가수량', 'U12'),  # (F:18) 
		('매수4호가수량', 'U12'),  # (F:19) 
		('매도5호가', np.uint32),  # (F:20) 
		('매수5호가', np.uint32),  # (F:21) 
		('매도5호가수량', 'U12'),  # (F:22) 
		('매수5호가수량', 'U12'),  # (F:23) 
		('매도6호가', np.uint32),  # (F:24) 
		('매수6호가', np.uint32),  # (F:25) 
		('매도6호가수량', 'U12'),  # (F:26) 
		('매수6호가수량', 'U12'),  # (F:27) 
		('매도7호가', np.uint32),  # (F:28) 
		('매수7호가', np.uint32),  # (F:29) 
		('매도7호가수량', 'U12'),  # (F:30) 
		('매수7호가수량', 'U12'),  # (F:31) 
		('매도8호가', np.uint32),  # (F:32) 
		('매수8호가', np.uint32),  # (F:33) 
		('매도8호가수량', 'U12'),  # (F:34) 
		('매수8호가수량', 'U12'),  # (F:35) 
		('매도9호가', np.uint32),  # (F:36) 
		('매수9호가', np.uint32),  # (F:37) 
		('매도9호가수량', 'U12'),  # (F:38) 
		('매수9호가수량', 'U12'),  # (F:39) 
		('매도10호가', np.uint32),  # (F:40) 
		('매수10호가', np.uint32),  # (F:41) 
		('매도10호가수량', 'U12'),  # (F:42) 
		('매수10호가수량', 'U12'),  # (F:43) 
		('매도총호가수량', 'U12'),  # (F:44) 
		('매수총호가수량', 'U12'),  # (F:45) 
		('시간외매도호가수량', 'U12'),  # (F:46) 
		('시간외매수호가수량', 'U12'),  # (F:47) 
		('동시구분', 'U1'),  # (F:48) 
		('예상체결가격', np.uint32),  # (F:49) 
		('예상체결수량', 'U12'),  # (F:50) 
		('경쟁대량방향구분', 'U1'),  # (F:51) 
		])
	MULTI_OUTPUT_DTYPE = None



class knx_mst(BaseTR):
	NAME, DESCRIPTION = 'knx_mst', 'KONEX 종목정보조회'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('장구분', 'U1'),  # (F:02) 
		('종목명', 'U40'),  # (F:03) 
		('업종구분', 'U1'),  # (F:04) 
		('업종코드', 'U3'),  # (F:05) 
		('제조업구분/업종대분류', 'U3'),  # (F:06) 
		('업종중분류', 'U3'),  # (F:07) 
		('업종소분류', 'U3'),  # (F:08) 
		('산업업종코드', 'U6'),  # (F:09) 
		('KOSPI200세부업종', 'U1'),  # (F:10) 
		('KOSPI100채용구분', 'U1'),  # (F:11) 
		('KOSPI50채용구분', 'U1'),  # (F:12) 
		('정보통신지수채용구분', 'U1'),  # (F:13) 
		('시가총액규모', 'U1'),  # (F:14) 
		('KOSDI구분/지배구조우량구분', 'U2'),  # (F:15) 
		('상장구분', 'U2'),  # (F:16) 
		('증권ID', 'U2'),  # (F:17) 
		('결산월일', 'U4'),  # (F:18) 
		('거래정지구분', 'U1'),  # (F:19) 
		('관리구분', 'U1'),  # (F:20) 
		('시장경부구분코드', 'U1'),  # (F:21) 
		('락구분', 'U2'),  # (F:22) 
		('불성실공시지정여부', 'U1'),  # (F:23) 
		('매매구분', 'U1'),  # (F:24) 
		('리츠종류코드', 'U1'),  # (F:25) 
		('투자유의구분', 'U1'),  # (F:26) 
		('정규장매매수량단위', 'U5'),  # (F:27) 
		('시간외매매수량단위', 'U5'),  # (F:28) 
		('증거금구분', 'U1'),  # (F:29) 
		('신용증거금등급', 'U1'),  # (F:30) 
		('투자위험예고여부', 'U1'),  # (F:31) 
		('투자주의환기종목여부', 'U1'),  # (F:32) 
		('ETF추적수익률배수부호', 'U1'),  # (F:33) 
		('EFT추적수익률배수', 'U3'),  # (F:34) 
		('ETF대상지수소속시장구분코드', 'U1'),  # (F:35) 
		('ETF구분자', 'U1'),  # (F:36) 
		('단기과열종목코드', 'U1'),  # (F:37) 
		('지정자문인시장참가자번호', 'U5'),  # (F:38) 
		('단위매매체결여부', 'U1'),  # (F:39) 
		])


class TB(BaseTR):
	NAME, DESCRIPTION = 'TB', 'K-OTC 마스터'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('일련번호', 'U4'),  # (F:02) 
		('입회일자', 'U8'),  # (F:03) 
		('한글종목명', 'U20'),  # (F:04) 
		('영문종목명', 'U20'),  # (F:05) 
		('주권심볼', 'U7'),  # (F:06) 
		('산업업종코드', 'U8'),  # (F:07) 
		('상장구분', 'U2'),  # (F:08) 
		('상장주식수', 'U12'),  # (F:09) 발행주식
		('상장일', 'U8'),  # (F:10) 
		('소속구분', 'U2'),  # (F:11) 
		('자본금규모', 'U1'),  # (F:12) 
		('결산월', 'U2'),  # (F:13) 
		('액면가', np.uint32),  # (F:14) 
		('기준가', np.uint32),  # (F:15) 
		('상한가', np.uint32),  # (F:16) 
		('하한가', np.uint32),  # (F:17) 
		('전일종가', np.uint32),  # (F:18) 
		('전일거래량', np.uint32),  # (F:19) 
		('전일거래대금', np.uint64),  # (F:20) 
		('거래정지구분', 'U1'),  # (F:21) 
		('락구분', 'U2'),  # (F:22) 
		('불성실공시지정여부', 'U1'),  # (F:23) 
		('연초일자', 'U8'),  # (F:24) 
		('연초종가', np.uint32),  # (F:25) 
		('연중최고일자', 'U8'),  # (F:26) 
		('연중최고종가', np.uint32),  # (F:27) 
		('연중최저일자', 'U8'),  # (F:28) 
		('연중최저종가', np.uint32),  # (F:29) 
		('52주최고일자', 'U8'),  # (F:30) 
		('52주최고종가', np.uint32),  # (F:31) 
		('52주최저일자', 'U8'),  # (F:32) 
		('52주최저종가', np.uint32),  # (F:33) 
		('4일종가합', 'U12'),  # (F:34) 
		('9일종가합', 'U12'),  # (F:35) 
		('19일종가합', 'U12'),  # (F:36) 
		('59일종가합', 'U12'),  # (F:37) 
		('119일종가합', 'U12'),  # (F:38) 
		('4일거래량합', np.uint64),  # (F:39) 
		('9일거래량합', np.uint64),  # (F:40) 
		('19일거래량합', np.uint64),  # (F:41) 
		('59일거래량합', np.uint64),  # (F:42) 
		('119일거래량합', np.uint64),  # (F:43) 
		('심리11', 'U2'),  # (F:44) 
		('삼선전환상태', 'U1'),  # (F:45) 
		('삼선전환', np.uint32),  # (F:46) 
		('삼선전환다음', np.uint32),  # (F:47) 
		('삼선전환일자', 'U8'),  # (F:48) 
		('PER', 'U6'),  # (F:49) 
		('EPS', 'U10'),  # (F:50) 
		('전일가중평균주가', np.uint32),  # (F:51) 
		('결산구분', 'U1'),  # (F:52) 
		('지정신청사', 'U30'),  # (F:53) 
		('취소구분', 'U1'),  # (F:54) 
		('연누적거래량', np.uint64),  # (F:55) 
		('연누적거래대금', np.uint64),  # (F:56) 
		('공모구분', 'U1'),  # (F:57) 
		('공모가', np.uint32),  # (F:58) 
		('지정유형', 'U1'),  # (F:59) 
		('불성실공시지정일1', 'U8'),  # (F:60) 
		('불성실공시만료일1', 'U8'),  # (F:61) 
		('불성실공시지정일2', 'U8'),  # (F:62) 
		('불성실공시만료일2', 'U8'),  # (F:63) 
		('투자유의구분', 'U1'),  # (F:64) 
		('지정사유1', 'U2'),  # (F:65) 
		('지정일1', 'U8'),  # (F:66) 
		('지정사유2', 'U2'),  # (F:67) 
		('지정일2', 'U8'),  # (F:68) 
		('지정사유3', 'U2'),  # (F:69) 
		('지정일3', 'U8'),  # (F:70) 
		('지정사유4', 'U2'),  # (F:71) 
		('지정일4', 'U8'),  # (F:72) 
		('지정사유5', 'U2'),  # (F:73) 
		('지정일5', 'U8'),  # (F:74) 
		('지정사유6', 'U2'),  # (F:75) 
		('지정일6', 'U8'),  # (F:76) 
		('지수벤처기업구분', 'U1'),  # (F:77) 
		('시가총액구분', 'U1'),  # (F:78) 
		('제조업구분', 'U2'),  # (F:79) 
		('업종중분류', 'U3'),  # (F:80) 
		('업종소분류', 'U3'),  # (F:81) 
		('벤처구분', 'U1'),  # (F:82) 
		('기세구분', 'U1'),  # (F:83) 
		('정리매매여부', 'U1'),  # (F:84) 
		])
	MULTI_OUTPUT_DTYPE = None


class TC(BaseTR):
	NAME, DESCRIPTION = 'TC', 'K-OTC 현재가'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('일련번호', 'U7'),  # (F:00) 
		('표준코드', 'U12'),  # (F:01) 
		('단축코드', 'U6'),  # (F:02) 
		('시간', 'U6'),  # (F:03) 
		('현재가', np.uint32),  # (F:04) 
		('전일대비구분', 'U1'),  # (F:05) 
		('전일대비', np.uint32),  # (F:06) 
		('전일대비율', np.float32),  # (F:07) 
		('매도호가', np.uint32),  # (F:08) 
		('매수호가', np.uint32),  # (F:09) 
		('시가', np.uint32),  # (F:10) 
		('고가', np.uint32),  # (F:11) 
		('저가', np.uint32),  # (F:12) 
		('누적거래량', np.uint64),  # (F:13) 
		('누적거래대금', np.uint64),  # (F:14) 
		('가중평균주가', np.uint32),  # (F:15) 
		('매도총잔량', 'U10'),  # (F:16) 
		('매수총잔량', 'U10'),  # (F:17) 
		('매도우선호가잔량', 'U10'),  # (F:18) 
		('매수우선호가잔량', 'U10'),  # (F:19) 
		('체결번호', 'U6'),  # (F:20) 
		('체결량', 'U12'),  # (F:21) 
		('매도호가번호', 'U6'),  # (F:22) 
		('매수호가번호', 'U6'),  # (F:23) 
		])
	MULTI_OUTPUT_DTYPE = None

class TH(BaseTR):
	NAME, DESCRIPTION = 'TH', 'K-OTC 호가'
	INPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('일련번호', 'U7'),  # (F:00) 
		('표준코드', 'U12'),  # (F:01) 
		('단축코드', 'U6'),  # (F:02) 
		('호가번호', 'U6'),  # (F:03) 
		('접수시각', 'U6'),  # (F:04) 
		('처리구분', 'U1'),  # (F:05) 
		('원호가번호', 'U6'),  # (F:06) 
		('원호가격', np.uint32),  # (F:07) 
		('매도매수구분', 'U1'),  # (F:08) 
		('가격', np.uint32),  # (F:09) 
		('수량', 'U10'),  # (F:10) 
		('증권사번호', 'U5'),  # (F:11) 
		('지점명', 'U12'),  # (F:12) 
		('잔량', 'U10'),  # (F:13) 
		('처리시간', 'U6'),  # (F:14) 
		('매도호가', np.uint32),  # (F:15) 
		('매수호가', np.uint32),  # (F:16) 
		('매도총잔량', 'U10'),  # (F:17) 
		('매수총잔량', 'U10'),  # (F:18) 
		('매도우선호가잔량', 'U10'),  # (F:19) 
		('매수우선호가잔량', 'U10'),  # (F:20) 
		])
	MULTI_OUTPUT_DTYPE = None

class kotc_mst(BaseTR):
	NAME, DESCRIPTION = 'kotc_mst', 'K-OTC 종목정보조회'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('종목명', 'U20'),  # (F:02) 
		('주권심볼', 'U7'),  # (F:03) 
		('산업업종코드', 'U8'),  # (F:04) 
		('상장구분', 'U2'),  # (F:05) 
		('상장일', 'U8'),  # (F:06) 
		('소속구분', 'U2'),  # (F:07) 
		('자본금규모', 'U1'),  # (F:08) 
		('거래정지구분', 'U1'),  # (F:09) 
		('락구분', 'U2'),  # (F:10) 
		('불성실공시지정여부', 'U1'),  # (F:11) 
		('전일가중평균주가', np.uint32),  # (F:12) 
		('결산구분', 'U1'),  # (F:13) 
		('최소구분', 'U1'),  # (F:14) 
		('공모구분', 'U1'),  # (F:15) 
		('공모가', np.uint32),  # (F:16) 
		('지정유형', 'U1'),  # (F:17) 
		('거래부진', 'U1'),  # (F:18) 
		])

class CB(BaseTR):
	NAME, DESCRIPTION = 'CB', '신주인수권 마스터'
	INPUT_DTYPE = np.dtype([
		('단축코드', np.uint32),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', np.uint32),  # (F:01) 
		('일련번호', 'U4'),  # (F:02) 
		('입회일자', 'U8'),  # (F:03) 
		('한글종목명', 'U40'),  # (F:04) 
		('영문종목명', 'U40'),  # (F:05) 
		('주권심볼', 'U7'),  # (F:06) 
		('제조업구분', 'U2'),  # (F:07) 
		('업종중분류', 'U3'),  # (F:08) 
		('업종소분류', 'U3'),  # (F:09) 
		('산업업종코드', 'U6'),  # (F:10) 
		('상장구분', 'U2'),  # (F:11) 
		('상장주식수', np.uint64),  # (F:12) 
		('상장일', 'U8'),  # (F:13) 
		('소속구분', 'U2'),  # (F:14) 
		('자본금규모', 'U1'),  # (F:15) 
		('결산월', 'U2'),  # (F:16) 
		('액면가', np.uint32),  # (F:17) 
		('기준가', np.uint32),  # (F:18) 
		('상한가', np.uint32),  # (F:19) 
		('하한가', np.uint32),  # (F:20) 
		('대용가', np.uint32),  # (F:21) 
		('전일종가', np.uint32),  # (F:22) 
		('전일거래량', np.uint64),  # (F:23) 
		('전일거래대금', np.uint64),  # (F:24) 
		('거래정지구분', 'U1'),  # (F:25) 
		('관리구분', 'U1'),  # (F:26) 
		('감리구분', 'U1'),  # (F:27) 
		('락구분', 'U2'),  # (F:28) 
		('불성실공시지정여부', 'U1'),  # (F:29) 
		('연초일자', 'U8'),  # (F:30) 
		('연초종가', np.uint32),  # (F:31) 
		('연중최고일자', 'U8'),  # (F:32) 
		('연중최고종가', np.uint32),  # (F:33) 
		('연중최저일자', 'U8'),  # (F:34) 
		('연중최저종가', np.uint32),  # (F:35) 
		('최고호가가격', np.uint32),  # (F:36) 
		('최저호가가격', np.uint32),  # (F:37) 
		('평가가격', np.uint32),  # (F:38) 
		('매매구분', 'U1'),  # (F:39) 
		('정리매매시작일', 'U8'),  # (F:40) 
		('정리매매종료일', 'U8'),  # (F:41) 
		('행사가격', np.uint32),  # (F:42) 
		('REITs구분', 'U1'),  # (F:43) 
		('매매수량단위', 'U5'),  # (F:44) 
		('시간외매매수량단위', 'U5'),  # (F:45) 
		('자본금', 'U18'),  # (F:46) 
		('목적주권', 'U12'),  # (F:47) 
		('신주인수권발행가', np.uint32),  # (F:48) 
		('신주인수권상장폐지일', 'U8'),  # (F:49) 
		])
	MULTI_OUTPUT_DTYPE = None

class CC(BaseTR):
	NAME, DESCRIPTION = 'CC', '신주인수권 현재가'
	INPUT_DTYPE = np.dtype([
		('단축코드', np.uint32),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', np.uint32),  # (F:01) 
		('시간', 'U8'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', np.float32),  # (F:06) 
		('매도호가', np.uint32),  # (F:07) 
		('매수호가', np.uint32),  # (F:08) 
		('시가', np.uint32),  # (F:09) 
		('고가', np.uint32),  # (F:10) 
		('저가', np.uint32),  # (F:11) 
		('시가시간', 'U6'),  # (F:12) 
		('고가시간', 'U6'),  # (F:13) 
		('저가시간', 'U6'),  # (F:14) 
		('누적거래량', np.uint64),  # (F:15) 
		('누적거래대금', np.uint64),  # (F:16) 
		('단위체결량', 'U12'),  # (F:17) 
		('매매구분', 'U1'),  # (F:18) 
		('장구분', 'U1'),  # (F:19) 
		('호가체결구분', 'U1'),  # (F:20) 
		])
	MULTI_OUTPUT_DTYPE = None

class CH(BaseTR):
	NAME, DESCRIPTION = 'CH', '신주인수권 호가'
	INPUT_DTYPE = np.dtype([
		('단축코드', np.uint32),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', np.uint32),  # (F:01) 
		('호가접수시간', 'U6'),  # (F:02) 
		('장구분', 'U1'),  # (F:03) 
		('매도1호가', np.uint32),  # (F:04) 
		('매수1호가', np.uint32),  # (F:05) 
		('매도1호가수량', 'U12'),  # (F:06) 
		('매수1호가수량', 'U12'),  # (F:07) 
		('매도2호가', np.uint32),  # (F:08) 
		('매수2호가', np.uint32),  # (F:09) 
		('매도2호가수량', 'U12'),  # (F:10) 
		('매수2호가수량', 'U12'),  # (F:11) 
		('매도3호가', np.uint32),  # (F:12) 
		('매수3호가', np.uint32),  # (F:13) 
		('매도3호가수량', 'U12'),  # (F:14) 
		('매수3호가수량', 'U12'),  # (F:15) 
		('매도4호가', np.uint32),  # (F:16) 
		('매수4호가', np.uint32),  # (F:17) 
		('매도4호가수량', 'U12'),  # (F:18) 
		('매수4호가수량', 'U12'),  # (F:19) 
		('매도5호가', np.uint32),  # (F:20) 
		('매수5호가', np.uint32),  # (F:21) 
		('매도5호가수량', 'U12'),  # (F:22) 
		('매수5호가수량', 'U12'),  # (F:23) 
		('매도6호가', np.uint32),  # (F:24) 
		('매수6호가', np.uint32),  # (F:25) 
		('매도6호가수량', 'U12'),  # (F:26) 
		('매수6호가수량', 'U12'),  # (F:27) 
		('매도7호가', np.uint32),  # (F:28) 
		('매수7호가', np.uint32),  # (F:29) 
		('매도7호가수량', 'U12'),  # (F:30) 
		('매수7호가수량', 'U12'),  # (F:31) 
		('매도8호가', np.uint32),  # (F:32) 
		('매수8호가', np.uint32),  # (F:33) 
		('매도8호가수량', 'U12'),  # (F:34) 
		('매수8호가수량', 'U12'),  # (F:35) 
		('매도9호가', np.uint32),  # (F:36) 
		('매수9호가', np.uint32),  # (F:37) 
		('매도9호가수량', 'U12'),  # (F:38) 
		('매수9호가수량', 'U12'),  # (F:39) 
		('매도10호가', np.uint32),  # (F:40) 
		('매수10호가', np.uint32),  # (F:41) 
		('매도10호가수량', 'U12'),  # (F:42) 
		('매수10호가수량', 'U12'),  # (F:43) 
		('매도총호가수량', 'U12'),  # (F:44) 
		('매수총호가수량', 'U12'),  # (F:45) 
		('시간외매도호가수량', 'U12'),  # (F:46) 
		('시간외매수호가수량', 'U12'),  # (F:47) 
		('동시구분', 'U1'),  # (F:48) 
		('예상체결가격', np.uint32),  # (F:49) 
		('예상체결수량', 'U12'),  # (F:50) 
		])
	MULTI_OUTPUT_DTYPE = None

class TR_5008_5(BaseTR):
	NAME, DESCRIPTION = 'TR_5008_5', '신주인수권 종목 List'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('한글종목명', 'U40'),  # (F:00) 
		('표준코드', 'U12'),  # (F:01) 
		('단축코드', 'U6'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		])

class TR_CCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_CCHART', '신주인수권 차트 데이터'
	INPUT_DTYPE = np.dtype([
		('단축코드', np.uint32),  # (F:00) 
		('그래프종류', 'U1'),  # (F:01) T: 틱데이터 		D:일데이터
		('시간간격', 'U3'),  # (F:02) 001 ~ 999
		('시작일', 'U8'),  # (F:03) YYYYMMDD
		('종료일', 'U8'),  # (F:04) YYYYMMDD
		('조회갯수', 'U4'),  # (F:05) 1 – 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('시간', 'U6'),  # (F:01) 
		('시가', 'U8'),  # (F:02) 
		('고가', 'U8'),  # (F:03) 
		('저가', 'U8'),  # (F:04) 
		('종가', 'U8'),  # (F:05) 
		('주가수정계수', 'U8'),  # (F:06) 
		('거래량수정계수', np.uint64),  # (F:07) 
		('락구분', 'U4'),  # (F:08) 
		('단위거래량', np.uint64),  # (F:09) 
		('단위거래대금', np.uint64),  # (F:10) 
		])

class XB(BaseTR):
	NAME, DESCRIPTION = 'XB', '금현물 마스터'
	INPUT_DTYPE = np.dtype([
		('단축코드', np.uint32),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', np.uint32),  # (F:01) 
		('일련번호', 'U4'),  # (F:02) 
		('입회일자', 'U8'),  # (F:03) 
		('한글종목명', 'U40'),  # (F:04) 
		('영문종목명', 'U40'),  # (F:05) 
		('상장일자', 'U8'),  # (F:06) 
		('상장폐지일자', 'U8'),  # (F:07) 
		('상품ID', 'U10'),  # (F:08) 
		('기준가', np.uint32),  # (F:09) 
		('상한가', np.uint32),  # (F:10) 
		('하한가', np.uint32),  # (F:11) 
		('거래정지구분', 'U1'),  # (F:12) 
		('매매수량단위', 'U6'),  # (F:13) 
		('전일종가', np.uint32),  # (F:14) 
		('대용가', np.uint32),  # (F:15) 
		])
	MULTI_OUTPUT_DTYPE = None

class XC(BaseTR):
	NAME, DESCRIPTION = 'XC', '금현물 현재가'
	INPUT_DTYPE = np.dtype([
		('단축코드', np.uint32),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', np.uint32),  # (F:01) 
		('체결시간', 'U9'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', 'U6'),  # (F:06) 
		('누적거래량', np.uint64),  # (F:07) 
		('누적거래대금', np.uint64),  # (F:08) 
		('단위체결량', 'U10'),  # (F:09) 
		('시가', np.uint32),  # (F:10) 
		('고가', np.uint32),  # (F:11) 
		('저가', np.uint32),  # (F:12) 
		('시가시간', 'U9'),  # (F:13) 
		('고가시간', 'U9'),  # (F:14) 
		('저가시간', 'U9'),  # (F:15) 
		('협의대량매매 누적체결수량', 'U12'),  # (F:16) 
		('체결매도매수구분', 'U1'),  # (F:17) 
		('매도1호가', np.uint32),  # (F:18) 
		('매수1호가', np.uint32),  # (F:19) 
		])
	MULTI_OUTPUT_DTYPE = None

class XH(BaseTR):
	NAME, DESCRIPTION = 'XH', '금현물 호가'
	INPUT_DTYPE = np.dtype([
		('단축코드', np.uint32),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', np.uint32),  # (F:01) 
		('호가접수시간', 'U6'),  # (F:02) 
		('장구분', 'U1'),  # (F:03) 
		('매도1호가', np.uint32),  # (F:04) 
		('매수1호가', np.uint32),  # (F:05) 
		('매도1호가수량', 'U12'),  # (F:06) 
		('매수1호가수량', 'U12'),  # (F:07) 
		('매도2호가', np.uint32),  # (F:08) 
		('매수2호가', np.uint32),  # (F:09) 
		('매도2호가수량', 'U12'),  # (F:10) 
		('매수2호가수량', 'U12'),  # (F:11) 
		('매도3호가', np.uint32),  # (F:12) 
		('매수3호가', np.uint32),  # (F:13) 
		('매도3호가수량', 'U12'),  # (F:14) 
		('매수3호가수량', 'U12'),  # (F:15) 
		('매도4호가', np.uint32),  # (F:16) 
		('매수4호가', np.uint32),  # (F:17) 
		('매도4호가수량', 'U12'),  # (F:18) 
		('매수4호가수량', 'U12'),  # (F:19) 
		('매도5호가', np.uint32),  # (F:20) 
		('매수5호가', np.uint32),  # (F:21) 
		('매도5호가수량', 'U12'),  # (F:22) 
		('매수5호가수량', 'U12'),  # (F:23) 
		('매도6호가', np.uint32),  # (F:24) 
		('매수6호가', np.uint32),  # (F:25) 
		('매도6호가수량', 'U12'),  # (F:26) 
		('매수6호가수량', 'U12'),  # (F:27) 
		('매도7호가', np.uint32),  # (F:28) 
		('매수7호가', np.uint32),  # (F:29) 
		('매도7호가수량', 'U12'),  # (F:30) 
		('매수7호가수량', 'U12'),  # (F:31) 
		('매도8호가', np.uint32),  # (F:32) 
		('매수8호가', np.uint32),  # (F:33) 
		('매도8호가수량', 'U12'),  # (F:34) 
		('매수8호가수량', 'U12'),  # (F:35) 
		('매도9호가', np.uint32),  # (F:36) 
		('매수9호가', np.uint32),  # (F:37) 
		('매도9호가수량', 'U12'),  # (F:38) 
		('매수9호가수량', 'U12'),  # (F:39) 
		('매도10호가', np.uint32),  # (F:40) 
		('매수10호가', np.uint32),  # (F:41) 
		('매도10호가수량', 'U12'),  # (F:42) 
		('매수10호가수량', 'U12'),  # (F:43) 
		('매도총호가수량', 'U12'),  # (F:44) 
		('매수총호가수량', 'U12'),  # (F:45) 
		('동시구분', 'U1'),  # (F:46) 
		('예상체결가격', np.uint32),  # (F:47) 
		('예상체결수량', 'U12'),  # (F:48) 
		('LP매도1호가수량', 'U12'),  # (F:49) 
		('LP매도2호가수량', 'U12'),  # (F:50) 
		('LP매도3호가수량', 'U12'),  # (F:51) 
		('LP매도4호가수량', 'U12'),  # (F:52) 
		('LP매도5호가수량', 'U12'),  # (F:53) 
		('LP매도6호가수량', 'U12'),  # (F:54) 
		('LP매도7호가수량', 'U12'),  # (F:55) 
		('LP매도8호가수량', 'U12'),  # (F:56) 
		('LP매도9호가수량', 'U12'),  # (F:57) 
		('LP매도10호가수량', 'U12'),  # (F:58) 
		('LP매수1호가수량', 'U12'),  # (F:59) 
		('LP매수2호가수량', 'U12'),  # (F:60) 
		('LP매수3호가수량', 'U12'),  # (F:61) 
		('LP매수4호가수량', 'U12'),  # (F:62) 
		('LP매수5호가수량', 'U12'),  # (F:63) 
		('LP매수6호가수량', 'U12'),  # (F:64) 
		('LP매수7호가수량', 'U12'),  # (F:65) 
		('LP매수8호가수량', 'U12'),  # (F:66) 
		('LP매수9호가수량', 'U12'),  # (F:67) 
		('LP매수10호가수량', 'U12'),  # (F:68) 
		])
	MULTI_OUTPUT_DTYPE = None

class TR_GLCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_GLCHART', '금현물 차트데이터'
	INPUT_DTYPE = np.dtype([
		('단축코드', np.uint32),  # (F:00) 
		('그래프 종류', 'U1'),  # (F:01) 
		('시간간격', 'U3'),  # (F:02) 
		('시작일', 'U8'),  # (F:03) 
		('종료일', 'U8'),  # (F:04) 
		('조회갯수', 'U4'),  # (F:05) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:01) 
		('시간', 'U6'),  # (F:02) 
		('시가', 'U8'),  # (F:03) 
		('고가', 'U8'),  # (F:04) 
		('저가', 'U8'),  # (F:05) 
		('현재가', 'U8'),  # (F:06) 
		('단위거래량', np.uint64),  # (F:07) 
		('단위거래대금', np.uint64),  # (F:08) 
		])

class IC(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'IC', '지수 현재가'
	INPUT_DTYPE = np.dtype([
		('지수코드', 'U4'),  # (F:00) 업종코드는 부록 코드표 참조
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) 
		('시간', 'U6'),  # (F:01) 
		('장구분', 'U1'),  # (F:02) 2: 장종료(장종료예상지수종료) 3: 시간외종료  4: 장전예상지수종료 1: 장중
		('현재지수', np.float32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.float32),  # (F:05) 
		('전일대비율', np.float32),  # (F:06) 
		('누적거래량', np.uint64),  # (F:07) 
		('누적거래대금', np.uint64),  # (F:08) 
		('단위체결량', 'U8'),  # (F:09) 
		('시가', np.float32),  # (F:10) 
		('고가', np.float32),  # (F:11) 
		('저가', np.float32),  # (F:12) 
		('고가시간', 'U6'),  # (F:13) 
		('저가시간', 'U6'),  # (F:14) 
		])
	MULTI_OUTPUT_DTYPE = None


class IK(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'IK', 'KOSPI200 실시간 지수'
	INPUT_DTYPE = np.dtype([
		('지수코드', 'U4'),  # (F:00) “2101” K200 고정
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) 
		('시간', 'U8'),  # (F:01) 
		('현재지수', np.float32),  # (F:02) 
		])
	MULTI_OUTPUT_DTYPE = None


class IT(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'IT', '업종 투자자'
	INPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) 업종투자자코드는 부록 코드표 참조
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) 
		('시간', 'U6'),  # (F:01) 
		('매수증권거래량01', np.uint64),  # (F:02) 
		('매수증권거래대금01', np.uint64),  # (F:03) 
		('매도증권거래량01', np.uint64),  # (F:04) 
		('매도증권거래대금01', np.uint64),  # (F:05) 
		('순매수증권거래량01', np.uint64),  # (F:06) 
		('순매수증권거래대금01', np.uint64),  # (F:07) 
		('매수보험거래량02', np.uint64),  # (F:08) 
		('매수보험거래대금02', np.uint64),  # (F:09) 
		('매도보험거래량02', np.uint64),  # (F:10) 
		('매도보험거래대금02', np.uint64),  # (F:11) 
		('순매수보험거래량02', np.uint64),  # (F:12) 
		('순매수보험거래대금02', np.uint64),  # (F:13) 
		('매수투신거래량03', np.uint64),  # (F:14) 
		('매수투신거래대금03', np.uint64),  # (F:15) 
		('매도투신거래량03', np.uint64),  # (F:16) 
		('매도투신거래대금03', np.uint64),  # (F:17) 
		('순매수투신거래량03', np.uint64),  # (F:18) 
		('순매수투신거래대금03', np.uint64),  # (F:19) 
		('매수은행거래량04', np.uint64),  # (F:20) 
		('매수은행거래대금04', np.uint64),  # (F:21) 
		('매도은행거래량04', np.uint64),  # (F:22) 
		('매도은행거래대금04', np.uint64),  # (F:23) 
		('순매수은행거래량04', np.uint64),  # (F:24) 
		('순매수은행거래대금04', np.uint64),  # (F:25) 
		('매수종금거래량05', np.uint64),  # (F:26) 
		('매수종금거래대금05', np.uint64),  # (F:27) 
		('매도종금거래량05', np.uint64),  # (F:28) 
		('매도종금거래대금05', np.uint64),  # (F:29) 
		('순매수종금거래량05', np.uint64),  # (F:30) 
		('순매수종금거래대금05', np.uint64),  # (F:31) 
		('매수기금거래량06', np.uint64),  # (F:32) 
		('매수기금거래대금06', np.uint64),  # (F:33) 
		('매도기금거래량06', np.uint64),  # (F:34) 
		('매도기금거래대금06', np.uint64),  # (F:35) 
		('순매수기금거래량06', np.uint64),  # (F:36) 
		('순매수기금거래대금06', np.uint64),  # (F:37) 
		('매수기타법인거래량07', np.uint64),  # (F:38) 
		('매수기타법인거래대금07', np.uint64),  # (F:39) 
		('매도기타법인거래량07', np.uint64),  # (F:40) 
		('매도기타법인거래대금07', np.uint64),  # (F:41) 
		('순매수기타법인거래량07', np.uint64),  # (F:42) 
		('순매수기타법인거래대금07', np.uint64),  # (F:43) 
		('매수개인거래량08', np.uint64),  # (F:44) 
		('매수개인거래대금08', np.uint64),  # (F:45) 
		('매도개인거래량08', np.uint64),  # (F:46) 
		('매도개인거래대금08', np.uint64),  # (F:47) 
		('순매수개인거래량08', np.uint64),  # (F:48) 
		('순매수개인거래대금08', np.uint64),  # (F:49) 
		('매수외국인거래량09', np.uint64),  # (F:50) 
		('매수외국인거래대금09', np.uint64),  # (F:51) 
		('매도외국인거래량09', np.uint64),  # (F:52) 
		('매도외국인거래대금09', np.uint64),  # (F:53) 
		('순매수외국인거래량09', np.uint64),  # (F:54) 
		('순매수외국인거래대금09', np.uint64),  # (F:55) 
		('매수기관거래량10', np.uint64),  # (F:56) 
		('매수기관거래대금10', np.uint64),  # (F:57) 
		('매도기관거래량10', np.uint64),  # (F:58) 
		('매도기관거래대금10', np.uint64),  # (F:59) 
		('순매수기관거래량10', np.uint64),  # (F:60) 
		('순매수기관거래대금10', np.uint64),  # (F:61) 
		('매수외국인기타거래량11', np.uint64),  # (F:62) 
		('매수외국인기타거래대금11', np.uint64),  # (F:63) 
		('매도외국인기타거래량11', np.uint64),  # (F:64) 
		('매도외국인기타거래대금11', np.uint64),  # (F:65) 
		('순매수외국인기타거래량11', np.uint64),  # (F:66) 
		('순매수외국인기타거래대금11', np.uint64),  # (F:67) 
		('매수국가거래량12', np.uint64),  # (F:68) 
		('매수국가거래대금12', np.uint64),  # (F:69) 
		('매도국가거래량12', np.uint64),  # (F:70) 
		('매도국가거래대금12', np.uint64),  # (F:71) 
		('순매수국가거래량12', np.uint64),  # (F:72) 
		('순매수국가거래대금12', np.uint64),  # (F:73) 
		('매수사모펀드거래량13', np.uint64),  # (F:74) 
		('매수사모펀드거래대금13', np.uint64),  # (F:75) 
		('매도사모펀드거래대금13', np.uint64),  # (F:76) 
		('매수외국인기타거래대금13', np.uint64),  # (F:77) 
		('순매수사모펀드거래량13', np.uint64),  # (F:78) 
		('순매수사모펀드거래대금13', np.uint64),  # (F:79) 
		])
	MULTI_OUTPUT_DTYPE = None

class TR_1202_A(BaseTR):
	NAME, DESCRIPTION = 'TR_1202_A', '업종 투자자 시간대별 – 거래량'
	INPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) “0001”:거래소, “1001”:코스닥,  “0999”:선  물, “1999”:코스닥 선물, “0996”:콜옵션, “0995”:풋옵션 “9996” : 주식선물 “7999”: CME 선물
		('시장분류', 'U2'),  # (F:01) 01 : 거래소 대금    02 : 코스닥 대금 03 : K200선물수량   09 : K200콜수량 10 : K200풋수량     06 : 거래소 수량 07 : 코스닥 수량    08 : K200선물대금 04 : K200콜대금     05 : K200풋대금 11 : 스타선물수량   12 : 스타선물대금 13 : 주식선물수량   14 : 주식선물대금 15 : CME 선물
		('조회방법', 'U1'),  # (F:02) “1”: 전체조회, “”: 30개조회
		('시간간격', 'U3'),  # (F:03) “001”:틱, “005”:5분, “010”:10분
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('시간', 'U6'),  # (F:00) 
		('매수개인거래량08', np.uint64),  # (F:01) 
		('매도개인거래량08', np.uint64),  # (F:02) 
		('순매수개인거래량08', np.uint64),  # (F:03) 
		('매수외국인거래량09', np.uint64),  # (F:04) 
		('매도외국인거래량09', np.uint64),  # (F:05) 
		('순매수외국인거래량09', np.uint64),  # (F:06) 
		('매수기관거래량10', np.uint64),  # (F:07) 
		('매도기관거래량10', np.uint64),  # (F:08) 
		('순매수기관거래량10', np.uint64),  # (F:09) 
		('매수증권거래량01', np.uint64),  # (F:10) 
		('매도증권거래량01', np.uint64),  # (F:11) 
		('순매수증권거래량01', np.uint64),  # (F:12) 
		('매수투신거래량03', np.uint64),  # (F:13) 
		('매도투신거래량03', np.uint64),  # (F:14) 
		('순매수투신거래량03', np.uint64),  # (F:15) 
		('매수은행거래량04', np.uint64),  # (F:16) 
		('매도은행거래량04', np.uint64),  # (F:17) 
		('순매수은행거래량04', np.uint64),  # (F:18) 
		('매수종금거래량05', np.uint64),  # (F:19) 
		('매도종금거래량05', np.uint64),  # (F:20) 
		('순매수종금거래량05', np.uint64),  # (F:21) 
		('매수보험거래량02', np.uint64),  # (F:22) 
		('매도보험거래량02', np.uint64),  # (F:23) 
		('순매수보험거래량02', np.uint64),  # (F:24) 
		('매수기금거래량06', np.uint64),  # (F:25) 
		('매도기금거래량06', np.uint64),  # (F:26) 
		('순매수기금거래량06', np.uint64),  # (F:27) 
		('매수기타법인거래량07', np.uint64),  # (F:28) 
		('매도기타법인거래량07', np.uint64),  # (F:29) 
		('순매수기타법인거래량07', np.uint64),  # (F:30) 
		('매수외국인기타거래량11', np.uint64),  # (F:31) 
		('매도외국인기타거래량11', np.uint64),  # (F:32) 
		('순매수외국인기타거래량11', np.uint64),  # (F:33) 
		('매수선물업자거래량12', np.uint64),  # (F:34) 
		('매도선물업자거래량12', np.uint64),  # (F:35) 
		('순매수선물업자거래량12', np.uint64),  # (F:36) 
		('매수사모펀드거래량21', np.uint64),  # (F:37) 
		('매도사모펀드거래량21', np.uint64),  # (F:38) 
		('순매수사모펀드거래량21', np.uint64),  # (F:39) 
		('시간2', 'U6'),  # (F:40) 
		('현재지수', 'U12'),  # (F:41) 
		])

class TR_1202_B(BaseTR):
	NAME, DESCRIPTION = 'TR_1202_B', '업종 투자자 시간대별 – 거래대금'
	INPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) “0001”:거래소, “1001”:코스닥,  “0999”:선  물, “1999”:코스닥 선물, “0996”:콜옵션, “0995”:풋옵션 “9996” : 주식선물 “7999”: CME 선물
		('시장분류', 'U2'),  # (F:01) 01 : 거래소 대금    02 : 코스닥 대금 03 : K200선물수량   09 : K200콜수량 10 : K200풋수량     06 : 거래소 수량 07 : 코스닥 수량    08 : K200선물대금 04 : K200콜대금     05 : K200풋대금 11 : 스타선물수량   12 : 스타선물대금 13 : 주식선물수량   14 : 주식선물대금 15 : CME 선물
		('조회방법', 'U1'),  # (F:02) “1”: 전체조회, “”: 30개조회
		('시간간격', 'U3'),  # (F:03) “001”:틱, “005”:5분, “010”:10분
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('시간', 'U6'),  # (F:00) 
		('매수개인거래대금08', np.uint64),  # (F:01) 
		('매도개인거래대금08', np.uint64),  # (F:02) 
		('순매수개인거래대금08', np.uint64),  # (F:03) 
		('매수외국인거래대금09', np.uint64),  # (F:04) 
		('매도외국인거래대금09', np.uint64),  # (F:05) 
		('순매수외국인거래대금09', np.uint64),  # (F:06) 
		('매수기관거래대금10', np.uint64),  # (F:07) 
		('매도기관거래대금10', np.uint64),  # (F:08) 
		('순매수기관거래대금10', np.uint64),  # (F:09) 
		('매수증권거래대금01', np.uint64),  # (F:10) 
		('매도증권거래대금01', np.uint64),  # (F:11) 
		('순매수증권거래대금01', np.uint64),  # (F:12) 
		('매수투신거래대금03', np.uint64),  # (F:13) 
		('매도투신거래대금03', np.uint64),  # (F:14) 
		('순매수투신거래대금03', np.uint64),  # (F:15) 
		('매수은행거래대금04', np.uint64),  # (F:16) 
		('매도은행거래대금04', np.uint64),  # (F:17) 
		('순매수은행거래대금04', np.uint64),  # (F:18) 
		('매수종금거래대금05', np.uint64),  # (F:19) 
		('매도종금거래대금05', np.uint64),  # (F:20) 
		('순매수종금거래대금05', np.uint64),  # (F:21) 
		('매수보험거래대금02', np.uint64),  # (F:22) 
		('매도보험거래대금02', np.uint64),  # (F:23) 
		('순매수보험거래대금02', np.uint64),  # (F:24) 
		('매수기금거래대금06', np.uint64),  # (F:25) 
		('매도기금거래대금06', np.uint64),  # (F:26) 
		('순매수기금거래대금06', np.uint64),  # (F:27) 
		('매수기타법인거래대금07', np.uint64),  # (F:28) 
		('매도기타법인거래대금07', np.uint64),  # (F:29) 
		('순매수기타법인거래대금07', np.uint64),  # (F:30) 
		('매수외국인기타거래대금11', np.uint64),  # (F:31) 
		('매도외국인기타거래대금11', np.uint64),  # (F:32) 
		('순매수외국인기타거래대금11', np.uint64),  # (F:33) 
		('매수선물업자거래대금12', np.uint64),  # (F:34) 
		('매도선물업자거래대금12', np.uint64),  # (F:35) 
		('순매수선물업자거래대금12', np.uint64),  # (F:36) 
		('매수사모펀드거래대금21', np.uint64),  # (F:37) 
		('매도사모펀드거래대금21', np.uint64),  # (F:38) 
		('순매수사모펀드거래대금21', np.uint64),  # (F:39) 
		('시간2', 'U6'),  # (F:40) 
		('현재지수', np.uint64),  # (F:41) 
		])

class TR_1203(BaseTR):
	NAME, DESCRIPTION = 'TR_1203', '일자별 투자자'
	INPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) “0001”:거래소, “1001”:코스닥,  “0999”:선  물, “1999”:코스닥 선물, “0996”:콜옵션, “0995”:풋옵션 “9996” : 주식선물 “7999”: CME 선물
		('분류', 'U2'),  # (F:01) 01 : 거래소 대금    02 : 코스닥 대금 03 : K200선물수량   09 : K200콜수량 10 : K200풋수량     06 : 거래소 수량 07 : 코스닥 수량    08 : K200선물대금 04 : K200콜대금     05 : K200풋대금 11 : 스타선물수량   12 : 스타선물대금 13 : 주식선물수량   14 : 주식선물대금 15 : CME 선물
		('시작일', 'U8'),  # (F:02) 
		('종료일', 'U8'),  # (F:03) 
		('구분', 'U1'),  # (F:04) 사용안함
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = None

class TR_1205(BaseTR):
	NAME, DESCRIPTION = 'TR_1205', '업종별 투자자'
	INPUT_DTYPE = np.dtype([
		('업종분류', 'U1'),  # (F:00) ‘0’:거래소 대금, ‘1’:코스닥 대금 ‘2’:거래소 수량, ‘3’:코스닥 수량 (억/천주)
		('시작일자', 'U8'),  # (F:01) 
		('종료일자', 'U8'),  # (F:02) 
		('언어구분', 'U1'),  # (F:03) K 고정
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('한글종목명', 'U20'),  # (F:00) 
		('개인매수거래대금', np.uint64),  # (F:01) 
		('개인매도거래대금', np.uint64),  # (F:02) 
		('개인순매수거래대금', np.uint64),  # (F:03) 
		('외국인매수거래대금', np.uint64),  # (F:04) 
		('외국인매도거래대금', np.uint64),  # (F:05) 
		('외국인순매수거래대금', np.uint64),  # (F:06) 
		('기관매수거래대금', np.uint64),  # (F:07) 
		('기관매도거래대금', np.uint64),  # (F:08) 
		('기관순매수거래대금', np.uint64),  # (F:09) 
		('증권매수거래대금', np.uint64),  # (F:10) 
		('증권매도거래대금', np.uint64),  # (F:11) 
		('증권순매수거래대금', np.uint64),  # (F:12) 
		('투신매수거래대금', np.uint64),  # (F:13) 
		('투신매도거래대금', np.uint64),  # (F:14) 
		('투신순매수거래대금', np.uint64),  # (F:15) 
		('은행매수거래대금', np.uint64),  # (F:16) 
		('은행매도거래대금', np.uint64),  # (F:17) 
		('은행순매수거래대금', np.uint64),  # (F:18) 
		('종금매수거래대금', np.uint64),  # (F:19) 
		('종금매도거래대금', np.uint64),  # (F:20) 
		('종금순매수거래대금', np.uint64),  # (F:21) 
		('보험매수거래대금', np.uint64),  # (F:22) 
		('보험매도거래대금', np.uint64),  # (F:23) 
		('보험순매수거래대금', np.uint64),  # (F:24) 
		('기금매수거래대금', np.uint64),  # (F:25) 
		('기금매도거래대금', np.uint64),  # (F:26) 
		('기금순매수거래대금', np.uint64),  # (F:27) 
		('기타매수거래대금', np.uint64),  # (F:28) 
		('기타매도거래대금', np.uint64),  # (F:29) 
		('기타순매수거래대금', np.uint64),  # (F:30) 
		('외국인기타매수거래대금', np.uint64),  # (F:31) 
		('외국인기타매도거래대금', np.uint64),  # (F:32) 
		('외국인기타순매수거래대금', np.uint64),  # (F:33) 
		('외국인계매수거래대금', np.uint64),  # (F:34) 
		('외국인계매도거래대금', np.uint64),  # (F:35) 
		('외국인계순매수거래대금', np.uint64),  # (F:36) 
		('매수사모펀드거래대금', np.uint64),  # (F:37) 
		('매도사모펀드거래대금', np.uint64),  # (F:38) 
		('순매수사모펀드거래대금', np.uint64),  # (F:39) 
		('국가매수거래대금', np.uint64),  # (F:40) 
		('국가매도거래대금', np.uint64),  # (F:41) 
		('국가순매수거래대금', np.uint64),  # (F:42) 
		])

class TR_1206(BaseTR):
	NAME, DESCRIPTION = 'TR_1206', '종목별 투자자'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('시작일', 'U8'),  # (F:01) Ex>20080101
		('종료일', 'U8'),  # (F:02) Ex>20080912
		('조회구분', 'U1'),  # (F:03) “1” : 전체, “”:60개
		('데이터 종류 구분', 'U1'),  # (F:04) 0:거래량 		1:거래대금
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = None

class SS(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'SS', '프로그램매매 전체합계'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) 0:KOSPI            1:KOSDAQ
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) 
		('일자', 'U8'),  # (F:01) 
		('시간', 'U6'),  # (F:02) 
		('차익매도호가잔량', 'U12'),  # (F:03) 
		('차익매수호가잔량', 'U12'),  # (F:04) 
		('비차익매도호가잔량', 'U12'),  # (F:05) 
		('비차익매수호가잔량', 'U12'),  # (F:06) 
		('차익매도호가수량', 'U12'),  # (F:07) 
		('차익매수호가수량', 'U12'),  # (F:08) 
		('비차익매도호가수량', 'U12'),  # (F:09) 
		('비차익매수호가수량', 'U12'),  # (F:10) 
		('차익매도위탁체결수량', 'U12'),  # (F:11) 
		('차익매도자기체결수량', 'U12'),  # (F:12) 
		('차익매수위탁체결수량', 'U12'),  # (F:13) 
		('차익매수자기체결수량', 'U12'),  # (F:14) 
		('비차익매도위탁체결수량', 'U12'),  # (F:15) 
		('비차익매도자기체결수량', 'U12'),  # (F:16) 
		('비차익매수위탁체결수량', 'U12'),  # (F:17) 
		('비차익매수자기체결수량', 'U12'),  # (F:18) 
		('차익매도위탁체결금액', np.uint64),  # (F:19) 
		('차익매도자기체결금액', np.uint64),  # (F:20) 
		('차익매수위탁체결금액', np.uint64),  # (F:21) 
		('차익매수자기체결금액', np.uint64),  # (F:22) 
		('비차익매도위탁체결금액', np.uint64),  # (F:23) 
		('비차익매도자기체결금액', np.uint64),  # (F:24) 
		('비차익매수위탁체결금액', np.uint64),  # (F:25) 
		('비차익매수자기체결금액', np.uint64),  # (F:26) 
		])
	MULTI_OUTPUT_DTYPE = None

class TR_ICHART(BaseTR):
	NAME, DESCRIPTION = 'TR_ICHART', 'KOSPI200 지수 분/일 데이터'
	INPUT_DTYPE = np.dtype([
		('업종구분', 'U4'),  # (F:00) ‘2101’
		('그래프 종류', 'U1'),  # (F:01) 1:분데이터 		D:일데이터
		('시간간격', 'U3'),  # (F:02) 분데이터일 경우 1 – 5 일데이터일 경우 1
		('시작일', 'U8'),  # (F:03) YYYYMMDD 분 데이터 요청시 : “00000000”
		('종료일', 'U8'),  # (F:04) YYYYMMDD 분 데이터 요청시 : “99999999”
		('조회갯수', 'U4'),  # (F:05) 1 – 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('시간', 'U6'),  # (F:01) 
		('시가', np.float32),  # (F:02) 
		('고가', np.float32),  # (F:03) 
		('저가', np.float32),  # (F:04) 
		('현재가', np.float32),  # (F:05) 
		('단위거래량', np.uint64),  # (F:06) 
		('단위거래대금', np.uint64),  # (F:07) 
		])

class TR4_1500(BaseTR):
	NAME, DESCRIPTION = 'TR4_1500', '데마 그룹 조회'
	INPUT_DTYPE = np.dtype([
		('테마코드', 'U50'),  # (F:00) 빈칸: 전체
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('테마코드', 'U4'),  # (F:00) 
		('테마명', 'U50'),  # (F:01) 
		('평균상승', 'U6'),  # (F:02) 
		('종목수', 'U8'),  # (F:03) 
		('상승종목수', 'U8'),  # (F:04) 
		('보합종목수', 'U8'),  # (F:05) 
		('하락종목수', 'U8'),  # (F:06) 
		('시가총액', 'U8'),  # (F:07) 
		('5일등락율', 'U8'),  # (F:08) 
		])

class TR4_1500_1(BaseTR):
	NAME, DESCRIPTION = 'TR4_1500_1', '테마종목리스트'
	INPUT_DTYPE = np.dtype([
		('테마코드', 'U4'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('테마개요', 'U300'),  # (F:00) 
		])
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		('전일대비', np.uint32),  # (F:04) 
		('전일대비율', 'U4'),  # (F:05) 
		('거래량', np.uint32),  # (F:06) 
		('EPS', np.uint32),  # (F:07) 
		('PER', np.uint32),  # (F:08) 
		('거래강도', np.uint32),  # (F:09) 
		('종목구분', 'U4'),  # (F:10) 
		])

class TR4_1502_3(BaseTR):
	NAME, DESCRIPTION = 'TR4_1502_3', '테마별평균상승률순위조회'
	INPUT_DTYPE = np.dtype([
		('시작일', 'U8'),  # (F:00) 
		('종료일', 'U8'),  # (F:01) 
		('테마명', 'U20'),  # (F:02) 빈칸: 전체
		('일자', 'U8'),  # (F:03) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('테마코드', 'U4'),  # (F:00) 
		('테마명', 'U20'),  # (F:01) 
		('평균상승률', np.uint32),  # (F:02) 
		])

class upjong_mst(BaseTR):
	NAME, DESCRIPTION = 'upjong_mst', '거래소 업종 마스터'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U1'),  # (F:00) 1:KOSPI		2:KOSDAQ 3:KOSPI200      4:KOSDAQ50 5:KRX
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) 
		('업종명', 'U0'),  # (F:01) 
		])

class upjong_code_mst(BaseTR):
	NAME, DESCRIPTION = 'upjong_code_mst', '업종 종목 리스트'
	INPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) 7.1 업종코드 참고
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U0'),  # (F:01) 
		])

class stock_code(BaseTR):
	NAME, DESCRIPTION = 'stock_code', '현물 종목 정보 조회(개별)'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('장구분', 'U1'),  # (F:02) 0:KOSPI			1:KOSDAQ
		('종목명', 'U40'),  # (F:03) 
		('KOSPI200 세부업종', 'U1'),  # (F:04) 0:미분류, 1:제조업, 2:전기통신, 3:건설, 4:유통서비스, 5:금융
		('결산월일', 'U4'),  # (F:05) 상장사의 회계결산일(12월31일, 6월30일, 3월31일) 결산기나 결산월일 경우는 12월일 경우 '1200'로 표시
		('거래정지구분', 'U1'),  # (F:06) 0:정상	  1:정지    5:CB발동
		('관리구분', 'U1'),  # (F:07) 0:정상			1:관리
		('시장경보구분코드', 'U1'),  # (F:08) 0:정상, 1:주의, 2:경고, 3:위험
		('락구분', 'U2'),  # (F:09) 00:발생안함,  01:권리락, 02:배당락, 03:분배락,   04:권배락, 05:중간배당락,  06:권리중간배당락, 99:기타,  ※미해당의 경우 Space
		('불성실공시지정여부', 'U1'),  # (F:10) 
		('소속구분', 'U2'),  # (F:11) ST:주식, MF:증권투자회사, RT:리츠, SC:선박투자회사, IF:인프라투융자회사, DR:예탁증서, SW:신주인수권증권, SR:신주인수권증서, BW:주식워런트증권(ELW), FU:선물, OP:옵션, EF:상장지수펀드(ETF), BC:수익증권, FE:해외ETF, FS:해외원주, EN: ETN
		])

class fut_mst(BaseTR):
	NAME, DESCRIPTION = 'fut_mst', 'KOSPI 선물 종목 정보 조회'
	INPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('종목명', 'U30'),  # (F:02) “KOSPI 200 선물 XXXX”
		('축약종목명', 'U15'),  # (F:03) “F XXXX”
		('종목보조코드', 'U6'),  # (F:04) YYYYMM
		('스프레드근월물표준코드', 'U12'),  # (F:05) 
		('스프레드원월물표준코드', 'U12'),  # (F:06) 
		('최종거래일', 'U8'),  # (F:07) 
		('기초자산코드', 'U2'),  # (F:08) 
		('거래승수', 'U8'),  # (F:09) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, False
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = None

class opt_mst(BaseTR):
	NAME, DESCRIPTION = 'opt_mst', 'KOSPI 옵션 종목 정보 조회'
	INPUT_DTYPE = np.dtype([
		('구분코드', 'U1'),  # (F:00) 0:전종목 		1: 최근월물 2:차근월물		3:차차근월물 4:차차차월물
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('종목명', 'U30'),  # (F:02) 
		('옵션종류', 'U1'),  # (F:03) 2:콜옵션		3:풋옵션
		('ATM구분', 'U1'),  # (F:04) 1:ATM			2:ITM 3:OTM
		])

class elw_mst(BaseTR):
	NAME, DESCRIPTION = 'elw_mst', 'ELW 종목 정보 조회(전종목)'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('종목명', 'U40'),  # (F:02) 
		('행사가', 'U12'),  # (F:03) 
		('기초자산1', 'U6'),  # (F:04) 
		('기초자산2', 'U6'),  # (F:05) 
		('기초자산3', 'U6'),  # (F:06) 
		('기초자산4', 'U6'),  # (F:07) 
		('기초자산5', 'U6'),  # (F:08) 
		('발생사명', 'U40'),  # (F:09) 
		('최종일', 'U8'),  # (F:10) 
		('LP코드', 'U5'),  # (F:11) *7.3절의 거래원번호 참조
		('콜풋', 'U2'),  # (F:12) “01”:콜, “02”:풋
		])

class elw_code(BaseTR):
	NAME, DESCRIPTION = 'elw_code', 'ELW 종목 정보 조회(개별)'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('종목명', 'U40'),  # (F:02) 
		('행사가', 'U12'),  # (F:03) 
		('기초자산1', 'U6'),  # (F:04) 
		('기초자산2', 'U6'),  # (F:05) 
		('기초자산3', 'U6'),  # (F:06) 
		('기초자산4', 'U6'),  # (F:07) 
		('기초자산5', 'U6'),  # (F:08) 
		('발생사명', 'U40'),  # (F:09) 
		('최종일', 'U8'),  # (F:10) 
		('LP코드', 'U5'),  # (F:11) *7.3절의 거래원번호 참조
		('콜풋', 'U2'),  # (F:12) “01”:콜, “02”:풋
		])

class sfut_mst(BaseTR):
	NAME, DESCRIPTION = 'sfut_mst', '주식선물 종목 정보 조회(전종목)'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('종목명', 'U50'),  # (F:02) 
		('축약종목명', 'U15'),  # (F:03) 
		('종목보조코드', 'U6'),  # (F:04) 
		('스프레드근월물표준코드', 'U12'),  # (F:05) 
		('스프레드원월물표준코드', 'U12'),  # (F:06) 
		('최종거래일', 'U8'),  # (F:07) 
		('기초자산코드', 'U6'),  # (F:08) 
		('시장조성종목여부', 'U1'),  # (F:09) 
		])

class TR_3100_D(BaseTR):
	NAME, DESCRIPTION = 'TR_3100_D', '뉴스제목 목록조회'
	INPUT_DTYPE = np.dtype([
		('뉴스_종목코드', 'U6'),  # (F:00) “055550”
		('구분', 'U1'),  # (F:01) “1”:전체, “2”:뉴스, “3”:공시
		('조회일자', 'U8'),  # (F:02) “20070425”
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('뉴스_일자', 'U8'),  # (F:00) 
		('뉴스_입력시간', 'U6'),  # (F:01) 
		('뉴스_제목', 'U'),  # (F:02) 
		('뉴스_구분', 'U1'),  # (F:03) A=[인포], M=[MT], E=[ED], Y=[연합], H=[한경], I=[내부], F=[시황], P=[공시], Q=[공시], S=[공시], G=[공시], N=[공시], T=[공시], U=[해외]
		('뉴스_기사번호', 'U'),  # (F:04) 
		])

class TR_3100(BaseTR):
	NAME, DESCRIPTION = 'TR_3100', '뉴스 내용조회'
	INPUT_DTYPE = np.dtype([
		('뉴스_구분', 'U6'),  # (F:00) *목록조회에서 받은 내용
		('뉴스_일자', 'U8'),  # (F:01) *목록조회에서 받은 내용
		('뉴스_기사번호', 'U'),  # (F:02) *목록조회에서 받은 내용
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('뉴스_구분', 'U1'),  # (F:00) A=[인포], M=[MT], E=[ED], Y=[연합], H=[한경], I=[내부], F=[시황], P=[공시], Q=[공시], S=[공시], G=[공시], N=[공시], T=[공시], U=[해외]
		('뉴스_일자', 'U8'),  # (F:01) 
		('뉴스_입력시간', 'U6'),  # (F:02) 
		('검색엔진추출종목코드', 'U'),  # (F:03) 받은 데이터를 6자리씩 자르면 종목코드입니다. Ex>005930000660000100
		('뉴스_내용', 'U'),  # (F:04) 
		('뉴스_내용1', 'U'),  # (F:05) 뉴스 내용이 긴 경우 추가분
		('뉴스_내용2', 'U'),  # (F:06) 뉴스 내용이 긴 경우 추가분
		])

class TR_INCHART(BaseTR):
	NAME, DESCRIPTION = 'TR_INCHART', '해외지수, 환율 분/일/주/월 데이터'
	INPUT_DTYPE = np.dtype([
		('심벌', 'U6'),  # 해외주요지수,환율 심벌 테이블 참고
		('그래프종류', 'U1'),  # 1:분데이터 (지수만) D:일데이터  W:주데이터	M:월데이터
		('시간간격', 'U3'),  #  분데이터일 경우 5, 30  일/주/월데이터일 경우 1
		('시작일', 'U8'),  # YYYYMMDD   분 데이터 요청시 : “00000000”
		('종료일', 'U8'),  # YYYYMMDD   분 데이터 요청시 : “99999999”
		('조회갯수', 'U4')	#  1 – 9999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),
		('시간', 'U6'),
		('시가', np.uint32),
		('고가', np.uint32),
		('저가', np.uint32),
		('종가', np.uint32),
		('단위거래량', np.uint32)
	])

class TR_1451(BaseTR):
	NAME, DESCRIPTION = 'TR_1451', '프로그램매매 – 시간/일자별 조회'
	INPUT_DTYPE = np.dtype([
		('업종구분', 'U1'),  # (F:00) 0: 거래소, 1:코스닥
		('시간구분', 'U1'),  # (F:01) T:시간대별, D:일자별
		('단위구분', 'U1'),  # (F:02) 1:금액(백만원) 2:수량(주)
		('시작일', 'U8'),  # (F:03) 20081023(일자별만 유효)
		('종료일', 'U8'),  # (F:04) 20081023(일자별만 유효)
		('전체여부', 'U1'),  # (F:05) 0:최근데이터, 1:전체데이터
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('시간/일자', 'U8'),  # (F:00) 
		('차익매도', np.uint64),  # (F:01) 
		('차익매수', np.uint64),  # (F:02) 
		('비차익매도', np.uint64),  # (F:03) 
		('비차익매수', np.uint64),  # (F:04) 
		('전체매도', np.uint64),  # (F:05) 
		('전체매수', np.uint64),  # (F:06) 
		('전체순매수', np.uint64),  # (F:07) 
		('현재지수', 'U'),  # (F:08) 
		('전일대비구분', 'U'),  # (F:09) 상한(1)상승(2)보합(3)하한(4)하락(5)기세상한(6)기세상승(7)기세하한(8)기세하한(9)
		('전일대비', 'U'),  # (F:10) 
		('자료구분', 'U'),  # (F:11) “X”
		('누적순매수', 'U'),  # (F:12) 
		])

class TR_1452(BaseTR):
	NAME, DESCRIPTION = 'TR_1452', '프로그램매매 – 차익거래잔고'
	INPUT_DTYPE = np.dtype([
		('거래원번호', 'U4'),  # (F:00) 7.3 거래원번호 참고 ※ 전체 : “99997”
		('조회일자', 'U8'),  # (F:01) 20090225
		('단위구분', 'U1'),  # (F:02) 1:금액(백만원) 2:수량(주)
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('매도주식거래량', np.uint64),  # (F:01) 
		('매도주식증감', np.uint64),  # (F:02) 
		('매도선물계약수량', np.uint64),  # (F:03) 
		('매도선물증감', np.uint64),  # (F:04) 
		('매수주식거래량', np.uint64),  # (F:05) 
		('매수주식증감', np.uint64),  # (F:06) 
		('매수선물계약수량', np.uint64),  # (F:07) 
		('매수선물증감', np.uint64),  # (F:08) 
		])


class TR_1303(BaseTR):
	NAME, DESCRIPTION = 'TR_1303', '회원사 일자별 매매 데이터 조회'
	INPUT_DTYPE = np.dtype([
		('종목코드', 'U6'),  # (F:00) “005930”
		('회원사코드', 'U5'),  # (F:01) 7.3 거래원 코드 참조
		('조회구분', 'U1'),  # (F:02) “D”
		('시작일자', 'U8'),  # (F:03) “20090909” ** 최대 90일 가능 **
		('종료일자', 'U8'),  # (F:04) “20090909” ** 최대 90일 가능 **
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = None


class SP(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'SP', '프로그램매매 종목별 조회'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) “005930”
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('일자', 'U8'),  # (F:02) 
		('시간', 'U6'),  # (F:03) 
		('차익매도호가잔량', 'U12'),  # (F:04) 
		('차익매수호가잔량', 'U12'),  # (F:05) 
		('비차익매도호가잔량', 'U12'),  # (F:06) 
		('비차익매수호가잔량', 'U12'),  # (F:07) 
		('차익매도호가수량', 'U12'),  # (F:08) 
		('차익매수호가수량', 'U12'),  # (F:09) 
		('비차익매도호가수량', 'U12'),  # (F:10) 
		('비차익매수호가수량', 'U12'),  # (F:11) 
		('매도위탁체결수량', 'U12'),  # (F:12) 
		('매도자기체결수량', 'U12'),  # (F:13) 
		('매수위탁체결수량', 'U12'),  # (F:14) 
		('매수자기체결수량', 'U12'),  # (F:15) 
		('매도위탁체결금액', 'U12'),  # (F:16) 
		('매도자기체결금액', 'U12'),  # (F:17) 
		('매수위탁체결금액', 'U12'),  # (F:18) 
		('매수자기체결금액', 'U12'),  # (F:19) 
		('매도사전공시수량', 'U12'),  # (F:20) 
		('매수사전공시수량', 'U12'),  # (F:21) 
		('매도공시사전정정수량', 'U12'),  # (F:22) 
		('매수공시사전정정수량', 'U12'),  # (F:23) 
		('사후공시매도수량', 'U12'),  # (F:24) 
		('사후공시매수수량', 'U12'),  # (F:25) 
		('차익매도위탁체결수량', 'U12'),  # (F:26) 
		('차익매도자기체결수량', 'U12'),  # (F:27) 
		('차익매수위탁체결수량', 'U12'),  # (F:28) 
		('차익매수자기체결수량', 'U12'),  # (F:29) 
		('비차익매도위탁체결수량', 'U12'),  # (F:30) 
		('비차익매도자기체결수량', 'U12'),  # (F:31) 
		('비차익매수위탁체결수량', 'U12'),  # (F:32) 
		('비차익매수자기체결수량', 'U12'),  # (F:33) 
		('차익매도위탁체결금액', 'U12'),  # (F:34) 
		('차익매도자기체결금액', 'U12'),  # (F:35) 
		('차익매수위탁체결금액', 'U12'),  # (F:36) 
		('차익매수자기체결금액', 'U12'),  # (F:37) 
		('비차익매도위탁체결금액', 'U12'),  # (F:38) 
		])
	MULTI_OUTPUT_DTYPE = None

class ID(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'ID', '지수 등락'
	INPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) 업종코드는 부록 코드표 참조
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('업종코드', 'U4'),  # (F:00) 
		('시간', 'U6'),  # (F:01) 
		('장구분', 'U1'),  # (F:02) 
		('전체종목수', 'U4'),  # (F:03) 
		('거래형성종목수', 'U4'),  # (F:04) 
		('상승종목수', 'U4'),  # (F:05) 
		('상한종목수', 'U4'),  # (F:06) 
		('하락종목수', 'U4'),  # (F:07) 
		('하한종목수', 'U4'),  # (F:08) 
		('보합종목수', 'U4'),  # (F:09) 
		('기세형성종목수', 'U4'),  # (F:10) 
		('기세상승종목수', 'U4'),  # (F:11) 
		('기세하락종목수', 'U4'),  # (F:12) 
		])
	MULTI_OUTPUT_DTYPE = None

class TR_5300_4(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'TR_5300_4', '선물 실시간 주문체결 조회 (고객용)'
	INPUT_DTYPE = np.dtype([
		('계좌수', 'U3'),  # (F:00) 계좌번호리스트의 개수
		('종목코드', 'U12'),  # (F:01) 전체조회시 SPACE
		('매매구분', 'U1'),  # (F:02) 0:전체			1:매도 2:매수
		('계좌번호리스트', 'U1024'),  # (F:03) 계좌번호 최대 200개
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('처리구분', 'U2'),  # (F:00) 00:정상주문 		01:정정주문 	 02:취소주문 		03:체결 04:정정확인 		05:취소확인  09:주문거부
		('지점번호', 'U3'),  # (F:01) 
		('계좌번호', 'U11'),  # (F:02) 
		('시장구분', 'U2'),  # (F:03) 1:KOSPI			2:KOSDAQ 3:선물/옵션/개별주식	4:제3시장 5:ECN			6:KOFEX
		('상품구분', 'U2'),  # (F:04) 
		('주문번호', 'U7'),  # (F:05) 
		('원주문번호', 'U7'),  # (F:06) 
		('주문구분', 'U2'),  # (F:07) 
		('매도매수구분', 'U2'),  # (F:08) 
		('상태', 'U2'),  # (F:09) 
		('종목코드2', 'U12'),  # (F:10) 
		('종목명', 'U20'),  # (F:11) 
		('계좌명', 'U20'),  # (F:12) 
		('주문수량', 'U8'),  # (F:13) 
		('주문가격', np.uint32),  # (F:14) 
		('접수시간', 'U8'),  # (F:15) 
		('체결번호', 'U7'),  # (F:16) 
		('체결수량', 'U8'),  # (F:17) 
		('체결단가', 'U10'),  # (F:18) 
		('체결시간', 'U8'),  # (F:19) 
		('채널', 'U2'),  # (F:20) 
		('입력자', 'U12'),  # (F:21) 
		('관리자', 'U12'),  # (F:22) 
		('일련번호', 'U8'),  # (F:23) 
		('체결금액', 'U8'),  # (F:24) 
		('현재가', 'U8'),  # (F:25) 
		('기초자산명', 'U20'),  # (F:26) 
		])

class TR_1303_1(BaseTR):
	NAME, DESCRIPTION = 'TR_1303_1', '회원사 리스트 조회'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U'),  # (F:00) ‘005930’
		('조회구분', 'U'),  # (F:01) 항상 ‘D’
		('시작일자', 'U'),  # (F:02) ‘20100101’
		('종료일자', 'U'),  # (F:03) ‘20100105’
		('국내/외국 구분', 'U'),  # (F:04) 항상 ‘2’
		('언어구분', 'U'),  # (F:05) 공백
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('순번', 'U0'),  # (F:00) 
		('회원사ID', 'U0'),  # (F:01) 
		('회원사명', 'U0'),  # (F:02) 
		])

class TR_1864(BaseTR):
	NAME, DESCRIPTION = 'TR_1864', '거래량 급등락 종목 조회'
	INPUT_DTYPE = np.dtype([
		('장구분자', 'U0'),  # (F:00) 0 : KOSPI, 1 : KOSDAQ, 2 : 전체
		('대비급등락 구분', 'U0'),  # (F:01) 5일 평균대비 급증 : 1 5일 평균대비 급락 : 2 10일 평균대비 급증 : 3 10일 평균대비 급락 : 4 20일 평균대비 급증 : 5 20일 평균대비 급락 : 6
		('대비율', 'U0'),  # (F:02) * 대비급등락구분이 급증일 때 50% 이상 급증 : 1 100% 이상 급증 : 2 150% 이상 급증 : 3 * 대비급등락구분이 급락일 때 30% 이상 급락: 4 50% 이상 급락: 5 70% 이상 급락: 6
		('거래량조건', np.uint64),  # (F:03) 단위:주
		('종목조건', 'U1'),  # (F:04) 1:전체조회 2:관리종목제외 3:증거금100%인 종목제외 A:증거금20%인 종목보기 B:증거금30%인 종목보기 C:증거금40%인 종목보기 D:증거금100%인 종목보기
		('시가총액조건', 'U8'),  # (F:05) 단위:억
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('순위', 'U0'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('한글종목명', 'U20'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', 'U4'),  # (F:06) 
		('누적거래량', np.uint64),  # (F:07) 
		('급증률', 'U0'),  # (F:08) 
		('매도1호가', np.uint32),  # (F:09) 
		('매수1호가', np.uint32),  # (F:10) 
		('업종구분', 'U1'),  # (F:11) 
		('시가총액', np.uint32),  # (F:12) 
		('체결강도', np.uint32),  # (F:13) 
		])

class TR_1863(BaseTR):
	NAME, DESCRIPTION = 'TR_1863', '주가 등락율 상하위 종목 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) 0 : KOSPI, 1 : KOSDAQ, 2 : 전체
		('상하위 구분', 'U1'),  # (F:01) 0 : 상위, 1 : 하위
		('등락율 시작', 'U0'),  # (F:02) 등락율 범위 하한선 %  ( 예 : “0” = 등락율 0% 이상 ) ( 예 : “-15” = 등락율 -15% 이상)
		('등락율 종료', 'U0'),  # (F:03) 등락율 범위 상한선 %  ( 예 : “30” = 등락율 30 % 이하)  ( 예 : “0” = 등락율 0 % 이하)
		('거래량 이상', np.uint64),  # (F:04) 수량 (단위:주)
		('당일여부', 'U1'),  # (F:05) 0 : 당일, 1 : 당일아님
		('입력일자', 'U8'),  # (F:06) YYYYMMDD
		('시가총액 시작', 'U0'),  # (F:07) 금액 (단위:억)
		('종목조건', 'U1'),  # (F:08) 1:전체조회 2:관리종목제외 3:증거금100%인 종목제외 A:증거금20%인 종목보기 B:증거금30%인 종목보기 C:증거금40%인 종목보기 D:증거금100%인 종목보기
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('순위', 'U0'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('한글종목명', 'U20'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', 'U4'),  # (F:06) 
		('거래강도', 'U4'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('매도1호가', np.uint32),  # (F:09) 
		('매수1호가', np.uint32),  # (F:10) 
		('매도1호가 수량', 'U12'),  # (F:11) 
		('매수1호가 수량', 'U12'),  # (F:12) 
		('업종구분', 'U1'),  # (F:13) 
		('상하한가 진입시간', 'U8'),  # (F:14) 
		('시가총액', 'U0'),  # (F:15) 
		])


class TR_1870(BaseTR):
	NAME, DESCRIPTION = 'TR_1870', '이격도 조건 종목 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) 0 : KOSPI, 1 : KOSDAQ, 2 : 전체
		('이격도구분', 'U1'),  # (F:01) 0 : 5일, 1 : 20일, 2 : 60일, 4 :120일
		('이격도1', 'U3'),  # (F:02) 이격도 범위 하한선  ( 예 : “80” = 이격도 80 이상)
		('이격도2', 'U3'),  # (F:03) 이격도 범위 상한선 ( 예 : “120” = 이격도 120 이하)
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		('전일대비', np.uint32),  # (F:04) 
		('누적거래량', np.uint64),  # (F:05) 
		('5일 이격도', 'U0'),  # (F:06) 
		('20일 이격도', 'U0'),  # (F:07) 
		('60일 이격도', 'U0'),  # (F:08) 
		('120일 이격도', 'U0'),  # (F:09) 
		('장구분2', 'U1'),  # (F:10) 
		])


class TR_1505_07(BaseTR):
	NAME, DESCRIPTION = 'TR_1505_07', '전일 기관 순매도/순매수 상위50 종목 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) 0 : KOSPI, 1 : KOSDAQ, 2 : 전체
		('매수매도 구분', 'U1'),  # (F:01) 0 : 순매수, 1 : 순매도
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		('전일대비', np.uint32),  # (F:04) 
		('전일대비율', 'U4'),  # (F:05) 
		('전일 순매수/순매도', 'U0'),  # (F:06) 
		('거래강도', 'U4'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('업종구분', 'U0'),  # (F:09) 
		])


class TR_1406(BaseTR):
	NAME, DESCRIPTION = 'TR_1406', '전일 외국인 순매도/순매수 종목 조회'
	INPUT_DTYPE = np.dtype([
		('시장구분', 'U4'),  # (F:00) 0 : KOSPI, 1 : KOSDAQ, 2 : 전체
		('연속일수', 'U4'),  # (F:01) 예 :“3”= 전영업일 기준 3일 연속 순매수/순매도 ( 최소값 : 1 )
		('매수매도 구분', 'U4'),  # (F:02) 1 : 순매수, 2 : 순매도
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('장구분', 'U1'),  # (F:01) 
		('한글종목명', 'U20'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', 'U0'),  # (F:06) 
		('외국인누적거래량', np.uint64),  # (F:07) 
		('외국인보유비중', 'U0'),  # (F:08) 
		('기관누적거래량', np.uint64),  # (F:09) 
		('발행수량', 'U0'),  # (F:10) 
		('외국인보유', 'U0'),  # (F:11) 
		])


class TR_1871_2(BaseTR):
	NAME, DESCRIPTION = 'TR_1871_2', '업종별 종목 등락율 조회'
	INPUT_DTYPE = np.dtype([
		('시장구분', 'U1'),  # (F:00) 0 : KOSPI, 1 : KOSDAQ, 2 : KOSPI200, 3: 전체
		('기준일', 'U8'),  # (F:01) YYYYMMDD
		('비교일', 'U8'),  # (F:02) YYYYMMDD
		('업종코드', 'U3'),  # (F:03) 업종코드 4자리 중 끝 3자리 시장구분  “0”일 때 : 거래소업종 3자리 코드 (001 등) “1”일 때 : 코스닥업종 3자리 코드 (001 등) “2”일 때 : 거래소기타업종 3자리 코드 (101 등) “3”일 때 : 공백
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('기준일종가', np.uint32),  # (F:02) 
		('비교일종가', np.uint32),  # (F:03) 
		('등락', np.uint32),  # (F:04) 
		('등락률', 'U4'),  # (F:05) 
		('기준영업일', 'U8'),  # (F:06) 
		('비교영업일', 'U8'),  # (F:07) 
		('장구분2', 'U1'),  # (F:08) 
		('현재가', np.uint32),  # (F:09) 
		('전일대비구분', 'U1'),  # (F:10) 
		('전일대비', np.uint32),  # (F:11) 
		('매도1호가', np.uint32),  # (F:12) 
		('매수1호가', np.uint32),  # (F:13) 
		('기준가', np.uint32),  # (F:14) 
		])


class TR_1505_03(BaseTR):
	NAME, DESCRIPTION = 'TR_1505_03', '신고가/신저가 종목 조회'
	INPUT_DTYPE = np.dtype([
		('시장구분', 'U1'),  # (F:00) 0 : KOSPI, 1 : KOSDAQ, 2 : 전체
		('종류', 'U3'),  # (F:01) 0 : 연중신고가, 1 : 연중신저가 2 : 52주신고가, 3 : 52주신저가
		('거래량조건', np.uint64),  # (F:02) 단위:주
		('종목조건', 'U1'),  # (F:03) 1:전체조회 2:관리종목제외 3:증거금100%인 종목제외 A:증거금20%인 종목보기 B:증거금30%인 종목보기 C:증거금40%인 종목보기 D:증거금100%인 종목보기
		('시가총액조건', 'U8'),  # (F:04) 단위:억
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		('전일대비', np.uint32),  # (F:04) 
		('전일대비율', 'U4'),  # (F:05) 
		('신고저가', 'U0'),  # (F:06) 
		('거래강도', 'U4'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('업종구분', 'U0'),  # (F:09) 
		('매도1호가', np.uint32),  # (F:10) 
		('매수1호가', np.uint32),  # (F:11) 
		('시가총액', np.uint32),  # (F:12) 
		('체결강도', np.uint32),  # (F:13) 
		])


class TR_1860(BaseTR):
	NAME, DESCRIPTION = 'TR_1860', '상한가/하한가 종목 조회'
	INPUT_DTYPE = np.dtype([
		('시장구분', 'U1'),  # (F:00) 0 : KOSPI, 1 : KOSDAQ, 2 : 전체
		('상하한구분', 'U3'),  # (F:01) 1 : 상한가, 4 : 하한가
		('날짜', 'U8'),  # (F:02) YYYYMMDD
		('거래량조건', np.uint64),  # (F:03) 단위:주
		('종목조건', 'U1'),  # (F:04) 1:전체조회 2:관리종목제외 3:증거금100%인 종목제외 A:증거금20%인 종목보기 B:증거금30%인 종목보기 C:증거금40%인 종목보기 D:증거금100%인 종목보기
		('시가총액조건', 'U8'),  # (F:05) 단위:억
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('해당일종가', 'U0'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', 'U4'),  # (F:06) 
		('종가 전일대비구분', 'U0'),  # (F:07) 
		('종가 전일대비', 'U0'),  # (F:08) 
		('종가 전일대비율', 'U0'),  # (F:09) 
		('연속일', 'U0'),  # (F:10) 
		('거래강도', 'U4'),  # (F:11) 
		('누적거래량', np.uint64),  # (F:12) 
		('업종구분', 'U0'),  # (F:13) 
		('매도 총호가수량', 'U12'),  # (F:14) 
		('매수 총호가수량', 'U12'),  # (F:15) 
		('매도1호가', np.uint32),  # (F:16) 
		('매수1호가', np.uint32),  # (F:17) 
		('매도1호가 수량', 'U12'),  # (F:18) 
		('매수1호가 수량', 'U12'),  # (F:19) 
		('시가총액', np.uint32),  # (F:20) 
		('체결강도', np.uint32),  # (F:21) 
		])


class TR_1862(BaseTR):
	NAME, DESCRIPTION = 'TR_1862', '시가대비 상승율 조회'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U40'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('시가', np.uint32),  # (F:03) 
		('시가대비상승율', 'U10'),  # (F:04) 
		])


class cfut_mst(BaseTR):
	NAME, DESCRIPTION = 'cfut_mst', '상품선물 종목 코드 조회 (전종목)'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('파생상품ID', 'U10'),  # (F:02) 
		('한글종목명', 'U40'),  # (F:03) 
		('기초자산ID', 'U3'),  # (F:04) 
		('스프레드근월물표준코드', 'U12'),  # (F:05) 
		('스프레드원월물표준코드', 'U12'),  # (F:06) 
		('최종거래일', 'U8'),  # (F:07) 
		('기초자산종목코드', 'U12'),  # (F:08) 
		('거래단위', 'U17'),  # (F:09) 
		('거래승수', 'U21'),  # (F:10) 
		])


class erx_mst(BaseTR):
	NAME, DESCRIPTION = 'erx_mst', '유렉스 종목 코드 조회 (전종목) – 옵션'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('GIC', 'U13'),  # (F:00) 
		('단축코드', np.uint32),  # (F:01) 
		('한글종목명', 'U30'),  # (F:02) 
		('옵션종류', 'U1'),  # (F:03) 
		('ATM 구분', 'U1'),  # (F:04) 
		('만기일', 'U8'),  # (F:05) 
		])


class fri_mst(BaseTR):
	NAME, DESCRIPTION = 'fri_mst', '해외지수 코드 조회 (전종목)'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('GIC', 'U15'),  # (F:00) 
		('국가코드', 'U3'),  # (F:01) 
		('심벌', 'U12'),  # (F:02) 
		('거래소코드', 'U3'),  # (F:03) 
		('한글종목명', 'U40'),  # (F:04) 
		])


class TR_1206_ELW(BaseTR):
	NAME, DESCRIPTION = 'TR_1206_ELW', 'ELW 종목별 동향 (일별)'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('시작일', 'U0'),  # (F:01) YYYYMMDD
		('종료일', 'U0'),  # (F:02) YYYYMMDD
		('데이터 개수 구분', 'U0'),  # (F:03) 0:60개씩 		1:전체
		('데이터 종류 구분', 'U0'),  # (F:04) 0:거래량 		1:거래대금
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U0'),  # (F:00) 
		('가격', 'U0'),  # (F:01) 
		('시가', 'U0'),  # (F:02) 
		('고가', 'U0'),  # (F:03) 
		('저가', 'U0'),  # (F:04) 
		('전일대비구분', 'U0'),  # (F:05) 
		('전일대비', 'U0'),  # (F:06) 
		('누적거래량', np.uint64),  # (F:07) 
		('개인매수거래량', np.uint64),  # (F:08) 
		('개인매도거래량', np.uint64),  # (F:09) 
		('개인순매수거래량', np.uint64),  # (F:10) 
		('개인매수누적', 'U0'),  # (F:11) 
		('개인매도누적', 'U0'),  # (F:12) 
		('개인순매수누적거래량', np.uint64),  # (F:13) 
		('외국인매수거래량', np.uint64),  # (F:14) 
		('외국인매도거래량', np.uint64),  # (F:15) 
		('외국인순매수거래량', np.uint64),  # (F:16) 
		('외국인매수누적', 'U0'),  # (F:17) 
		('외국인매도누적', 'U0'),  # (F:18) 
		('외국인순매수누적거래량', np.uint64),  # (F:19) 
		('기관매수거래량', np.uint64),  # (F:20) 
		('기관매도거래량', np.uint64),  # (F:21) 
		('기관순매수거래량', np.uint64),  # (F:22) 
		('기관매수누적', 'U0'),  # (F:23) 
		('기관매도누적', 'U0'),  # (F:24) 
		('기관순매수누적거래량', np.uint64),  # (F:25) 
		('증권매수거래량', np.uint64),  # (F:26) 
		('증권매도거래량', np.uint64),  # (F:27) 
		('증권순매수거래량', np.uint64),  # (F:28) 
		('증권매수누적', 'U0'),  # (F:29) 
		('증권매도누적', 'U0'),  # (F:30) 
		('증권순매수누적거래량', np.uint64),  # (F:31) 
		('투신매수거래량', np.uint64),  # (F:32) 
		('투신매도거래량', np.uint64),  # (F:33) 
		('투신순매수거래량', np.uint64),  # (F:34) 
		('투신매수누적', 'U0'),  # (F:35) 
		('투신매도누적', 'U0'),  # (F:36) 
		('투신순매수누적거래량', np.uint64),  # (F:37) 
		('은행매수거래량', np.uint64),  # (F:38) 
		('은행매도거래량', np.uint64),  # (F:39) 
		('은행순매수거래량', np.uint64),  # (F:40) 
		('은행매수누적', 'U0'),  # (F:41) 
		('은행매도누적', 'U0'),  # (F:42) 
		('은행순매수누적거래량', np.uint64),  # (F:43) 
		('종금매수거래량', np.uint64),  # (F:44) 
		('종금매도거래량', np.uint64),  # (F:45) 
		('종금순매수거래량', np.uint64),  # (F:46) 
		('종금매수누적', 'U0'),  # (F:47) 
		('종금매도누적', 'U0'),  # (F:48) 
		('종금순매수누적거래량', np.uint64),  # (F:49) 
		('보험매수거래량', np.uint64),  # (F:50) 
		('보험매도거래량', np.uint64),  # (F:51) 
		('보험순매수거래량', np.uint64),  # (F:52) 
		('보험매수누적', 'U0'),  # (F:53) 
		('보험매도누적', 'U0'),  # (F:54) 
		('보험순매수누적거래량', np.uint64),  # (F:55) 
		('기금매수거래량', np.uint64),  # (F:56) 
		('기금매도거래량', np.uint64),  # (F:57) 
		('기금순매수거래량', np.uint64),  # (F:58) 
		('기금매수누적', 'U0'),  # (F:59) 
		('기금매도누적', 'U0'),  # (F:60) 
		('기금순매수누적거래량', np.uint64),  # (F:61) 
		('기타매수거래량', np.uint64),  # (F:62) 
		('기타매도거래량', np.uint64),  # (F:63) 
		('기타순매수거래량', np.uint64),  # (F:64) 
		('기타매수누적', 'U0'),  # (F:65) 
		('기타매도누적', 'U0'),  # (F:66) 
		('기타순매수누적거래량', np.uint64),  # (F:67) 
		('외국인기타매수거래량', np.uint64),  # (F:68) 
		('외국인기타매도거래량', np.uint64),  # (F:69) 
		('외국인기타순매수거래량', np.uint64),  # (F:70) 
		('외국인기타매수누적', 'U0'),  # (F:71) 
		('외국인기타매도누적', 'U0'),  # (F:72) 
		('외국인기타순매수누적거래량', np.uint64),  # (F:73) 
		('프로그램매수', 'U0'),  # (F:74) 
		('프로그램매도', 'U0'),  # (F:75) 
		('프로그램순매수', 'U0'),  # (F:76) 
		('프로그램누적매수', 'U0'),  # (F:77) 
		('프로그램누적매도', 'U0'),  # (F:78) 
		('프로그램누적순매수', 'U0'),  # (F:79) 
		('사모펀드매수', 'U0'),  # (F:80) 
		('사모펀드매도', 'U0'),  # (F:81) 
		('사모펀드순매수', 'U0'),  # (F:82) 
		('사모펀드누적매수', 'U0'),  # (F:83) 
		('사모펀드누적매도', 'U0'),  # (F:84) 
		('사모펀드누적순매수', 'U0'),  # (F:85) 
		('전일대비율', 'U0'),  # (F:86) 
		])


class TR_2106(BaseTR):
	NAME, DESCRIPTION = 'TR_2106', '옵션 만기월물별 전종목 시세'
	INPUT_DTYPE = np.dtype([
		('콜풋구분', 'U1'),  # (F:00) 2:콜 			3:풋
		('만기년월', 'U6'),  # (F:01) YYYYMM
		('장구분', 'U1'),  # (F:02) 0: 코스피200         1: 미니
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U8'),  # (F:00) 
		('행사가격', 'U4'),  # (F:01) 
		('KP등가', 'U4'),  # (F:02) 
		('ATM 구분', 'U1'),  # (F:03) 
		('현재가/종가/지수/기세가', 'U4'),  # (F:04) 
		('전일대비구분 (기준가)', 'U1'),  # (F:05) 
		('전일대비', 'U4'),  # (F:06) 
		('전일대비율', 'U4'),  # (F:07) 
		('누적거래량/주식거래량', np.uint64),  # (F:08) 
		('매도01호가', 'U4'),  # (F:09) 
		('매도01호가수량', 'U4'),  # (F:10) 
		('매수01호가', 'U4'),  # (F:11) 
		('매수01호가수량', 'U4'),  # (F:12) 
		('이론가', 'U4'),  # (F:13) 
		('내재변동성', 'U4'),  # (F:14) 
		('괴리도', 'U4'),  # (F:15) 
		('괴리율', 'U1'),  # (F:16) 
		('델타', 'U4'),  # (F:17) 
		('감마', 'U4'),  # (F:18) 
		('세타', 'U4'),  # (F:19) 
		('베가', 'U4'),  # (F:20) 
		('로', 'U4'),  # (F:21) 
		('미결제약정수량', 'U4'),  # (F:22) 
		('전일종가', 'U4'),  # (F:23) 
		('전일미결제약정수량', 'U8'),  # (F:24) 
		('시가', 'U4'),  # (F:25) 
		('고가', 'U4'),  # (F:26) 
		('저가', 'U4'),  # (F:27) 
		('누적거래대금', np.uint64),  # (F:28) 
		('기준가', 'U0'),  # (F:29) 
		])


class TR_3201(BaseTR):
	NAME, DESCRIPTION = 'TR_3201', '주요 통화(화폐)의 상호간 환율 조회'
	INPUT_DTYPE = np.dtype([
		('거래날짜', 'U8'),  # (F:00) YYYYMMDD
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('환율1', 'U0'),  # (F:00) 달러/달러
		('환율2', 'U0'),  # (F:01) 원/달러
		('환율3', 'U0'),  # (F:02) 엔/달러
		('환율4', 'U0'),  # (F:03) 유로/달러
		('환율5', 'U0'),  # (F:04) 파운드/달러
		('환율6', 'U0'),  # (F:05) 대만달러/달러
		('환율7', 'U0'),  # (F:06) 홍콩달러/달러
		('환율8', 'U0'),  # (F:07) 위안/달러
		('환율9', 'U0'),  # (F:08) 달러/원
		('환율10', 'U0'),  # (F:09) 원/원
		('환율11', 'U0'),  # (F:10) 엔/원
		('환율12', 'U0'),  # (F:11) 유로/원
		('환율13', 'U0'),  # (F:12) 파운드/원
		('환율14', 'U0'),  # (F:13) 대만달러/원
		('환율15', 'U0'),  # (F:14) 홍콩달러/원
		('환율16', 'U0'),  # (F:15) 위안/원
		('환율17', 'U0'),  # (F:16) 달러/엔
		('환율18', 'U0'),  # (F:17) 원/엔
		('환율19', 'U0'),  # (F:18) 엔/엔
		('환율20', 'U0'),  # (F:19) 유로/엔
		('환율21', 'U0'),  # (F:20) 파운드/엔
		('환율22', 'U0'),  # (F:21) 대만달러/엔
		('환율23', 'U0'),  # (F:22) 홍콩달러/엔
		('환율24', 'U0'),  # (F:23) 위안/엔
		('환율25', 'U0'),  # (F:24) 달러/유로
		('환율26', 'U0'),  # (F:25) 원/유로
		('환율27', 'U0'),  # (F:26) 엔/유로
		('환율28', 'U0'),  # (F:27) 유로/유로
		('환율29', 'U0'),  # (F:28) 파운드/유로
		('환율30', 'U0'),  # (F:29) 대만달러/유로
		('환율31', 'U0'),  # (F:30) 홍콩달러/유로
		('환율32', 'U0'),  # (F:31) 위안/유로
		('환율33', 'U0'),  # (F:32) 달러/파운드
		('환율34', 'U0'),  # (F:33) 원/파운드
		('환율35', 'U0'),  # (F:34) 엔/파운드
		('환율36', 'U0'),  # (F:35) 유로/파운드
		('환율37', 'U0'),  # (F:36) 파운드/파운드
		('환율38', 'U0'),  # (F:37) 대만달러/파운드
		('환율39', 'U0'),  # (F:38) 홍콩달러/파운드
		('환율40', 'U0'),  # (F:39) 위안/파운드
		('환율41', 'U0'),  # (F:40) 달러/대만달러
		('환율42', 'U0'),  # (F:41) 원/대만달러
		('환율43', 'U0'),  # (F:42) 엔/대만달러
		('환율44', 'U0'),  # (F:43) 유로/대만달러
		('환율45', 'U0'),  # (F:44) 파운드/대만달러
		('환율46', 'U0'),  # (F:45) 대만달러/대만달러
		('환율47', 'U0'),  # (F:46) 홍콩달러/대만달러
		('환율48', 'U0'),  # (F:47) 위안/대만달러
		('환율49', 'U0'),  # (F:48) 달러/홍콩달러
		('환율50', 'U0'),  # (F:49) 원/홍콩달러
		('환율51', 'U0'),  # (F:50) 엔/홍콩달러
		('환율52', 'U0'),  # (F:51) 유로/홍콩달러
		('환율53', 'U0'),  # (F:52) 파운드/홍콩달러
		('환율54', 'U0'),  # (F:53) 대만달러/홍콩달러
		('환율55', 'U0'),  # (F:54) 홍콩달러/홍콩달러
		('환율56', 'U0'),  # (F:55) 위안/홍콩달러
		('환율57', 'U0'),  # (F:56) 달러/위안
		('환율58', 'U0'),  # (F:57) 원/위안
		('환율59', 'U0'),  # (F:58) 엔/위안
		('환율60', 'U0'),  # (F:59) 유로/위안
		('환율61', 'U0'),  # (F:60) 파운드/위안
		('환율62', 'U0'),  # (F:61) 대만달러/위안
		('환율63', 'U0'),  # (F:62) 홍콩달러/위안
		('환율64', 'U0'),  # (F:63) 위안/위안
		])
	MULTI_OUTPUT_DTYPE = None


class TR_1700_10(BaseTR):
	NAME, DESCRIPTION = 'TR_1700_10', '예상지수 체결가 분석'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) 0:거래소, 1:코스닥, 2:전체
		('전일대비구분', 'U1'),  # (F:01) 1:예상상한가, 2:예상상승, 3:예상보합,  4:예상하락, 5:예상하한가
		('예상전일대비 시작값', np.uint32),  # (F:02) 예상상승 하락시에만 사용(ex. 0)
		('예상전일대비 종료값', np.uint32),  # (F:03) 예상상승 하락시에만 사용(ex. 15)
		('예상체결수량', 'U12'),  # (F:04) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('기준가', np.uint32),  # (F:03) 
		('상한가', np.uint32),  # (F:04) 
		('하한가', np.uint32),  # (F:05) 
		('예상체결가격', np.uint32),  # (F:06) 
		('예상체결부호', 'U1'),  # (F:07) 2:상승 1:하락
		('예상체결전일비', 'U'),  # (F:08) 
		('예상체결전일비율', 'U'),  # (F:09) 
		('직전실가격대비', 'U'),  # (F:10) 
		('예상체결수량', 'U'),  # (F:11) 
		('연속일수', 'U'),  # (F:12) 
		('장구분', 'U1'),  # (F:13) 0:거래소, 1:코스닥
		])


class TR_9053(BaseTR):
	NAME, DESCRIPTION = 'TR_9053', '선물 전일 시고저종 조회'
	INPUT_DTYPE = np.dtype([
		('단축코드', np.uint32),  # (F:00) 
		('구분', 'U2'),  # (F:01) 선물 : “FU,” 옵션 : OP, 상품선물 : “CF”
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('전일시가', np.uint32),  # (F:00) 
		('전일고가', np.uint32),  # (F:01) 
		('전일저가', np.uint32),  # (F:02) 
		('전일종가', np.uint32),  # (F:03) 
		])


class TR_1457(BaseTR):
	NAME, DESCRIPTION = 'TR_1457', '프로그램 투자자별 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) 0: 거래소, 1: 코스닥
		('시작일자', 'U8'),  # (F:01) 
		('종료일자', 'U8'),  # (F:02) 
		('단위구분', 'U1'),  # (F:03) 0: 수량, 1: 금액
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('전체개인매도', np.uint64),  # (F:00) 
		('전체개인매수', np.uint64),  # (F:01) 
		('전체개인순매수', np.uint64),  # (F:02) 
		('전체외국인계매도', np.uint64),  # (F:03) 
		('전체외국인계매수', np.uint64),  # (F:04) 
		('전체외국인계순매수', np.uint64),  # (F:05) 
		('전체기관계매도', np.uint64),  # (F:06) 
		('전체기관계매수', np.uint64),  # (F:07) 
		('전체기관계순매수', np.uint64),  # (F:08) 
		('전체금융투자매도', np.uint64),  # (F:09) 
		('전체금융투자매수', np.uint64),  # (F:10) 
		('전체금융투자순매수', np.uint64),  # (F:11) 
		('전체투신매도', np.uint64),  # (F:12) 
		('전체투신매수', np.uint64),  # (F:13) 
		('전체투신순매수', np.uint64),  # (F:14) 
		('전체은행매도', np.uint64),  # (F:15) 
		('전체은행매수', np.uint64),  # (F:16) 
		('전체은행순매수', np.uint64),  # (F:17) 
		('전체기타금융매도', np.uint64),  # (F:18) 
		('전체기타금융매수', np.uint64),  # (F:19) 
		('전체기타금융순매수', np.uint64),  # (F:20) 
		('전체보험매도', np.uint64),  # (F:21) 
		('전체보험매수', np.uint64),  # (F:22) 
		('전체보험순매수', np.uint64),  # (F:23) 
		('전체연기금매도', np.uint64),  # (F:24) 
		('전체연기금매수', np.uint64),  # (F:25) 
		('전체연기금순매수', np.uint64),  # (F:26) 
		('전체외국인매도', np.uint64),  # (F:27) 
		('전체외국인매수', np.uint64),  # (F:28) 
		('전체외국인순매수', np.uint64),  # (F:29) 
		('전체외국인기타매도', np.uint64),  # (F:30) 
		('전체외국인기타매수', np.uint64),  # (F:31) 
		('전체외국인기타순매수', np.uint64),  # (F:32) 
		('전체기타법인매도', np.uint64),  # (F:33) 
		('전체기타법인매수', np.uint64),  # (F:34) 
		('전체기타법인순매수', np.uint64),  # (F:35) 
		('전체국가매도', np.uint64),  # (F:36) 
		('전체국가매수', np.uint64),  # (F:37) 
		('전체국가순매수', np.uint64),  # (F:38) 
		('전체사모펀드매도', np.uint64),  # (F:39) 
		('전체사모펀드매수', np.uint64),  # (F:40) 
		('전체사모펀드순매수', np.uint64),  # (F:41) 
		('차익개인매도', np.uint64),  # (F:42) 
		('차익개인매수', np.uint64),  # (F:43) 
		('차익개인순매수', np.uint64),  # (F:44) 
		('차익외국인계매도', np.uint64),  # (F:45) 
		('차익외국인계매수', np.uint64),  # (F:46) 
		('차익외국인계순매수', np.uint64),  # (F:47) 
		('차익기관계매도', np.uint64),  # (F:48) 
		('차익기관계매수', np.uint64),  # (F:49) 
		('차익기관계순매수', np.uint64),  # (F:50) 
		('차익금융투자매도', np.uint64),  # (F:51) 
		('차익금융투자매수', np.uint64),  # (F:52) 
		('차익금융투자순매수', np.uint64),  # (F:53) 
		('차익투신매도', np.uint64),  # (F:54) 
		('차익투신매수', np.uint64),  # (F:55) 
		('차익투신순매수', np.uint64),  # (F:56) 
		('차익은행매도', np.uint64),  # (F:57) 
		('차익은행매수', np.uint64),  # (F:58) 
		('차익은행순매수', np.uint64),  # (F:59) 
		('차익기타금융매도', np.uint64),  # (F:60) 
		('차익기타금융매수', np.uint64),  # (F:61) 
		('차익기타금융순매수', np.uint64),  # (F:62) 
		('차익보험매도', np.uint64),  # (F:63) 
		('차익보험매수', np.uint64),  # (F:64) 
		('차익보험순매수', np.uint64),  # (F:65) 
		('차익연기금매도', np.uint64),  # (F:66) 
		('차익연기금매수', np.uint64),  # (F:67) 
		('차익연기금순매수', np.uint64),  # (F:68) 
		('차익외국인매도', np.uint64),  # (F:69) 
		('차익외국인매수', np.uint64),  # (F:70) 
		('차익외국인순매수', np.uint64),  # (F:71) 
		('차익외국인기타매도', np.uint64),  # (F:72) 
		('차익외국인기타매수', np.uint64),  # (F:73) 
		('차익외국인기타순매수', np.uint64),  # (F:74) 
		('차익기타법인매도', np.uint64),  # (F:75) 
		('차익기타법인매수', np.uint64),  # (F:76) 
		('차익기타법인순매수', np.uint64),  # (F:77) 
		('차익국가매도', np.uint64),  # (F:78) 
		('차익국가매수', np.uint64),  # (F:79) 
		('차익국가순매수', np.uint64),  # (F:80) 
		('차익사모펀드매도', np.uint64),  # (F:81) 
		('차익사모펀드매수', np.uint64),  # (F:82) 
		('차익사모펀드순매수', np.uint64),  # (F:83) 
		('비차익개인매도', np.uint64),  # (F:84) 
		('비차익개인매수', np.uint64),  # (F:85) 
		('비차익개인순매수', np.uint64),  # (F:86) 
		('비차익외국인계매도', np.uint64),  # (F:87) 
		('비차익외국인계매수', np.uint64),  # (F:88) 
		('비차익외국인계순매수', np.uint64),  # (F:89) 
		('비차익기관계매도', np.uint64),  # (F:90) 
		('비차익기관계매수', np.uint64),  # (F:91) 
		('비차익기관계순매수', np.uint64),  # (F:92) 
		('비차익금융투자매도', np.uint64),  # (F:93) 
		('비차익금융투자매수', np.uint64),  # (F:94) 
		('비차익금융투자순매수', np.uint64),  # (F:95) 
		('비차익투신매도', np.uint64),  # (F:96) 
		('비차익투신매수', np.uint64),  # (F:97) 
		('비차익투신순매수', np.uint64),  # (F:98) 
		('비차익은행매도', np.uint64),  # (F:99) 
		('비차익은행매수', np.uint64),  # (F:100) 
		('비차익은행순매수', np.uint64),  # (F:101) 
		('비차익기타금융매도', np.uint64),  # (F:102) 
		('비차익기타금융매수', np.uint64),  # (F:103) 
		('비차익기타금융순매수', np.uint64),  # (F:104) 
		('비차익보험매도', np.uint64),  # (F:105) 
		('비차익보험매수', np.uint64),  # (F:106) 
		('비차익보험순매수', np.uint64),  # (F:107) 
		('비차익기금매도', np.uint64),  # (F:108) 
		('비차익기금매수', np.uint64),  # (F:109) 
		('비차익기금순매수', np.uint64),  # (F:110) 
		('비차익외국인매도', np.uint64),  # (F:111) 
		('비차익외국인매수', np.uint64),  # (F:112) 
		('비차익외국인순매수', np.uint64),  # (F:113) 
		('비차익외국인기타매도', np.uint64),  # (F:114) 
		('비차익외국인기타매수', np.uint64),  # (F:115) 
		('비차익외국인기타순매수', np.uint64),  # (F:116) 
		('비차익기타법인매도', np.uint64),  # (F:117) 
		('비차익기타법인매수', np.uint64),  # (F:118) 
		('비차익기타법인순매수', np.uint64),  # (F:119) 
		('비차익국가매도', np.uint64),  # (F:120) 
		('비차익국가매수', np.uint64),  # (F:121) 
		('비차익국가순매수', np.uint64),  # (F:122) 
		('비차익사모펀드매도', np.uint64),  # (F:123) 
		('비차익사모펀드매수', np.uint64),  # (F:124) 
		('비차익사모펀드순매수', np.uint64),  # (F:125) 
		])
	MULTI_OUTPUT_DTYPE = None


class SI(BaseTR, BaseRealtime):
	NAME, DESCRIPTION = 'SI', '프로그램 투자자별 매매동향'
	INPUT_DTYPE = np.dtype([
		('투자자코드', 'U5'),  # (F:00) 시장구분코드(1) + 투자자구분코드(4) 시장구분: 0 = 거래소, 1 = 코스닥 투자자구분:  [부록 7.4 투자자구분코드 참고] ex) 거래소 + 개인 = 08000
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('투자자코드', 'U5'),  # (F:00) 시장구분코드(1) + 투자자구분코드(4) 시장구분: 0 = 거래소, 1 = 코스닥 투자자구분:  [부록 7.4 투자자구분코드 참고] ex) 거래소 + 개인 = 08000
		('시간', 'U6'),  # (F:01) 
		('매도차익체결수량', 'U12'),  # (F:02) 
		('매도차익거래대금', np.uint64),  # (F:03) 
		('매도비차익체결수량', 'U12'),  # (F:04) 
		('매도비차익거래대금', np.uint64),  # (F:05) 
		('매수차익체결수량', 'U12'),  # (F:06) 
		('매수차익거래대금', np.uint64),  # (F:07) 
		('매수비차익체결수량', 'U12'),  # (F:08) 
		('매수비차익거래대금', np.uint64),  # (F:09) 
		])
	MULTI_OUTPUT_DTYPE = None


class TR_1841(BaseTR):
	NAME, DESCRIPTION = 'TR_1841', '체결강도 조회'
	INPUT_DTYPE = np.dtype([
		('종목코드', 'U6'),  # (F:00) 
		('일괄조회여부', 'U1'),  # (F:01) 0, 1
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('체결시간', 'U8'),  # (F:00) 
		('현재가', np.uint32),  # (F:01) 
		('전일대비구분', 'U1'),  # (F:02) 
		('전일대비', np.uint32),  # (F:03) 
		('전일대비율', 'U4'),  # (F:04) 
		('매도체결', 'U8'),  # (F:05) 
		('매수체결', 'U8'),  # (F:06) 
		('체결강도', 'U4'),  # (F:07) 
		('단위체결량', 'U12'),  # (F:08) 
		('호가체결구분', 'U1'),  # (F:09) 
		('체결매도매수구분', 'U1'),  # (F:10) 
		])


class TR_1314_3(BaseTR):
	NAME, DESCRIPTION = 'TR_1314_3', '외국인/기관 매매종목 현황'
	INPUT_DTYPE = np.dtype([
		('투자자구분', 'U2'),  # (F:00) 02: 보험, 03: 투신, 04: 은행, 05: 기타금융,  07:기타법인, 09: 외국인, 10: 기관
		('시장구분', 'U1'),  # (F:01) 0: 거래소, 1: 코스닥, 2: 전체
		('상위하위구분', 'U1'),  # (F:02) 0: 상위, 1: 하위
		('매도매수구분', 'U1'),  # (F:03) 0: 매도, 1: 매수
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('종목명', 'U20'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('등락구분', 'U1'),  # (F:03) 
		('등락', np.uint32),  # (F:04) 
		('등락율', 'U4'),  # (F:05) 
		('당일누적거래량', np.uint64),  # (F:06) 
		('당일누적거래대금', np.uint64),  # (F:07) 
		('누적거래량(외국인 외국계 창구포함)', np.uint64),  # (F:08) 
		('누적거래량(투신)', np.uint64),  # (F:09) 
		('누적거래량(은행)', np.uint64),  # (F:10) 
		('누적거래량(보험/종금)', np.uint64),  # (F:11) 
		('누적거래량(기금, 공제)', np.uint64),  # (F:12) 
		('누적거래량(기타법인)', np.uint64),  # (F:13) 
		('누적거래량(국가/지자체)', np.uint64),  # (F:14) 
		('프로그램매수수량', 'U12'),  # (F:15) 
		])


class SE(BaseTR):
	NAME, DESCRIPTION = 'SE', '현물ETF'
	INPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('시간', 'U6'),  # (F:02) 
		('현재가', np.float32),  # (F:03) NAV 값(현재가는 SC 실시간 TR 사용)
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.float32),  # (F:05) 
		('전일대비율', np.float32),  # (F:06) 
		('시가', np.float32),  # (F:07) 
		('고가', np.float32),  # (F:08) 
		('저가', np.float32),  # (F:09) 
		('시가시간', 'U6'),  # (F:10) 
		('고가시간', 'U6'),  # (F:11) 
		('저가시간', 'U6'),  # (F:12) 
		('추적오차율', np.float32),  # (F:13) 
		('괴리율', np.float32),  # (F:14) 전일값 기준으로 계산(실시간으로 당일 괴리율값 계산하지 않습니다.)
		])
	MULTI_OUTPUT_DTYPE = None


class gmf_mst(BaseTR):
	NAME, DESCRIPTION = 'gmf_mst', '야간달러선물 종목 정보 조회'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U8'),  # (F:01) 
		('종목명', 'U30'),  # (F:02) 
		('심볼명', 'U15'),  # (F:03) 
		('만기일', 'U8'),  # (F:04) 
		('기초자산ID', 'U3'),  # (F:05) 
		])


class TR_RB001(BaseTR):
	NAME, DESCRIPTION = 'TR_RB001', '현물 마스터 전종목 조회'
	INPUT_DTYPE = np.dtype([
		('구분', 'U1'),  # (F:00) 0: 전체, 1: KOSPI, 2: KOSDAQ
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('장구분', 'U1'),  # (F:02) 0:유가증권, 1:코스닥
		('일련번호', 'U4'),  # (F:03) 
		('입회일자', 'U8'),  # (F:04) 
		('한글종목명', 'U40'),  # (F:05) 
		('영문종목명', 'U40'),  # (F:06) 
		('제조업구분/업종대분류', 'U3'),  # (F:07) 
		('업종중분류', 'U3'),  # (F:08) 
		('업종소분류', 'U3'),  # (F:09) 
		('산업업종코드', 'U6'),  # (F:10) 
		('KOSPI200/KOSDAQ50채용구분', 'U1'),  # (F:11) 0:미분류, 1:건설기계, 2:조선운송, 3:철강소재, 4:에너지화학, 5:정보통신, 6:금융, 7:필수소비재, 8:자유소비재
		('KOSPI100채용구분', 'U1'),  # (F:12) Y/N
		('KOSPI50채용구분', 'U1'),  # (F:13) Y/N
		('정보통신지수채용구분', 'U1'),  # (F:14) 0:미채용
		('시가총액규모/지수업종그룹', 'U1'),  # (F:15) (유가) 0:제외, 1:대, 2:중, 3:소 (코스닥) 0:제외, 1:KOSDAQ100, 2:KOSDAQmid300, 3:KOSDAQsmall
		('KOSDI구분/지배구조우량구분', 'U2'),  # (F:16) (유가) 00:일반, 01:배당지수종목, 03:우량, 04:배당+우량 (코스닥) 00:일반, 01:우량, 02:KOSTAR지수종목, 03:우량+KOSTAR
		('상장구분', 'U2'),  # (F:17) 01:정상, 02:신규, 03:신주상장, 04:기준가산출후거래무, 05:상장폐지, 06:주식병합, 07:기준가조정
		('상장주식수', np.uint64),  # (F:18) 
		('소속구분', 'U2'),  # (F:19) ST:주식, MF:증권투자회사, RT:리츠, SC:선박투자회사, IF:인프라투융자회사, DR:예탁증서, SW:신주인수권증권, SR:신주인수권증서, BW:주식워런트증권(ELW), FU:선물, OP:옵션, EF:상장지수펀드(ETF), BC:수익증권, FE:해외ETF, FS:해외원주, EN: ETN
		('결산월일', 'U4'),  # (F:20) 상장사의 회계결산일(12월 31일, 6월 30일, 3월 31일) 결산기나 결산월일 경우는 12월일 경우 '1200'로 표시
		('액면가', np.uint32),  # (F:21) 외국주권일 경우 소숫점셋째자리까지 표현가능
		('액면가변경구분코드', 'U2'),  # (F:22) 00:해당없음, 01:액면분할, 02:액면병합, 99:기타
		('전일종가', np.uint32),  # (F:23) 
		('전일거래량', np.uint64),  # (F:24) 
		('전일거래대금', np.uint64),  # (F:25) 
		('기준가', np.uint32),  # (F:26) 
		('상한가', np.uint32),  # (F:27) 
		('하한가', np.uint32),  # (F:28) 
		('대용가', np.uint32),  # (F:29) 
		('거래정지구분', 'U1'),  # (F:30) 0:정상, 1:정지, 5:CB발동
		('관리구분', 'U1'),  # (F:31) 0:정상, 1:관리
		('감리구분', 'U1'),  # (F:32) 0:정상, 1:주의, 2:경고, 3:위험
		('락구분', 'U2'),  # (F:33) 00:발생안함, 01:권리락, 02:배당락, 03:분배락, 04:권배락, 05:중간배당락, 06:권리중간배당락, 99:기타 ※미해당의 경우 SPACE
		('불성실공시지정여부', 'U1'),  # (F:34) 0:정상, 1:불성실공시지정
		('평가가격', np.uint32),  # (F:35) 
		('최고호가가격', np.uint32),  # (F:36) 
		('최저호가가격', np.uint32),  # (F:37) 
		('매매구분', 'U1'),  # (F:38) 1:보통, 2:신규상장, 3:관리지정, 4:관리해제, 5:정리매매, 6:30일간거래정지후재개, 7:시가기준가산출, 8:단일가매매
		('정리매매시작일', 'U8'),  # (F:39) 
		('정리매매종료일', 'U8'),  # (F:40) 
		('투자유의구분', 'U1'),  # (F:41) 
		('REITs구분', 'U1'),  # (F:42) 1:일반리츠, 2:CRV리츠
		('매매수량단위', 'U5'),  # (F:43) 
		('시간외매매수량단위', 'U5'),  # (F:44) 
		('자본금', 'U18'),  # (F:45) 
		('배당수익율', np.float32),  # (F:46) 9(6)V9(1)
		('ETF분류', 'U1'),  # (F:47) 0:일반형, 1:투자회사형, 2:수익증권형
		('ETF관련지수업종대', 'U1'),  # (F:48) 1:유가증권, 2:코스닥, 3:섹터, 4:GICS, 8:MF(매경), 9:해외
		('ETF관련지수업종중', 'U3'),  # (F:49) 
		('ETF CU단위', 'U8'),  # (F:50) 
		('ETF 구성종목수', 'U4'),  # (F:51) 
		('ETF 순자산총액', np.uint64),  # (F:52) 
		('ETF관련지수대비비율', np.float32),  # (F:53) 9(5)V9(6) ETF대상지수 대비 Etf종목 종가의 비율
		('최종NAV', np.float32),  # (F:54) 9(7)V9(2) 송신일자의 최종NAV 자료
		('매매방식 구분', 'U1'),  # (F:55) 항상 0
		('통합지수종목구분', 'U1'),  # (F:56) 0:일반종목, 1:통합지수종목
		('매매개시일', 'U8'),  # (F:57) 
		('KRX 섹터지수 자동차구분', 'U1'),  # (F:58) 0:일반종목, 1:KRX섹터지수 자동차구분
		('KRX 섹터지수 반도체구분', 'U1'),  # (F:59) 0:일반종목, 1:KRX섹터지수 반도체구분
		('KRX 섹터지수 바이오구분', 'U1'),  # (F:60) 0:일반종목, 1:KRX섹터지수 바이오구분
		('KRX 섹터지수 금융구분', 'U1'),  # (F:61) 0:일반종목, 1:KRX섹터지수 금융구분
		('KRX 섹터지수 정보통신구분', 'U1'),  # (F:62) 0:일반종목, 1:KRX섹터지수 정보통신구분
		])

	def _set_input_data(self, 시장구분=Ibook.시장구분.전체) -> None:
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 0, 시장구분)


class TR_1455(BaseTR):
	NAME, DESCRIPTION = 'TR_1455', '프로그램매매 – 사전사후공시'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) 0: 거래소, 1: 코스닥
		('순위구분', 'U1'),  # (F:01) 0: 시가총액상위순, 1: 시가총액하위순 2: 매도잔량,       3: 매도사전공시 4: 매수잔량,       5: 매수사전공시 6: 순매수순,       7: 매도금액 8: 매수금액,       9: 순매수금액
		('언어구분', 'U1'),  # (F:02) E: 영문, K: 한글
		('데이터구분', 'U1'),  # (F:03) 0: 금액, 1: 수량
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U8'),  # (F:00) 
		('한글종목명/업종명', 'U50'),  # (F:01) 
		('매도미체결수량', 'U12'),  # (F:02) 
		('매도사전공시수량', 'U12'),  # (F:03) 
		('매도합계', 'U12'),  # (F:04) 
		('매수미체결수량', 'U12'),  # (F:05) 
		('매수사전공시수량', 'U12'),  # (F:06) 
		('매수합계', 'U12'),  # (F:07) 
		('순매수', 'U12'),  # (F:08) 
		('시가총액', 'U12'),  # (F:09) 
		('현재가', 'U8'),  # (F:10) 
		('매도사후공시수량', 'U12'),  # (F:11) 
		('매수사후공시수량', 'U12'),  # (F:12) 
		])


class TR_1230_3(BaseTR):
	NAME, DESCRIPTION = 'TR_1230_3', 'ETN 현재가 조회'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 0: 거래소, 1: 코스닥
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('추적지수명', 'U40'),  # (F:01) 
		('ETN 현재가', 'U8'),  # (F:02) 
		('LV 현재가', 'U12'),  # (F:03) 
		('지수현재가', 'U12'),  # (F:04) 
		('전일IV', 'U12'),  # (F:05) 
		('거래량', np.uint64),  # (F:06) 
		('LP보유량', 'U12'),  # (F:07) 
		('만기일', 'U8'),  # (F:08) 
		])
	MULTI_OUTPUT_DTYPE = None


class TR_1140(BaseTR):
	NAME, DESCRIPTION = 'TR_1140', '현재가 종합 조회2'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('시작시간', 'U6'),  # (F:01) 090000
		('종료시간', 'U6'),  # (F:02) 공백(NULL)
		('기준금액체크', 'U0'),  # (F:03) 공백(NULL)
		('기준가격', 'U0'),  # (F:04) 공백(NULL)
		('이상이하', 'U0'),  # (F:05) 공백(NULL)
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('VWAP', 'U8'),  # (F:00) 
		('구간거래량', np.uint64),  # (F:01) 
		('PER', 'U8'),  # (F:02) 
		('EPS', 'U8'),  # (F:03) 
		('신용잔고율', 'U8'),  # (F:04) 
		('외국인비율', 'U8'),  # (F:05) 
		('증감', 'U8'),  # (F:06) 
		('52주 최고가', 'U8'),  # (F:07) 
		('52주 최고일자', 'U6'),  # (F:08) 
		('금일대비비율(고)', 'U8'),  # (F:09) 
		('52주 최저가', 'U8'),  # (F:10) 
		('52주 최저일자', 'U6'),  # (F:11) 
		('금일대비비율(저)', 'U8'),  # (F:12) 
		('구간시작 누적거래량', np.uint64),  # (F:13) 
		('구간시작 누적거래대금', np.uint64),  # (F:14) 
		('구간끝 누적거래량', np.uint64),  # (F:15) 
		('구간끝 누적거래대금', np.uint64),  # (F:16) 
		])
	MULTI_OUTPUT_DTYPE = None


class TR_1650(BaseTR):
	NAME, DESCRIPTION = 'TR_1650', '종목 신용 일별 거래 동향'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('구분', 'U1'),  # (F:01) 1: 융자, 2: 대주
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('현재가', np.uint32),  # (F:01) 
		('등락구분', 'U1'),  # (F:02) 
		('등락', np.uint32),  # (F:03) 
		('등락율', 'U4'),  # (F:04) 
		('누적거래량', np.uint64),  # (F:05) 
		('대주신규주수', np.uint32),  # (F:06) 
		('대주신규금액', 'U12'),  # (F:07) 
		('대주상환주수', np.uint32),  # (F:08) 
		('대주상환금액', 'U12'),  # (F:09) 
		('대주잔고주수', np.uint32),  # (F:10) 
		('대주잔고금액', 'U12'),  # (F:11) 
		('전일대비', np.uint32),  # (F:12) 
		('대주공여율', 'U5'),  # (F:13) 
		('대주잔고율', 'U5'),  # (F:14) 
		('잔고평균가', np.uint32),  # (F:15) 
		])


class TR_1670_1(BaseTR):
	NAME, DESCRIPTION = 'TR_1670_1', '종목별 대차 거래 내역'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('그래프 종류', 'U1'),  # (F:01) D, W, M
		('시작일', 'U8'),  # (F:02) 
		('종료일', 'U8'),  # (F:03) 
		('조회갯수', 'U4'),  # (F:04) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('현재가', 'U8'),  # (F:01) 
		('전일대비구분', 'U8'),  # (F:02) 
		('전일대비', 'U8'),  # (F:03) 
		('전일대비율', 'U4'),  # (F:04) 
		('체결주수', 'U8'),  # (F:05) 
		('상환주수', 'U8'),  # (F:06) 
		('잔고주수', 'U8'),  # (F:07) 
		('잔고금액', 'U8'),  # (F:08) 
		('일자2', 'U0'),  # (F:09) 
		])


class TR_1878(BaseTR):
	NAME, DESCRIPTION = 'TR_1878', '종목별 공매도 현황'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('시작일자', 'U8'),  # (F:01) 
		('종료일자', 'U8'),  # (F:02) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('현재가/종가/지수/기세가', 'U8'),  # (F:01) 
		('전일대비구분 (기준가)', 'U1'),  # (F:02) 
		('전일대비', 'U8'),  # (F:03) 
		('전일대비율', 'U8'),  # (F:04) 
		('시가', 'U8'),  # (F:05) 
		('고가', 'U8'),  # (F:06) 
		('저가', 'U8'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('공매도량', 'U8'),  # (F:09) 
		('공매도대금', 'U8'),  # (F:10) 
		('평균가', 'U8'),  # (F:11) 
		('누적공매도량', 'U8'),  # (F:12) 
		])


class TR_1852_10(BaseTR):
	NAME, DESCRIPTION = 'TR_1852_10', '변동성완화 종목조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U30'),  # (F:01) 
		('적용시간', 'U4'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U8'),  # (F:04) 
		('전일대비', 'U8'),  # (F:05) 
		('전일대비율', 'U8'),  # (F:06) 
		('매도호가', 'U8'),  # (F:07) 
		('매수호가', 'U8'),  # (F:08) 
		('누적거래량', np.uint64),  # (F:09) 
		('적용구분', 'U8'),  # (F:10) 
		('VI종류코드', 'U8'),  # (F:11) 
		('발동가격', 'U8'),  # (F:12) 
		('참조가격', 'U8'),  # (F:13) 
		('괴리율', 'U8'),  # (F:14) 
		])


class TR_1852_20(BaseTR):
	NAME, DESCRIPTION = 'TR_1852_20', '변동성완화 종목조회 _ 일별'
	INPUT_DTYPE = np.dtype([
		('시작일자', 'U8'),  # (F:00) 
		('종료일자', 'U8'),  # (F:01) 
		('단축코드', 'U6'),  # (F:02) 전종목: 빈칸
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('적용일', 'U8'),  # (F:00) 
		('적용시간', 'U6'),  # (F:01) 
		('해제시간', 'U6'),  # (F:02) 
		('단축코드', 'U6'),  # (F:03) 
		('종목명', 'U30'),  # (F:04) 
		('발동가격', 'U8'),  # (F:05) 
		('참조가격', 'U8'),  # (F:06) 
		('괴리율', 'U8'),  # (F:07) 
		('적용구분', 'U1'),  # (F:08) 1: 적용, 2: 해제
		('종류구분', 'U1'),  # (F:09) 1: 정적, 2:동적, 3:정적&동적
		])


class TR_3213(BaseTR):
	NAME, DESCRIPTION = 'TR_3213', '전일기준 국제원자재 동향'
	INPUT_DTYPE = np.dtype([
		('기준일', 'U8'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('심볼', 'U8'),  # (F:00) 
		('상품명', 'U20'),  # (F:01) 
		('가격', 'U8'),  # (F:02) 
		('전일대비부호', 'U1'),  # (F:03) 상한(1)상승(2)보합(3)하한(4)하락(5)기세상한(6)기세상승(7)기세하한(8)기세하한(9)
		('전일비', 'U7'),  # (F:04) 
		('일자', 'U8'),  # (F:05) 
		('거래소', 'U8'),  # (F:06) 
		])


class TR_3102_CT(BaseTR):
	NAME, DESCRIPTION = 'TR_3102_CT', '뉴스 시황_수급 동향조회'
	INPUT_DTYPE = np.dtype([
		('뉴스_카테고리구분', 'U2'),  # (F:00) “09”: 고정
		('조회일자', 'U8'),  # (F:01) “20160201”
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('시간', 'U6'),  # (F:01) 
		('제목', 'U'),  # (F:02) 
		('뉴스 구분', 'U'),  # (F:03) 뉴스 내용 조회시 이용 (F)
		('종목코드', 'U'),  # (F:04) 
		('기사번호', 'U'),  # (F:05) 뉴스 내용 조회시 이용
		])


class TR_1842_S(BaseTR):
	NAME, DESCRIPTION = 'TR_1842_S', '체결강도 분차트'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('조회갯수', 'U4'),  # (F:01) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('체결시간', 'U6'),  # (F:01) 
		('시가', np.uint32),  # (F:02) 
		('고가', np.uint32),  # (F:03) 
		('저가', np.uint32),  # (F:04) 
		('현재가', np.uint32),  # (F:05) 
		('단위체결량', 'U12'),  # (F:06) 
		('체결강도', 'U4'),  # (F:07) 
		('매도체결', 'U8'),  # (F:08) 
		('매수체결', 'U8'),  # (F:09) 
		('거래강도', 'U4'),  # (F:10) 
		])


class TR_1843_S(BaseTR):
	NAME, DESCRIPTION = 'TR_1843_S', '체결강도 일차트'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('조회갯수', 'U4'),  # (F:01) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('시가', np.uint32),  # (F:01) 
		('고가', np.uint32),  # (F:02) 
		('저가', np.uint32),  # (F:03) 
		('현재가', np.uint32),  # (F:04) 
		('단위체결량', 'U12'),  # (F:05) 
		('체결강도', 'U4'),  # (F:06) 
		('매도체결', 'U8'),  # (F:07) 
		('매수체결', 'U8'),  # (F:08) 
		('거래강도', 'U4'),  # (F:09) 
		])


class TR_0100_M8(BaseTR):
	NAME, DESCRIPTION = 'TR_0100_M8', '시장조치조건 – 단기과열종목'
	INPUT_DTYPE = np.dtype([
		('업종구분', 'U4'),  # (F:00) 0000:전체, 0001:거래소, 1001:코스닥
		('단기과열구분', 'U1'),  # (F:01) 1:지정예고, 2:지정(연장포함)
		('언어구분', 'U1'),  # (F:0２) K:한글, E:영문
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		('전일대비', np.uint32),  # (F:04) 
		('전일대비율', 'U4'),  # (F:05) 
		('매도１호가', np.uint32),  # (F:06) 
		('매수１호가', np.uint32),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('장구분', 'U1'),  # (F:09) 
		('지정일', 'U8'),  # (F:10) 
		])
	
	def _set_input_data(self,
						업종구분 : str = Ibook.시장구분.전체.zfill(4),  # 0000:전체, 0001:거래소, 1001:코스닥
                                                단기과열구분 : str = Ibook.단기과열구분.지정,  # 1:지정예고, 2:지정(연장포함)
						언어구분 : str = Ibook.언어구분.한글) -> None:
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 0, str(업종구분))
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 1, str(단기과열구분) )
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 2, str(언어구분))


class erxf_mst(BaseTR):
	NAME, DESCRIPTION = 'erxf_mst', '유렉스 종목 코드 조회 (전종목) - 선물'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('GIC', 'U13'),  # (F:00) 
		('단축코드', np.uint32),  # (F:01) 
		('한글종목명', 'U30'),  # (F:02) 
		('심볼명', 'U15'),  # (F:03) 
		('만기일', 'U8'),  # (F:04) 
		('기초자산코드', 'U2'),  # (F:05) 
		('매매단위', 'U8'),  # (F:06) 
		])


class TR_RB002(BaseTR):
	NAME, DESCRIPTION = 'TR_RB002', '현물 현재가 전종목 조회'
	INPUT_DTYPE = np.dtype([
		('구분', 'U1'),  # (F:00) 0: 전체, 1: KOSPI, 2: KOSDAQ
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),  # (F:00) 
		('단축코드', 'U6'),  # (F:01) 
		('체결시간', 'U8'),  # (F:02) 
		('현재가', np.uint32),  # (F:03) 
		('전일대비구분', 'U1'),  # (F:04) 
		('전일대비', np.uint32),  # (F:05) 
		('전일대비율', np.float32),  # (F:06) 
		('누적거래량', np.uint64),  # (F:07) 
		('누적거래대금', np.uint64),  # (F:08) 
		('단위체결량', 'U12'),  # (F:09) 
		('시가', np.uint32),  # (F:10) 
		('고가', np.uint32),  # (F:11) 
		('저가', np.uint32),  # (F:12) 
		('시가시간', 'U6'),  # (F:13) 
		('고가시간', 'U6'),  # (F:14) 
		('저가시간', 'U6'),  # (F:15) 
		('매매구분', 'U1'),  # (F:16) 1:보통                 3:신고대량 5:장종료후시간외종가   6:장종료후시간외대량 7:장종료후시간외바스켓 8:장개시전시간외종가   9:장개시전시간외대량 A:장개시전시간외바스켓 B:장중바스켓           V:장중대량
		('장구분', 'U1'),  # (F:17) 1:정규장  2:장개시전시간외  3:장종료후시간외종가  4:장종료후시간외단일가,  7:일반 Buy-In, 8:당일 Buy-In
		('호가체결구분', 'U1'),  # (F:18) 0:시초가 1:매도호가 2:매수호가
		('가중평균가', np.uint32),  # (F:19) 
		('매도1호가', np.uint32),  # (F:20) 
		('매수1호가', np.uint32),  # (F:21) 
		('거래강도', np.float32),  # (F:22) 
		('매매구분별거래량', np.uint64),  # (F:23) 17번 장구분별 거래량
		('체결강도', np.float32),  # (F:24) 
		('체결매도매수구분', 'U1'),  # (F:25) 
		])


class TR_ID001(BaseTR):
	NAME, DESCRIPTION = 'TR_ID001', '홍콩 ELW 거래량 상위 종목 조회'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('홍콩ELW 종목코드', 'U15'),  # (F:00) 
		('종목명', 'U40'),  # (F:01) 
		('현재가', 'U17'),  # (F:02) 
		('행사가격', 'U17'),  # (F:03) 
		('거래량', np.uint64),  # (F:04) 
		('콜/풋구분', 'U1'),  # (F:05) 
		])


class TR_1852_30(BaseTR):
	NAME, DESCRIPTION = 'TR_1852_30', '시장조치종목 조회1'
	INPUT_DTYPE = np.dtype([
		('조회구분', 'U1'),  # (F:00) 0:저유동성종목, 1:이상급등종목, 2:공매도과열종목
		('장구분', 'U1'),  # (F:01) 0: 거래소, 1: 코스닥, 2: 전체
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U30'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U8'),  # (F:03) 
		('전일대비', 'U8'),  # (F:04) 
		('전일대비율', 'U8'),  # (F:05) 
		('매도호가', 'U8'),  # (F:06) 
		('매수호가', 'U8'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('장구분', 'U1'),  # (F:09) 
		])


class TR_0100_M1(BaseTR):
	NAME, DESCRIPTION = 'TR_0100_M1', '1852화면 투자관리 종목 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U4'),  # (F:00) 0000: 전체, 0001: 거래소, 1001: 코스닥
		('언어구분', 'U1'),  # (F:01) K or 공백: 한글, E: 영문
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U30'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U8'),  # (F:03) 
		('전일대비', 'U8'),  # (F:04) 
		('전일대비율', 'U8'),  # (F:05) 
		('매도1호가', 'U8'),  # (F:06) 
		('매수1호가', 'U8'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('장구분', 'U1'),  # (F:09) 
		])


class TR_0100_M2(BaseTR):
	NAME, DESCRIPTION = 'TR_0100_M2', '1852화면 투자주의/경고/위험 종목 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U4'),  # (F:00) 0000: 전체, 0001: 거래소, 1001: 코스닥
		('시장조치구분', 'U1'),  # (F:01) 0: 정상, 1:주의, 2: 경고, 3: 위험
		('언어구분', 'U1'),  # (F:02) K or 공백: 한글, E: 영문
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U30'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U8'),  # (F:03) 
		('전일대비', 'U8'),  # (F:04) 
		('전일대비율', 'U8'),  # (F:05) 
		('매도1호가', 'U8'),  # (F:06) 
		('매수1호가', 'U8'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('장구분', 'U1'),  # (F:09) 
		])


class TR_0100_M7(BaseTR):
	NAME, DESCRIPTION = 'TR_0100_M7', '1852화면 투자주의환기 종목 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U4'),  # (F:00) 0: 코스피, 1:코스닥, 9: 전체
		('시장조치구분', 'U1'),  # (F:01) 1: 투자주의환기
		('언어구분', 'U1'),  # (F:02) K or 공백: 한글, E: 영문
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U30'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U8'),  # (F:03) 
		('전일대비', 'U8'),  # (F:04) 
		('전일대비율', 'U8'),  # (F:05) 
		('매도1호가', 'U8'),  # (F:06) 
		('매수1호가', 'U8'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('장구분', 'U1'),  # (F:09) 
		])


class TR_0100_M6(BaseTR):
	NAME, DESCRIPTION = 'TR_0100_M6', '1852화면 불성실공시지정/거래정지 종목 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U4'),  # (F:00) 0: 코스피, 1:코스닥, 9: 전체
		('시장조치구분', 'U1'),  # (F:01) 1: 불성실공시지정, 2: 거래정지
		('언어구분', 'U1'),  # (F:02) K or 공백: 한글, E: 영문
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U30'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U8'),  # (F:03) 
		('전일대비', 'U8'),  # (F:04) 
		('전일대비율', 'U8'),  # (F:05) 
		('매도1호가', 'U8'),  # (F:06) 
		('매수1호가', 'U8'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('장구분', 'U1'),  # (F:09) 
		])


class fut_prod_mst(BaseTR):
	NAME, DESCRIPTION = 'fut_prod_mst', 'KOSPI 선물 품목 정보 조회'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('기초자산코드', 'U2'),  # (F:00) 
		('기초자산명', 'U40'),  # (F:01) 
		('기초자산ID', 'U3'),  # (F:02) 
		('축약종목명', 'U4'),  # (F:03) 
		('호가변동폭', 'U6'),  # (F:04) 
		('거래단위', 'U8'),  # (F:05) 
		])


class TR_SDIA_M1(BaseTR):
	NAME, DESCRIPTION = 'TR_SDIA_M1', '주식 종목 점수 조회'
	INPUT_DTYPE = np.dtype([
		('종목코드', 'U6'),  # (F:00) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),  # (F:00) 
		('종목명', 'U40'),  # (F:01) 
		('업데이트일자', 'U8'),  # (F:02) 
		('총점', 'U8'),  # (F:03) 
		('총점색깔', 'U8'),  # (F:04) 
		('업종평균', 'U8'),  # (F:05) 
		('백분율', 'U8'),  # (F:06) 
		('순위표시', 'U8'),  # (F:07) 
		('점수산출 종목수', 'U8'),  # (F:08) 
		('재무점수', 'U8'),  # (F:09) 
		('재무평가', 'U40'),  # (F:10) 
		('현재가치점수', 'U8'),  # (F:11) 
		('현재가치평가', 'U40'),  # (F:12) 
		('상승동력점수', 'U8'),  # (F:13) 
		('상승동력평가', 'U40'),  # (F:14) 
		('주도주체', 'U40'),  # (F:15) 
		('주도주체평가', 'U40'),  # (F:16) 
		('주도주체동향', 'U40'),  # (F:17) 
		('주도주체손익상황', 'U8'),  # (F:18) 
		('주가평가', 'U40'),  # (F:19) 
		('주가방향', 'U40'),  # (F:20) 
		('주가강도', 'U40'),  # (F:21) 
		('변동성', 'U40'),  # (F:22) 
		('거래량평가', np.uint64),  # (F:23) 
		('거래량방향', np.uint64),  # (F:24) 
		('거래량강도', np.uint64),  # (F:25) 
		])
	MULTI_OUTPUT_DTYPE = None


class TR_2251_10(BaseTR):
	NAME, DESCRIPTION = 'TR_2251_10', '2251화면 투자자별 포지션 분석 데이터'
	INPUT_DTYPE = np.dtype([
		('최근물/차근물', 'U1'),  # (F:00) 최근물: 1 차근물: 2
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U8'),  # (F:00) 
		('현재가', 'U4'),  # (F:01) 
		('행사가격', 'U4'),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		])


class TR_2251(BaseTR):
	NAME, DESCRIPTION = 'TR_2251', '2251화면 투자주체별 포지션분석 확정손익 추가'
	INPUT_DTYPE = np.dtype([
		('최근물/차근물', 'U1'),  # (F:00) 최근물: 1 차근물: 2
		('당일/누적', 'U1'),  # (F:01) 당일: 1 누적: 2
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('투자자코드', 'U2'),  # (F:00) 
		('종목코드', 'U8'),  # (F:01) 
		('매수수량', np.uint64),  # (F:02) 
		('매수가격', np.uint64),  # (F:03) 
		('매도수량', np.uint64),  # (F:04) 
		('매도가격', np.uint64),  # (F:05) 
		('순매수수량', np.uint64),  # (F:06) 
		('순매수가격', np.uint64),  # (F:07) 
		])


class TR_0100_M6(BaseTR):
	NAME, DESCRIPTION = 'TR_0100_M6', '1852화면 불성실공시지정/거래정지 종목 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U4'),  # (F:00) 0: 코스피, 1:코스닥, 9: 전체
		('시장조치구분', 'U1'),  # (F:01) 1: 불성실공시지정, 2: 거래정지
		('언어구분', 'U1'),  # (F:02) K or 공백: 한글, E: 영문
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U30'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U8'),  # (F:03) 
		('전일대비', 'U8'),  # (F:04) 
		('전일대비율', 'U8'),  # (F:05) 
		('매도1호가', 'U8'),  # (F:06) 
		('매수1호가', 'U8'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('장구분', 'U1'),  # (F:09) 
		])


class TR_1856_IND(BaseTR):
	NAME, DESCRIPTION = 'TR_1856_IND', '시가총액 상위 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) “0”:코스피, “1”: 코스닥, “2”:전체
		('조회갯수', 'U3'),  # (F:01) 1~999
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U20'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		('전일대비', np.uint32),  # (F:04) 
		('전일대비율', 'U4'),  # (F:05) 
		('누적거래량', np.uint64),  # (F:06) 
		('누적거래대금', np.uint64),  # (F:07) 
		('주가이격', 'U6'),  # (F:08) 
		('거래이격', 'U6'),  # (F:09) 
		('상대강도', 'U6'),  # (F:10) 
		('투자심리', 'U6'),  # (F:11) 
		('PER', 'U8'),  # (F:12) 
		('시가총액', 'U12'),  # (F:13) 
		('시가총액비중', 'U6'),  # (F:14) 
		('시가', np.uint32),  # (F:15) 
		('고가', np.uint32),  # (F:16) 
		('저가', np.uint32),  # (F:17) 
		('발생주식수', 'U12'),  # (F:18) 
		('매도1호가', np.uint32),  # (F:19) 
		('매수1호가', np.uint32),  # (F:20) 
		('매도총잔량', 'U10'),  # (F:21) 
		('매수총잔량', 'U10'),  # (F:22) 
		('전일거래량', np.uint64),  # (F:23) 
		('외국인지분율', 'U6'),  # (F:24) 
		('자산총계', 'U12'),  # (F:25) 
		('부채총계', 'U12'),  # (F:26) 
		('매출액', 'U12'),  # (F:27) 
		('매출액증가율', 'U8'),  # (F:28) 
		('영업이익', 'U12'),  # (F:29) 
		('영업이익증가율', 'U8'),  # (F:30) 
		('순이익', 'U12'),  # (F:31) 
		('주당순이익', 'U8'),  # (F:32) 
		('배당금', 'U12'),  # (F:33) 
		('ROE', 'U8'),  # (F:34) 
		('ROA', 'U6'),  # (F:35) 
		('PBR', 'U6'),  # (F:36) 
		('유보율', 'U8'),  # (F:37) 
		('52주최고가', np.uint32),  # (F:38) 
		('52주최저가', np.uint32),  # (F:39) 
		])


class TR_1505_09(BaseTR):
	NAME, DESCRIPTION = 'TR_1505_09', '테마분석 – 신규상장및등록'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U1'),  # (F:00) “0”:코스피, “1”: 코스닥, “2”:전체
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		('전일대비', np.uint32),  # (F:04) 
		('전일대비율', np.float32),  # (F:05) 
		('신규상장일', 'U8'),  # (F:06) 
		('거래강도', np.float32),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('업종구분', 'U1'),  # (F:09) 
		('발행가', np.uint32),  # (F:10) 
		('발행가대비구분', 'U1'),  # (F:11) 
		('발행가대비', np.uint32),  # (F:12) 
		('발행가대비율', np.float32),  # (F:13) 
		])


class TR_0100_M5(BaseTR):
	NAME, DESCRIPTION = 'TR_0100_M5', '1852 투자위험예고'
	INPUT_DTYPE = np.dtype([
		('장,업종구분', 'U0'),  # (F:00) 0,1,2001(전체종합)
		('언어구분', 'U0'),  # (F:01) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		('전일대비', np.uint32),  # (F:04) 
		('전일대비율', 'U4'),  # (F:05) 
		('매도1호가', np.uint32),  # (F:06) 
		('매수1호가', np.uint32),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('시장경고위험예고구분', 'U0'),  # (F:09) 
		('장구분', 'U1'),  # (F:10) 
		])


class TR_1400(BaseTR):
	NAME, DESCRIPTION = 'TR_1400', '외국인 한도 추이'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U0'),  # (F:00) 
		('시작일', 'U8'),  # (F:01) 
		('종료일', 'U8'),  # (F:02) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U0'),  # (F:00) 
		('총한도', 'U0'),  # (F:01) 
		('외국인소유', 'U0'),  # (F:02) 
		('잔여한도', 'U0'),  # (F:03) 
		('소진율', 'U0'),  # (F:04) 
		('순매수량', 'U0'),  # (F:05) 
		('누적순매수량', 'U0'),  # (F:06) 
		('종가', 'U0'),  # (F:07) 
		('전일대비구분', 'U0'),  # (F:08) 
		('전일대비', 'U0'),  # (F:09) 
		('누적거래량', np.uint64),  # (F:10) 
		('외국계창구비중', 'U0'),  # (F:11) 
		])


class TR_1505_12(BaseTR):
	NAME, DESCRIPTION = 'TR_1505_12', '조건별시세-거래정지'
	INPUT_DTYPE = np.dtype([
		('장,업종구분', 'U0'),  # (F:00) 0001,1001,0000(전체)
		('언어구분', 'U0'),  # (F:01) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('한글종목명', 'U20'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		('전일대비', np.uint32),  # (F:04) 
		('전일대비율', 'U4'),  # (F:05) 
		('매도1호가', np.uint32),  # (F:06) 
		('매수1호가', np.uint32),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('장구분', 'U1'),  # (F:09) 
		('정리매매시작일', 'U8'),  # (F:10) 
		('정리매매종료일', 'U8'),  # (F:11) 
		])


class TR_1131_3(BaseTR):
	NAME, DESCRIPTION = 'TR_1131_3', 'ETF 주가추이'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),
		('장구분', 'U1'),
		('시간구분', 'U1')
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),
		('거래일자', 'U8'),
		('거래시간', 'U6'),
		('ETF현재가', np.uint32),
		('ETF전일대비구분', 'U1'),
		('ETF전일대비', np.uint32),
		('ETF거래량', np.uint64),
		('NAV현재가', np.float32),
		('NAV전일대비구분', 'U1'),
		('NAV전일대비', np.float32),
		('괴리도', np.float32),
		('괴리율', np.float32),
		('추적오차율', np.float32),
		('업종코드', 'U4'),
		('추적지수현재가', np.float32)
		])


class TR_1110_11(BaseTR):
	NAME, DESCRIPTION = 'TR_1110_11', '현재가종합화면용상단왼쪽'
	INPUT_DTYPE = np.dtype([('단축코드', 'U6')])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('전일종가', np.uint32),            # 0
		('전일등락', 'U1'),                 # 1
		('전일등락폭', np.uint32),           # 2
		('전일등락율', np.float16),          # 3
		('ECN현재가', np.uint32),           # 4
		('ECN전일대비구분', 'U1'),            # 5
		('ECN전일대비', np.uint32),          # 6
		('ECN전일대비율', np.float16),       # 7
		('52주최고주가', np.uint32),         # 8
		('52주최저주가', np.uint32),         # 9
		('52주최고일자', 'U8'),              # 10
		('52주최저일자', 'U8'),              # 11
		('상한가', np.uint32),               # 12
		('하한가', np.uint32),               # 13
		('액면가', np.uint32),               # 14
		('시가총액', np.uint64),             # 15
		('외인소유량', np.uint64),            # 16
		('외인소진율', np.float16),           # 17
		('자본금', np.uint64),               # 18
		('상장주식수', np.uint64),            # 19
		('대용가', np.uint32),               # 20
		('EPS', np.uint32),                 # 21
		('PER', np.float16),                 # 22
		('전일외국인소유량',  np.uint64),       # 23
		('현재가',  np.uint32),                # 24
		('전일기관순매수',  np.int64),         # 25
		('전전일기관순매수',  np.int64),        # 26
		('전전전일기관순매수',  np.int64),       # 27
		('전일외국인순매수',  np.int64),        # 28
		('전전일외국인순매수',  np.int64),       # 29
		('전전전일외국인순매수',   np.int64)     # 30
	])
	MULTI_OUTPUT_DTYPE = None

	def _set_input_data(self, code6) -> None:
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 0, str(code6))
		return


class TR_1862(BaseTR):
	NAME, DESCRIPTION = 'TR_1862', '시가대비상승율조회'
	REALTIME_AVAILABLE = False
	INPUT_DTYPE = None
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),           # 0
		('종목명', 'U20'),            # 1
		('현재가', np.uint32),        # 2
		('시가', np.uint32),          # 3
		('시가대비상승율', np.float16) # 4
	])


class TR_RB002(BaseTR):
	NAME, DESCRIPTION = 'TR_RB002', '현물현재가전종목조회'
	REALTIME_AVAILABLE = False
	INPUT_DTYPE = np.dtype([('구분', 'U1')])  # (F:00) 0: 전체, 1: KOSPI, 2: KOSDAQ
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('표준코드', 'U12'),          # 0
		('단축코드', 'U6'),           # 1
		('체결시간', 'U8'),           # 2
		('현재가', 'U9'),             # 3
		('전일대비구분', 'U1'),        # 4
		('전일대비', np.uint32),       # 5
		('전일대비율', np.float16),    # 6
		('누적거래량', np.uint64),     # 7
		('누적거래대금', np.uint64),   # 8
		('단위체결량', np.uint32),     # 9
		('시가', np.uint32),          # 10
		('고가', np.uint32),          # 11
		('저가', np.uint32),          # 12
		('시가시간', np.uint16),       # 13
		('고가시간', np.uint16),       # 14
		('저가시간', np.uint16),       # 15
		('매매구분', 'U1'),            # 16
		('장구분', 'U1'),              # 17
		('호가체결구분', 'U1'),        # 18
		('가중평균가', np.uint32),     # 19
		('매도1호가', np.uint32),      # 20
		('매수1호가', np.uint32),      # 21
		('거래강도', np.float16),      # 22
		('매매구분별거래량', np.uint64),# 23
		('체결강도', np.float16),      # 24
		('체결매도매수구분', 'U1')      # 25
	])

	def _set_input_data(self, 시장구분=Ibook.시장구분.전체) -> None:
		self._indi_instance.dynamicCall("SetSingleData(int, QString)", 0, 시장구분)
		return




class SABA101U1(BaseTR):
	NAME, DESCRIPTION = 'SABA101U1', '현물/ELW일반주문(매도/매수)'
	REALTIME_AVAILABLE = False
	INPUT_DTYPE = np.dtype([
		('계좌번호',         'U11'),         # 0
		('계좌상품',         'U2'),          # 1
		('계좌비밀번호',      'U9'),         # 2
		# ('계좌관리부점코드', 'U3'),          # 3 : 생략
		# ('시장거래구분',    'U1'),               # 4 : 생략
		('선물대용매도여부',  'U1'),            # 5
		('신용거래구분',      'U2'),               # 6
		('매도 / 매수 구분',  'U1'),           # 7
		('종목코드',         'U12'),                # 8
		('주문수량',        'U10'),                # 9
		('주문가격',        'U20'),                # 10
		('정규시간외구분코드', 'U1'),        # 11
		('호가유형코드',      'U1'),               # 12
		('주문조건코드',      'U1'),               # 13
		('신용대출통합주문구분코드', 'U1'),     # 14
		('신용대출일자',      'U8'),               # 15
		# ('원주문번호',       'U10'),               # 16
		# ('프로그램매매여부',   'U2'),            # 20
		('결과메시지 처리여부', 'U1')            # 21
	])
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('주문번호', 'U10'),
		('ORC 주문번호', 'U20'),
		('Message구분', 'U1'),
		('Message1', 'U35'),
		('Message2', 'U35'),
		('Message3', 'U35')
	])
	MULTI_OUTPUT_DTYPE = None

	def _set_input_data(self,
						계좌번호, 계좌비밀번호,
						신용거래구분,
						매도매수구분,
						종목코드7, 주문수량, 주문가격=None,
						계좌상품='01',
						선물대용매도여부=Ibook.선물대용매도여부.일반,
						정규시간외구분코드=Ibook.정규시간외구분코드.정규장,
						호가유형코드=Ibook.호가유형코드.시장가, 주문조건코드=Ibook.주문조건코드.일반,
						신용대출통합주문구분코드=Ibook.신용대출통합주문구분코드.해당없음, 신용대출일자=None,
						결과메시지_처리여부=Ibook.결과메세지_처리여부.네
						) -> None:
		TR_inst = self._indi_instance
		TR_inst.dynamicCall("SetSingleData(int, QString)", 0, str(계좌번호))  # 계좌번호
		TR_inst.dynamicCall("SetSingleData(int, QString)", 1, 계좌상품)  # 상품구분
		TR_inst.dynamicCall("SetSingleData(int, QString)", 2, 계좌비밀번호)  # 비밀번호
		TR_inst.dynamicCall("SetSingleData(int, QString)", 5, 선물대용매도여부)  # 선물대용매도구분
		TR_inst.dynamicCall("SetSingleData(int, QString)", 6, 신용거래구분)  # 신용거래구분
		TR_inst.dynamicCall("SetSingleData(int, QString)", 7, 매도매수구분)  # 매수매도 구분
		TR_inst.dynamicCall("SetSingleData(int, QString)", 8, 종목코드7)  # 종목코드
		TR_inst.dynamicCall("SetSingleData(int, QString)", 9, str(주문수량))  # 주문수량
		if 호가유형코드 == Ibook.호가유형코드.시장가:
			pass
		elif 주문가격 is not None:
			TR_inst.dynamicCall("SetSingleData(int, QString)", 10, str(주문가격))  # 주문가격
		else:
		        raise PriceSettingError("주문가격 설정 에러 ")
		TR_inst.dynamicCall("SetSingleData(int, QString)", 11, 정규시간외구분코드)  # 정규장
		TR_inst.dynamicCall("SetSingleData(int, QString)", 12, 호가유형코드)  # 호가유형, 1: 시장가, X:최유리, Y:최우선
		TR_inst.dynamicCall("SetSingleData(int, QString)", 13, 주문조건코드)  # 주문조건, 0:일반, 3:IOC, 4:FOK
		TR_inst.dynamicCall("SetSingleData(int, QString)", 14, 신용대출통합주문구분코드)  # 신용대출
		if 신용대출일자 is not None:
			TR_inst.dynamicCall("SetSingleData(int, QString)", 15, 신용대출일자)  # 신용대출일 YYYYMMDD
		TR_inst.dynamicCall("SetSingleData(int, QString)", 21, 결과메시지_처리여부)  # 결과 출력 여부
		return

	def proc_rcvd_data(self):
		super().proc_rcvd_data()
		Logger.write_order_history(self.single_output[0])


class SABA102U1(BaseTR):#
	NAME, DESCRIPTION = 'SABA102U1', '현물/ELW 일반 주문(정정/취소)'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('계좌상품', 'U2'),  # (F:01) 항상 ‘01’
		('계좌비밀번호', 'U9'),  # (F:02) 
		('계좌관리부점코드', 'U3'),  # (F:03) 생략
		('시장거래구분', 'U1'),  # (F:04) 생략, 2:단주
		('선물대용매도여부', 'U1'),  # (F:05) 0:일반  		1:KOSPI 2:KOSDAQ		3:예탁담보
		('신용거래구분', 'U2'),  # (F:06) 00:보통              	01:유통융자매수 03:자기융자매수      	05:유통대주매도 07:자기대주매도     	11:유통융자매도상환 12:유통융자현금상환 	33:자기융자매도상환 34:자기융자현금상환 	55:유통대주매수상환 56:유통대주현물상환 	77:자기대주매수상환 78:자기대주현물상환 	91:예탁담보대출 92:예탁담보매도상환 	93:예탁담보현금상환 96:주식청약대출     	97:주식청약상환
		('매도/매수 구분', 'U1'),  # (F:07) 3:정정  		4:취소
		('종목코드', 'U12'),  # (F:08) 현물: 단축코드(A포함)  (예:A005930) ELW: 단축코드 (J포함)  (예:J505236) ETN: 단축코드 (Q포함)  (예:Q500001)
		('주문수량', 'U10'),  # (F:09) 
		('주문가격', 'U20'),  # (F:10) 장전시간외, 시간외종가 주문시 “0”
		('정규시간외구분코드', 'U1'),  # (F:11) 1:정규장               2:장개시전시간외 3:장종료후시간외종가   4:장종료후시간외단일가 5:장종료후시간외대량
		('호가유형코드', 'U1'),  # (F:12) 1:시장가    2:지정가    I:조건부지정가       X:최유리    Y:최우선    Z.변동없음(정정주문시)
		('주문조건코드', 'U1'),  # (F:13) 0:일반         3:IOC         4: FOK
		('신용대출통합주문구분코드', 'U1'),  # (F:14) 
		('신용대출일자', 'U8'),  # (F:15) 
		('원주문번호', 'U10'),  # (F:16) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('주문번호', 'U10'),  # (F:00) 
		('ORC 주문번호', 'U20'),  # (F:01) 
		('Message구분', 'U1'),  # (F:02) 
		('Message1', 'U35'),  # (F:03) 
		('Message2', 'U35'),  # (F:04) 
		('Message3', 'U35'),  # (F:05) 
		])
	MULTI_OUTPUT_DTYPE = None

	def _set_input_data(self,
						계좌번호, 계좌비밀번호,
						신용거래구분,
						매도매수구분,
						종목코드7, 주문수량, 원주문번호,
						주문가격=None,
						계좌상품='01',
						선물대용매도여부=Ibook.선물대용매도여부.일반,
						정규시간외구분코드=Ibook.정규시간외구분코드.정규장,
						호가유형코드=Ibook.호가유형코드.변동없음, 주문조건코드=Ibook.주문조건코드.일반,
						신용대출통합주문구분코드=Ibook.신용대출통합주문구분코드.해당없음, 신용대출일자=None,
						결과메시지_처리여부=Ibook.결과메세지_처리여부.네
						) -> None:
		TR_inst = self._indi_instance
		TR_inst.dynamicCall("SetSingleData(int, QString)", 0, str(계좌번호))  # 계좌번호
		TR_inst.dynamicCall("SetSingleData(int, QString)", 1, 계좌상품)  # 상품구분
		TR_inst.dynamicCall("SetSingleData(int, QString)", 2, 계좌비밀번호)  # 비밀번호
		TR_inst.dynamicCall("SetSingleData(int, QString)", 5, 선물대용매도여부)  # 선물대용매도구분
		TR_inst.dynamicCall("SetSingleData(int, QString)", 6, 신용거래구분)  # 신용거래구분
		TR_inst.dynamicCall("SetSingleData(int, QString)", 7, 매도매수구분)  # 매수매도 구분
		TR_inst.dynamicCall("SetSingleData(int, QString)", 8, 종목코드7)  # 종목코드
		TR_inst.dynamicCall("SetSingleData(int, QString)", 9, str(주문수량))  # 주문수량
		if 호가유형코드 == Ibook.호가유형코드.시장가:
			pass
		elif 주문가격 is not None:
			TR_inst.dynamicCall("SetSingleData(int, QString)", 10, str(주문가격))  # 주문가격
		else:
		        pass
		        #raise PriceSettingError("주문가격 설정 에러 ")
		TR_inst.dynamicCall("SetSingleData(int, QString)", 11, 정규시간외구분코드)  # 정규장
		TR_inst.dynamicCall("SetSingleData(int, QString)", 12, 호가유형코드)  # 호가유형, 1: 시장가, X:최유리, Y:최우선
		TR_inst.dynamicCall("SetSingleData(int, QString)", 13, 주문조건코드)  # 주문조건, 0:일반, 3:IOC, 4:FOK
		TR_inst.dynamicCall("SetSingleData(int, QString)", 14, 신용대출통합주문구분코드)  # 신용대출
		if 신용대출일자 is not None:
			TR_inst.dynamicCall("SetSingleData(int, QString)", 15, 신용대출일자)  # 신용대출일 YYYYMMDD
		TR_inst.dynamicCall("SetSingleData(int, QString)", 16, 원주문번호)      
		#TR_inst.dynamicCall("SetSingleData(int, QString)", 21, 결과메시지_처리여부)  # 결과 출력 여부
		return

	def proc_rcvd_data(self):
		super().proc_rcvd_data()
		Logger.write_order_history(self.single_output[0])


class SABA110U1(BaseTR):
	""" ▶▶ 현물 단일계좌 복수종목 주문은 10건까지만 동시 전송이 가능합니다.
		▶▶ setmultidata를 호출하여 주문 정보를 세팅하실 때 반드시 32번 Field 까지 모두 처리를 해주셔야만 정상적인 주문이 가능합니다.
	"""
	NAME, DESCRIPTION = 'SABA110U1', '현물 단일계좌 복수종목 주문'
	SINGLE_INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),
		('비밀번호', 'U4'),
		('주문전송구분', 'U1')  # 항상 “Y”
	])
	MULTI_INPUT_DTYPE = np.dtype([
		('상품', 'U2'),  # 항상 ‘01’
		('계좌관리부점코드', 'U3'),  # 생략
		('시장거래구분', 'U1'),  # 생략, 2:단주
		('선물대용매도구분', 'U1'),  # 0:일반  1:KOSPI  2:KOSDAQ  3:예탁담보  
		('신용거래구분', 'U2'),  # 00:보통 01:유통융자매수 03:자기융자매수 05:유통대주매도 07:자기대주매도 11:유통융자매도상환 12:유통융자현금상환 33:자기융자매도상환 34:자기융자현금상환 55:유통대주매수상환 56:유통대주현물상환 	77:자기대주매수상환 78:자기대주현물상환 91:예탁담보대출 92:예탁담보매도상환 93:예탁담보현금상환 96:주식청약대출 97:주식청약상환
		('매도매수구분', 'U1'),  # 1:매도 2:매수 3:정정 4:취소
		('종목코드', 'U12'),  # 현물: 단축코드(A포함)  (예:A005930)  ELW: 단축코드 (J포함)  (예:J505236)  ETN: 단축코드 (Q포함)  (예:Q500001)
		('주문수량', 'U10'),  # 	
		('주문가격', 'U10'),  # 장전시간외, 시간외종가 주문시 “0”
		('정규시간외구분코드', 'U1'),  # 1:정규장 2:장개시전시간외 3:장종료후시간외종가 4:장종료후시간외단일가 5:장종료후시간외대량
		('호가유형코드', 'U1'),  # 1:시장가    2:지정가    I:조건부지정가       X:최유리    Y:최우선    Z.변동없음(정정주문시) 
		('주문조건구분코드', 'U1'),  # 0:일반         3:IOC         4: FOK
		('신용대출통합주문구분코드', 'U1'),  # 반드시 “” Setting
		('신용대출일', 'U8'),  # 반드시 “”Setting
		('원주문번호', 'U10'),  # ,	
		('주문검증구분', 'U1'),  # 항상“N”
		('주문필러1', 'U2'),  # 반드시 “”Setting
		('주문필러2', 'U1'),  # 반드시 “”Setting
		('주문필러3', 'U2'),  # 반드시 “”Setting
		('주문필러4', 'U1'),  # 반드시 “”Setting
		('주문필러5', 'U1'),  # 반드시 “”Setting
		('주문필러6', 'U1'),  # 반드시 “”Setting
		('주문필러7', 'U1'),  # 반드시 “”Setting
		('주문필러8', 'U12'),  # 반드시 “”Setting
		('주문필러9', 'U20'),  # 반드시 “”Setting
		('주문필러10', 'U1'),  # 반드시 “”Setting
		('주문필러11', 'U1'),  # 반드시 “”Setting
		('주문필러12', 'U1'),  # 반드시 “”Setting
		('주문필러13', 'U1'),  # 반드시 “”Setting
		('주문필러14', 'U1'),  # 반드시 “”Setting
		('주문필러15', 'U6'),  # 반드시 “”Setting
		('주문필러16', 'U3'),  # 반드시 “”Setting
		('주문필러17', 'U1'),  # 반드시 “”Setting
		])
	INPUT_DTYPE = (SINGLE_INPUT_DTYPE, MULTI_INPUT_DTYPE)
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('결과메세지', 'U100')
	])
	MULTI_OUTPUT_DTYPE = np.dtype([
		('주문번호', 'U10'),
		('채널주문번호', 'U20'),
		('오류코드', 'U5'),
		('주문메세지', 'U100')
	])


class SABA200QB(BaseTR):
	NAME, DESCRIPTION = 'SABA200QB', '잔고 및 주문 체결 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('상품구분', 'U2'),  # (F:01) 항상 ‘01’
		('비밀번호', 'U4'),  # (F:02) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),  # (F:00) 
		('종목명', 'U50'),  # (F:01) 
		('결제일 잔고 수량', 'U18'),  # (F:02) 
		('매도 미체결 수량', 'U18'),  # (F:03) 
		('매수 미체결 수량', 'U18'),  # (F:04) 
		('현재가', 'U20'),  # (F:05) 
		('평균단가', 'U20'),  # (F:06) 일반 평균 단가
		('신용잔고수량', 'U10'),  # (F:07) 
		('코스피대용수량', 'U18'),  # (F:08) 
		])


class SABA231Q1(BaseTR):
	NAME, DESCRIPTION = 'SABA231Q1', '현물 체결/미체결 조회(당일)'
	INPUT_DTYPE = np.dtype([
		('매매일자', 'U8'),  # (F:00) 공백으로 입력(당일 현물 체결 미체결 조회로만 쓰임)
		('계좌번호', 'U11'),  # (F:01) 
		('비밀번호', 'U4'),  # (F:02) 
		('장구분', 'U2'),  # (F:03) 00:전체  		01:KOSPI 02:KOSDAQ 		03:OTCBB   04:ECN  		05:단주  11:매도주문  		12:매수주문
		('체결구분', 'U1'),  # (F:04) 0:전체  		1:체결   2:미체결
		('건별구분', 'U1'),  # (F:05) 0:합산(주문건별 합산)  	1:건별(체결건)
		('입력종목코드', 'U12'),  # (F:06) *:전체
		('계좌상품코드', 'U2'),  # (F:07) 공백 : 전체 01: 종합계좌    10:코스피선물옵션 11: 코스닥선물옵션    21:증권저축잔고
		('작업구분', 'U1'),  # (F:08) “Y”(AH658Q_1->Y / AH658Q_1-> N 입력)
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('매도체결금액', 'U20'),  # (F:00) 
		('매수체결금액', 'U20'),  # (F:01) 
		('약정금액', 'U20'),  # (F:02) 
		('환산약정', 'U20'),  # (F:03) 
		('체결율', 'U20'),  # (F:04) 
		])
	MULTI_OUTPUT_DTYPE = np.dtype([
		('주문번호', 'U18'),  # (F:00) 
		('원주문번호', 'U18'),  # (F:01) 
		('시장거래구분', 'U1'),  # (F:02) 
		('시장구분명', 'U20'),  # (F:03) 
		('매수매도구분', 'U1'),  # (F:04) 1:매도, 2:매수
		('매매구분명', 'U40'),  # (F:05) 
		('정/취 구분', 'U1'),  # (F:06) 
		('정/취 구분면', 'U10'),  # (F:07) 정정,취소
		('정규시간외구분코드', 'U1'),  # (F:08) 1:정규장               2:장개시전시간외 3:장종료후시간외종가   4:장종료후시간외단일가 5:경매매
		('호가유형코드', 'U1'),  # (F:09) 
		('대량매매구분코드', 'U1'),  # (F:10) 
		('자사주신고서ID', 'U5'),  # (F:11) 
		('매체구분명', 'U20'),  # (F:12) 
		('출력종목코드', 'U12'),  # (F:13) 
		('종목명', 'U50'),  # (F:14) 
		('주문수량', 'U18'),  # (F:15) 
		('주문단가', 'U20'),  # (F:16) 
		('상품구분', 'U2'),  # (F:17) 
		('주문시간', 'U6'),  # (F:18) 
		('거부코드', 'U4'),  # (F:19) 
		('거부코드명', 'U40'),  # (F:20) 
		('확인구분', 'U1'),  # (F:21) 0:정상			1:거부 2:접속실패		3:거래소거부
		('체결시간', 'U6'),  # (F:22) 
		('입력자', 'U10'),  # (F:23) 
		('체결수량', 'U18'),  # (F:24) 
		('체결단가', 'U20'),  # (F:25) 주문건별 합산은 평균단가
		('미체결수량', 'U18'),  # (F:26) 
		('대출일', 'U8'),  # (F:27) 
		('확인수량', 'U18'),  # (F:28) 
		('신용구분', 'U2'),  # (F:29) 00:일반			01:유통융자매수 03:자기융자매수		11:유통융자매도상환
		('가격유형명', 'U30'),  # (F:30) 지정가, 시장가, 조건부지정가, 시간외종가...
		('상태명', 'U20'),  # (F:31) 의뢰, 접수, 확인, 거부
		('현재가', 'U20'),  # (F:32) 
		('주문조건구분코드', 'U1'),  # (F:33) 0: 일반(FAS)    3: IOC(FAK)   4: FOK
		('주문조건구분명', 'U20'),  # (F:34) 
		('주문조건수량', 'U18'),  # (F:35) 
		('운용사지시번호', 'U12'),  # (F:36) 
		('공매도구분코드', 'U2'),  # (F:37) 00 : 해당없음  01: 일반공매도  02: 차입증권매도  06 : 기타매도
		('매매단위수량', 'U18'),  # (F:38) 
		])


class SABA233Q1(BaseTR):
	NAME, DESCRIPTION = 'SABA233Q1', '계좌별 종목별 매매내역 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('상품구분', 'U2'),  # (F:01) 항상 ‘01’
		('비밀번호', 'U4'),  # (F:02) 
		('종목코드', 'U12'),  # (F:03) ‘A’+  단축코드 (A005930)
		('시작일', 'U8'),  # (F:04) 
		('종료일', 'U8'),  # (F:05) 
		('구분', 'U1'),  # (F:06) 매매일 : 1, 결제일 : 2
		('조회구분', 'U1'),  # (F:07) 전체 : 0, 매도 : 1, 매수 : 2
		('처리구분', 'U1'),  # (F:08) 합산 : 0, 건별 : 1
		('종목구분코드', 'U1'),  # (F:09) 전체 : 0, ELW제외 : 1, ELW : 2
		('조회구분코드', 'U1'),  # (F:10) 0: 내림차순(default), 1: 오름차순
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('거래구분', 'U40'),  # (F:01) 
		('종목코드', 'U12'),  # (F:02) 
		('종목명', 'U50'),  # (F:03) 
		('수량', 'U20'),  # (F:04) 
		('단가', 'U20'),  # (F:05) 
		('수수료', 'U20'),  # (F:06) 
		('제세금', 'U20'),  # (F:07) 
		('거래금액', 'U20'),  # (F:08) 
		('신용금액', 'U20'),  # (F:09) 
		('미수변제', 'U20'),  # (F:10) 
		('연체료', 'U20'),  # (F:11) 
		('신용이자', 'U20'),  # (F:12) 
		('변동금액', 'U20'),  # (F:13) 
		('최종금액', 'U20'),  # (F:14) 
		('주문매체명', 'U50'),  # (F:15) 
		])


class SABA251U1(BaseTR):
	NAME, DESCRIPTION = 'SABA251U1', '현물/ELW 예약주문'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('계좌상품', 'U2'),  # (F:01) 항상 ‘01’
		('계좌비밀번호', 'U9'),  # (F:02) 
		('시장거래구분', 'U1'),  # (F:03) 생략
		('선물대용매도여부', 'U1'),  # (F:04) 0:일반  		1:선물대용
		('신용거래구분', 'U2'),  # (F:05) 00:보통              	01:유통융자매수 03:자기융자매수      	05:유통대주매도 07:자기대주매도     	11:유통융자매도상환 12:유통융자현금상환 	33:자기융자매도상환 34:자기융자현금상환 	55:유통대주매수상환 56:유통대주현물상환 	77:자기대주매수상환 78:자기대주현물상환 	91:예탁담보대출 92:예탁담보매도상환 	93:예탁담보현금상환 96:주식청약대출     	97:주식청약상환
		('매도/매수 구분', 'U1'),  # (F:06) 1:매도  		2:매수   3:정정  		4:취소
		('종목코드', 'U12'),  # (F:07) 현물: 단축코드(A포함)  (예:A005930) ELW: 단축코드 (J포함)  (예:J505236) ETN: 단축코드 (Q포함)  (예:Q500001)
		('주문수량', 'U10'),  # (F:08) 주문가능구분코드 1, 2 설정시 미입력
		('주문가격', 'U20'),  # (F:09) 예약주문가격구분코드 1, 2설정시 미입력
		('신용대출일', 'U8'),  # (F:10) 
		('정규시간외구분코드', 'U1'),  # (F:11) 1:정규장               2:장개시전시간외 3:장종료후시간외종가   4:장종료후시간외단일가 5:경매매
		('호가유형코드', 'U1'),  # (F:12) 1:시장가    2:지정가    I:조건부지정가       X:최유리    Y:최우선    Z.변동없음(정정주문시)
		('예약순번', 'U18'),  # (F:13) 정정/취소시 사용할 원 예약순번
		('예약주문구분코드', 'U1'),  # (F:14) “2”
		('전화번호', 'U20'),  # (F:15) 생략
		('예약주문가격구분코드', 'U1'),  # (F:16) 지정가:0, 익일상한가:1, 익일하한가:2
		('주문가능구분코드', 'U1'),  # (F:17) 일반:0 , 최대:1, 현금100%:2
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('주문번호', 'U18'),  # (F:00) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABA292Q1(BaseTR):
	NAME, DESCRIPTION = 'SABA292Q1', '예약주문내역'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U4'),  # (F:01) 
		('시장구분', 'U1'),  # (F:02) “0”
		('처리일자', 'U8'),  # (F:03) 
		('구분', 'U1'),  # (F:04) 전체:0, 매도:1, 매수:2
		('조회구분', 'U1'),  # (F:05) 0: 당일조회, 1: 기간조회
		('조회시작일', 'U8'),  # (F:06) YYYYMMDD
		('조회종료일', 'U8'),  # (F:07) YYYYMMDD
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('예약번호', 'U18'),  # (F:00) 
		('주문구분명', 'U40'),  # (F:01) 
		('정규시간외구분코드', 'U1'),  # (F:02) 
		('정규시간외구분명', 'U30'),  # (F:03) 
		('호가유형코드', 'U1'),  # (F:04) 
		('호가유형명', 'U30'),  # (F:05) 
		('매체구분', 'U2'),  # (F:06) 
		('단축코드', 'U12'),  # (F:07) 
		('종목명', 'U50'),  # (F:08) 
		('주문수량', 'U18'),  # (F:09) 
		('주문단가', 'U20'),  # (F:10) 
		('예약시간', 'U9'),  # (F:11) 
		('대출일', 'U8'),  # (F:12) 
		('주문번호', 'U18'),  # (F:13) 
		('상품구분', 'U2'),  # (F:14) 
		('취소여부', 'U1'),  # (F:15) 
		('취소여부명', 'U30'),  # (F:16) 
		('예약일자', 'U8'),  # (F:17) 
		('주문일', 'U8'),  # (F:18) 
		('수량구분', 'U1'),  # (F:19) 
		('수량구분명', 'U30'),  # (F:20) 
		('단가구분', 'U1'),  # (F:21) 
		('단가구분명', 'U30'),  # (F:22) 
		('에러메세지', 'U100'),  # (F:23) 
		('주문자', 'U12'),  # (F:24) 
		('매도매수구분코드', 'U1'),  # (F:25) 
		('매매구분명', 'U30'),  # (F:26) 
		('예약주문종류코드', 'U1'),  # (F:27) 
		('주문시작일', 'U8'),  # (F:28) 
		('주문종료일', 'U8'),  # (F:29) 
		('주문일2', 'U8'),  # (F:30) 
		('기간예약순번', 'U18'),  # (F:31) 
		('주문건수', 'U18'),  # (F:32) 
		])


class SABA415Q1(BaseTR):
	NAME, DESCRIPTION = 'SABA415Q1', '비율별 주문가능 수량 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('상품구분', 'U2'),  # (F:01) 항상 ‘01’
		('비밀번호', 'U4'),  # (F:02) 
		('종목코드', 'U12'),  # (F:03) ‘A’+  단축코드 (A005930)
		('정규시간외구분코드', 'U1'),  # (F:04) 1:정규장               2:장개시전시간외 3:장종료후시간외종가   4:장종료후시간외단일가 5:장종료후시간외대량
		('호가유형 코드', 'U1'),  # (F:05) 1:시장가    2:지정가    I:조건부지정가       X:최유리    Y:최우선    Z.변동없음(정정주문시)
		('대량매매 구분코드', 'U1'),  # (F:06) ‘0’
		('신용구분', 'U2'),  # (F:07) 00:보통              	01:유통융자매수 03:자기융자매수      	05:유통대주매도 07:자기대주매도     	11:유통융자매도상환 12:유통융자현금상환 	33:자기융자매도상환 34:자기융자현금상환 	55:유통대주매수상환 56:유통대주현물상환 	77:자기대주매수상환 78:자기대주현물상환 	91:예탁담보대출 92:예탁담보매도상환 	93:예탁담보현금상환 96:주식청약대출     	97:주식청약상환
		('단가', 'U20'),  # (F:08) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('비율', 'U18'),  # (F:00) 
		('주문가능수량', 'U18'),  # (F:01) 
		('최대주문가능수량', 'U18'),  # (F:02) 
		('미수예정금액', 'U20'),  # (F:03) 
		('주문가능금액', 'U20'),  # (F:04) 
		('최대주문가능금액', 'U20'),  # (F:05) 
		('융자금', 'U20'),  # (F:06) 
		('최대융자금액', 'U20'),  # (F:07) 
		])


class SABA609Q1(BaseTR):
	NAME, DESCRIPTION = 'SABA609Q1', '현물 잔고 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('상품구분', 'U2'),  # (F:01) 항상 ‘01’
		('비밀번호', 'U4'),  # (F:02) 
		('구분1', 'U1'),  # (F:03) 1:매매기준		2:결제기준 3:신용잔고
		('단가구분', 'U1'),  # (F:04) 1:평균단가		2:제비용단가 3.매수비용단가		4:매도비용단가
		('종목구분코드', 'U1'),  # (F:05) 0:전체, 1:ELW제외, 2:ELW만
		('작업구분', 'U1'),  # (F:06) 0:전체 Output, 1:Multi Data제외 2:Multi Data만
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('일자', 'U2'),  # (F:00) 
		('요일(D)', 'U2'),  # (F:01) 
		('예수금(D)', 'U20'),  # (F:02) 
		('일자(D+1)', 'U2'),  # (F:03) 
		('요일(D+1)', 'U2'),  # (F:04) 
		('예수금(D+1)', 'U20'),  # (F:05) 
		('일자(D+2)', 'U2'),  # (F:06) 
		('요일(D+2)', 'U2'),  # (F:07) 
		('예수금(D+2)', 'U20'),  # (F:08) 
		('인출가능금액(D)', 'U20'),  # (F:09) 
		('신용금액(융자)', 'U20'),  # (F:10) 
		('대출금액', 'U20'),  # (F:11) 
		('현금매수', 'U20'),  # (F:12) 
		('최대(미수)', 'U20'),  # (F:13) 
		('신용매수', 'U20'),  # (F:14) 
		('주식매입금액', 'U20'),  # (F:15) 
		('실현손익', 'U20'),  # (F:16) 
		('채권평가금', 'U20'),  # (F:17) 
		('주식평가금액', 'U20'),  # (F:18) 
		('미실현손익', 'U20'),  # (F:19) 
		('현금증거금', 'U20'),  # (F:20) 
		('위탁순자산평가', 'U20'),  # (F:21) 
		('미실현손익률', 'U20'),  # (F:22) 9(07).99
		('익일반대매매', 'U20'),  # (F:23) 
		('총계약금액', 'U20'),  # (F:24) 
		('납입금액', 'U20'),  # (F:25) 
		('납입횟수', 'U18'),  # (F:26) 
		('채권매입금액', 'U20'),  # (F:27) 
		('상품순자산평가', 'U20'),  # (F:28) 
		('채권손익률', 'U20'),  # (F:29) 9(07).99
		])
	MULTI_OUTPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),  # (F:00) 
		('종목명', 'U50'),  # (F:01) 
		('구분코드', 'U1'),  # (F:02) 
		('구분', 'U10'),  # (F:03) 
		('잔고수량', 'U18'),  # (F:04) 
		('전일매도미결제', 'U18'),  # (F:05) 
		('당일매도미결제', 'U18'),  # (F:06) 
		('전일매수미결제', 'U18'),  # (F:07) 
		('당일매수미결제', 'U18'),  # (F:08) 
		('결제일수량', 'U18'),  # (F:09) 
		('주문가능수량', 'U18'),  # (F:10) 
		('미체결수량', 'U18'),  # (F:11) 
		('평균단가', 'U20'),  # (F:12) 
		('현재가', 'U20'),  # (F:13) 
		('전일대비', 'U20'),  # (F:14) 
		('비율', 'U20'),  # (F:15) 9(07).99
		('매도호가', 'U20'),  # (F:16) 
		('매수호가', 'U20'),  # (F:17) 
		('평가금액', 'U20'),  # (F:18) 
		('미실현손익금액', 'U20'),  # (F:19) 
		('손익률', 'U20'),  # (F:20) 
		('보유비중', 'U20'),  # (F:21) 9(07).99
		('융자금액', 'U20'),  # (F:22) 
		('자기금액', 'U20'),  # (F:23) 
		('대출일', 'U8'),  # (F:24) YYYYMMDD
		('만기일', 'U8'),  # (F:25) YYYYMMDD
		('신용이자', 'U20'),  # (F:26) 
		('매수일자(채권)', 'U8'),  # (F:27) YYYYMMDD
		('단축코드', 'U12'),  # (F:28) 
		('전일종가', 'U20'),  # (F:29) 
		])

	def _set_input_data(self, 계좌번호, 비밀번호, 구분1='1', 단가구분='2', 종목구분='0', 작업구분='0') -> None:
		#INPUT_DTYPE = np.dtype([
		# ('계좌번호', 'U11'),  # (F:00) 
		# ('상품구분', 'U2'),  # (F:01) 항상 ‘01’
		# ('비밀번호', 'U4'),  # (F:02) 
		# ('구분1', 'U1'),  # (F:03) 1:매매기준		2:결제기준 3:신용잔고
		# ('단가구분', 'U1'),  # (F:04) 1:평균단가		2:제비용단가 3.매수비용단가		4:매도비용단가
		# ('종목구분코드', 'U1'),  # (F:05) 0:전체, 1:ELW제외, 2:ELW만
		# ('작업구분', 'U1'),  # (F:06) 0:전체 Output, 1:Multi Data제외 2:Multi Data만
		# ])
		inst = self._indi_instance
		inst.dynamicCall("SetSingleData(int, QString)", 0, str(계좌번호))
		inst.dynamicCall("SetSingleData(int, QString)", 1, '01')  # 상품구분
		inst.dynamicCall("SetSingleData(int, QString)", 2, 비밀번호)
		inst.dynamicCall("SetSingleData(int, QString)", 3, 구분1)
		inst.dynamicCall("SetSingleData(int, QString)", 4, 단가구분)
		inst.dynamicCall("SetSingleData(int, QString)", 5, 종목구분)
		inst.dynamicCall("SetSingleData(int, QString)", 6, 작업구분)
		

# class SABA623Q1(BaseTR):
# 	NAME, DESCRIPTION = 'SABA623Q1', '전일대비 잔고증감 현황'
# 	INPUT_DTYPE = np.dtype([
# 		('계좌번호', 'U11'),  # (F:00) 
# 		('상품구분', 'U2'),  # (F:01) 항상 ‘01’
# 		('비밀번호', 'U4'),  # (F:02) 
# 		])
# 	REALTIME_AVAILABLE = False
# 	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
# 	SINGLE_OUTPUT_DTYPE = np.dtype([
# 		('금일', 'U?'),
# 		('금일요일', 'U?'),
# 		('전일', 'U?'),
# 		('전일요일', 'U?'),
# 		('전일예수금', 'U?'),
# 		('당일예수금', 'U?'),
# 		('전일대비예수금', 'U?'),
# 		('전일평가금액', 'U?'),
# 		('당일평가금액', 'U?'),
# 		('전일신용금액', 'U?'),
# 		('금일신용금액', 'U?'),
# 		('전일대비평가금액', 'U?'),
# 		('전일대비수익육', 'U?')
# 		])
# 	MULTI_OUTPUT_DTYPE = np.dtype([
# 		('종목명', 'U?'), 
# 		('결제잔고', 'U?'), 
# 		('전일체결', 'U?'), 
# 		('당일체결', 'U?'), 
# 		('당일잔고', 'U?'), 
# 		('전일종가', 'U?'), 
# 		('현재가', 'U?'), 
# 		('전일평가', 'U?'), 
# 		('금일평가', 'U?'), 
# 		('당일손익', 'U?'), 
# 		('당일수익율', 'U?'), 
# 		('신용금액', 'U?'), 
# 		('대출일', 'U?')
# 		])


class SABA655Q1(BaseTR):
	NAME, DESCRIPTION = 'SABA655Q1', '총자산 계좌잔고 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('상품구분', 'U2'),  # (F:01) 01: 종합계좌    10:코스피선물옵션 11: 코스닥선물옵션    21:증권저축잔고
		('비밀번호', 'U4'),  # (F:02)  
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('순자산 평가금액', 'U20'),  # (F:00) 
		('총자산 평가금액', 'U20'),  # (F:01) 
		('대출/미납금 합계', 'U20'),  # (F:02) 
		('주식 평가금액', 'U20'),  # (F:03) 
		('KOSPI선물옵션평가금액', 'U20'),  # (F:04) 
		('채권 평가금액', 'U20'),  # (F:05) 
		('RP 평가금액', 'U20'),  # (F:06) 
		('수익증권 평가금액', 'U20'),  # (F:07) 
		('미수 확보금', 'U20'),  # (F:08) 
		('국내뮤츄얼 평가금액', 'U20'),  # (F:09) 
		('해외뮤추얼 평가금액', 'U20'),  # (F:10) 
		('CD 평가금액', 'U20'),  # (F:11) 
		('CP 평가금액', 'U20'),  # (F:12) 
		('외화자산 평가금액', 'U20'),  # (F:13) 
		('권리 대용금', 'U20'),  # (F:14) 
		('상품청약금액', 'U20'),  # (F:15) 
		('신용설정보증금', 'U20'),  # (F:16) 
		('예수금합계', 'U20'),  # (F:17) 
		('현금증거금합계', 'U20'),  # (F:18) 
		('인출가능금액합계', 'U20'),  # (F:19) 
		('미수금', 'U20'),  # (F:20) 
		('신용 융자금', 'U20'),  # (F:21) 
		('미상환 융자금', 'U20'),  # (F:22) 
		('예탁담보대출금액', 'U20'),  # (F:23) 
		('청약담보대출금액', 'U20'),  # (F:24) 
		('수표입금액', 'U20'),  # (F:25) 
		('이자미납금', 'U20'),  # (F:26) 
		('대주담보금', 'U20'),  # (F:27) 
		('기타수표입금액', 'U20'),  # (F:28) 
		('담보부족금액', 'U20'),  # (F:29) 
		('현재담보비율', 'U20'),  # (F:30) 
		('최소유지비율', 'U20'),  # (F:31) 
		('ELS평가금액', 'U20'),  # (F:32) 
		('WARRANT평가금액', 'U20'),  # (F:33) 
		('대주담보금액', 'U20'),  # (F:34) 
		('매입자금대출금액', 'U20'),  # (F:35) 
		('은행마이너스대출', 'U20'),  # (F:36) 
		('반대매매일자', 'U8'),  # (F:37) 
		('CMA평가금액', 'U20'),  # (F:38) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABA835Q1(BaseTR):
	NAME, DESCRIPTION = 'SABA835Q1', '현물상품 예수금 및 잔고현황 조회'
	INPUT_DTYPE = None
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('총예수금O', 'U20'),  # (F:00) 
		('주문가능금액O', 'U20'),  # (F:01) 
		('출금가능금액O', 'U20'),  # (F:02) 
		('매입금액O', 'U20'),  # (F:03) 
		('평가금액O', 'U20'),  # (F:04) 
		('손익금액O', 'U20'),  # (F:05) 
		('총평가금액O', 'U20'),  # (F:06) 
		('수익율O', 'U20'),  # (F:07) 
		('총증거금O', 'U20'),  # (F:08) 
		('1차결제매수금액O', 'U20'),  # (F:09) 
		('1차결제매도금액O', 'U20'),  # (F:10) 
		('매수정산금액O', 'U20'),  # (F:11) 
		('매도정산금액O', 'U20'),  # (F:12) 
		('현물상품추정총예수금', 'U20'),  # (F:13) 
		])
	MULTI_OUTPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),  # (F:00) 
		('종목명', 'U50'),  # (F:01) 
		('신용구분코드', 'U20'),  # (F:02) 
		('잔고수량', 'U18'),  # (F:03) 
		('매도가능수량', 'U18'),  # (F:04) 
		('처분제한수량', 'U18'),  # (F:05) 
		('출고가능수량', 'U18'),  # (F:06) 
		('매입가', 'U20'),  # (F:07) 
		('현재가', 'U20'),  # (F:08) 
		('단가변동', 'U20'),  # (F:09) 
		('매입금액', 'U20'),  # (F:10) 
		('신용금액', 'U20'),  # (F:11) 
		('평가금액', 'U20'),  # (F:12) 
		('손익금액', 'U20'),  # (F:13) 
		('손익율', 'U20'),  # (F:14) 
		('매매단위수량', 'U18'),  # (F:15) 
		('유가증권구분코드', 'U1'),  # (F:16) 
		])


class SABA871U1(BaseTR):
	NAME, DESCRIPTION = 'SABA871U1', '금현물 주문'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('계좌상품코드', 'U2'),  # (F:01) 
		('계좌비밀번호', 'U9'),  # (F:02) 
		('계좌관리부점코드', 'U3'),  # (F:03) 
		('증권시장구분코드', 'U1'),  # (F:04) 
		('매도매수구분코드', 'U1'),  # (F:05) 
		('종목코드', 'U12'),  # (F:06) 
		('주문수량', 'U10'),  # (F:07) 
		('주문단가', 'U20'),  # (F:08) 
		('정규시간외구분코드', 'U1'),  # (F:09) 
		('호가유형코드', 'U1'),  # (F:10) 
		('주문조건구분코드', 'U1'),  # (F:11) 
		('원주문번호', 'U10'),  # (F:12) 
		('이상호가처리구분', 'U1'),  # (F:13) 
		('결과메시지처리여부', 'U1'),  # (F:14) 
		('채널주문번호', 'U20'),  # (F:15) 
		('FEP전송여부', 'U1'),  # (F:16) 
		('대량매매구분코드', 'U1'),  # (F:17) 
		('상대회원사번호', 'U5'),  # (F:18) 
		('상대거래소계좌번호', 'U12'),  # (F:19) 
		('협의상세시각', np.uint32),  # (F:20) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('주문번호', 'U10'),  # (F:00) 
		('채널주문번호Out', 'U20'),  # (F:01) 
		('메시지구분', 'U20'),  # (F:02) 
		('메시지1', 'U1'),  # (F:03) 
		('메시지2', 'U35'),  # (F:04) 
		('메시지3', 'U35'),  # (F:05) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABA941Q1(BaseTR):
	NAME, DESCRIPTION = 'SABA941Q1', '그룹별 증거금율'
	INPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),  # (F:00) 
		('종목그룹', 'U1'),  # (F:01) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('종목코드O', 'U12'),  # (F:00) 
		('종목명', 'U50'),  # (F:01) 
		('현금증거금율', 'U20'),  # (F:02) 
		('대용증거금율', 'U20'),  # (F:03) 
		('재사용증거금율', 'U20'),  # (F:04) 
		('종목그룹O', 'U1'),  # (F:05) 
		('신용제한범위구분', 'U20'),  # (F:06) 
		('외국인한도종목', 'U4'),  # (F:07) 
		('기타구분', 'U11'),  # (F:08) 
		('시장소속구분', 'U1'),  # (F:09) 
		('신용종목그룹코드', 'U1'),  # (F:10) 
		('신용현금증거금율', 'U20'),  # (F:11) 
		('신용대용증거금율', 'U20'),  # (F:12) 
		('신용총증거금율', 'U20'),  # (F:13) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABB446Q1(BaseTR):
	NAME, DESCRIPTION = 'SABB446Q1', '계좌별 기간별 주문체결'
	INPUT_DTYPE = np.dtype([
		('매매시작일자', 'U8'),  #	
		('매매종료일자', 'U8'),  #	
		('계좌번호', 'U11'),  #	
		('비밀번호', 'U4'),  #	
		('체결구분', 'U1'),  #	0:전체, 1:체결, 2:미체결
		('국가', 'U1'),  #	0:전체, 1:중국, 2:미국
		('거래소', 'U2'),  #	*:전체
		('In_GIC코드', 'U15'),  #	*:전체
		('체결건별구분', 'U1'),  #	0:합산, 1:건별
		('매도매수구분', 'U1'),  #	*:전체, 1:매도. 2:매수
		('계좌상품코드', 'U2')  #	
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('매도금액', 'U20'), 
		('매수금액', 'U20'), 
		('수수료_1', 'U20')
	])
	MULTI_OUTPUT_DTYPE = np.dtype([
		('매매구분', 'U1'), 
		('구분', 'U1'), 
		('ISIN코드', 'U12'), 
		('Out_GIC코드', 'U15'), 
		('단축코드', 'U12'), 
		('종목명', 'U50'), 
		('주문수량', 'U20'), 
		('주문단가', 'U20'), 
		('체결수량', 'U20'), 
		('체결단가', 'U20'), 
		('미체결수량', 'U20'), 
		('상태', 'U20'), 
		('거래금액', 'U20'), 
		('원화거래금액', 'U20'), 
		('수수료_2', 'U20'), 
		('주문번호', 'U18'), 
		('원주문번호', 'U18'), 
		('일자(국내)', 'U8'), 
		('주문시간', 'U14'), 
		('주문시간(현지)', 'U14'), 
		('체결시간', 'U14'), 
		('체결시간(현지)','U6'), 
		('국가구분', 'U40'), 
		('시장구분', 'U20'), 
		('통화', 'U3'), 
		('주문자', 'U30'), 
		('FIX거부사유내용', 'U100'), 
		('주문유형명', 'U40'), 
		('환율', 'U20'), 
		('매도매수구분명', 'U10'), 
		('신용거래구분코드', 'U2'), 
		('신용대출일자', 'U8')
		])


class SABC100U1(BaseTR):
	NAME, DESCRIPTION = 'SABC100U1', '선물/옵션 일반 주문(매도/매수/정정/취소)'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U4'),  # (F:01) 
		('종목코드', 'U12'),  # (F:02) 
		('주문수량', 'U10'),  # (F:03) 
		('주문단가', 'U13'),  # (F:04) 소수점 2자리(양수:999.99  음수:-999.99) RFR 종목 : 소수점 3자리(RFR이외종목은 3자리 절사)
		('주문조건', 'U1'),  # (F:05) 0:일반(FAS)     3:IOC(FAK)     4:FOK
		('매매구분', 'U2'),  # (F:06) 01:매도  		02:매수 (정정/취소시): 01
		('호가유형', 'U1'),  # (F:07) L:지정가  		M:시장가   C:조건부		B:최유리
		('차익거래구분', 'U1'),  # (F:08) 1:차익  		2:헷지   3:기타
		('처리구분', 'U1'),  # (F:09) 1:신규 			2:정정  3:취소
		('정정취소수량구분', 'U1'),  # (F:10) 0:신규 		1:전부       2:일부
		('원주문번호', 'U10'),  # (F:11) (매수/매도시 생략가능)
		('예약주문여부', 'U1'),  # (F:12) (생략가능) 1:예약
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('주문번호', 'U10'),  # (F:00) 
		('ORC주문번호', 'U20'),  # (F:01) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABC101U8(BaseTR):
	NAME, DESCRIPTION = 'SABC101U8', '롤오버 주문'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U4'),  # (F:01) 
		('종목코드', 'U12'),  # (F:02) 
		('주문수량', 'U10'),  # (F:03) 
		('주문단가', 'U13'),  # (F:04) 
		('주문조건구분코드', 'U1'),  # (F:05) 
		('선물옵션매매구분코드', 'U2'),  # (F:06) 01 : 매도, 02 : 매수
		('선물옵션호가유형코드', 'U1'),  # (F:07) L : 지정가, M : 시장가, C : 조건부, B:최유리
		('차익거래구분코드', 'U1'),  # (F:08) 1 : 차익거래, 2 : 헷지거래, 3 : 기타
		('처리구분', 'U1'),  # (F:09) 1 : 신규, 2 : 정정, 3 : 취소
		('일부전체구분코드 순번', 'U1'),  # (F:10) Y:Yes, N : No
		('원주문번호', 'U10'),  # (F:11) 
		('예약주문여부', 'U1'),  # (F:12) Y:Yes, N : No
		('주문착오확인여부', 'U1'),  # (F:13) 
		('선물옵션그룹코드', 'U10'),  # (F:14) 
		('MTS주문번호', 'U10'),  # (F:15) 
		('운용사지시번호', 'U12'),  # (F:16) 
		('채널주문번호', 'U20'),  # (F:17) 
		('예비필드', 'U20'),  # (F:18) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('주문번호', 'U10'),  # (F:00) 
		('FIX주문번호', 'U20'),  # (F:01) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABC104Q1(BaseTR):
	NAME, DESCRIPTION = 'SABC104Q1 ( bc414q_Q )', '선물주문가능계약수'
	INPUT_DTYPE = np.dtype([
		('종합계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U4'),  # (F:01) 
		('종목코드', 'U12'),  # (F:02) 
		('주문단가', 'U20'),  # (F:03) 
		('주문유형', 'U1'),  # (F:04) L:지정가  		M:시장가   C:조건부		B:최유리
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('예수금현황', 'U20'),  # (F:00) 
		('미수금', 'U20'),  # (F:01) 
		('대용금액', 'U20'),  # (F:02) 
		('예탁총액', 'U20'),  # (F:03) 
		('위탁증거금총액', 'U20'),  # (F:04) 
		('위탁증거금현금', 'U20'),  # (F:05) 
		('주문가능현금', 'U20'),  # (F:06) 
		('주문가능총액', 'U20'),  # (F:07) 
		('종목코드', 'U12'),  # (F:08) 
		('현재가', 'U20'),  # (F:09) 
		('시간', 'U6'),  # (F:10) 
		('청산가능매도수량', 'U18'),  # (F:11) 
		('청산가능매수수량', 'U18'),  # (F:12) 
		('신규주문가능매도수량', 'U18'),  # (F:13) 
		('신규주문가능매수수량', 'U18'),  # (F:14) 
		('총주문가능매도수량', 'U18'),  # (F:15) 
		('총주문가능매수수량', 'U18'),  # (F:16) 
		('매수호가1', 'U20'),  # (F:17) 
		('매수가능수량1', 'U18'),  # (F:18) 
		('매수호가2', 'U20'),  # (F:19) 
		('매수가능수량2', 'U18'),  # (F:20) 
		('매수호가3', 'U20'),  # (F:21) 
		('매수가능수량3', 'U18'),  # (F:22) 
		('매수호가4', 'U20'),  # (F:23) 
		('매수가능수량4', 'U18'),  # (F:24) 
		('매수호가5', 'U20'),  # (F:25) 
		('매수가능수량5', 'U18'),  # (F:26) 
		('매도호가1', 'U20'),  # (F:27) 
		('매도가능수량1', 'U18'),  # (F:28) 
		('매도호가2', 'U20'),  # (F:29) 
		('매도가능수량2', 'U18'),  # (F:30) 
		('매도호가3', 'U20'),  # (F:31) 
		('매도가능수량3', 'U18'),  # (F:32) 
		('매도호가4', 'U20'),  # (F:33) 
		('매도가능수량4', 'U18'),  # (F:34) 
		('매도호가5', 'U20'),  # (F:35) 
		('매도가능수량5', 'U18'),  # (F:36) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABC105U1(BaseTR):
	NAME, DESCRIPTION = 'SABC105U1', '유렉스 일반 주문(매도/매수/정정/취소)'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U4'),  # (F:01) 
		('종목코드', 'U12'),  # (F:02) E를 제외한 종목코드(Ex – 101S9)
		('주문수량', 'U10'),  # (F:03) 
		('주문단가', 'U13'),  # (F:04) 소수점 2자리(양수:999.99  음수:-999.99)
		('주문조건', 'U1'),  # (F:05) 0:일반(FAS)     3:IOC(FAK)     4:FOK
		('매매구분', 'U2'),  # (F:06) 01:매도  		02:매수 (정정/취소시): 01
		('호가유형', 'U1'),  # (F:07) L:지정가  		M:시장가   C:조건부		B:최유리
		('처리구분', 'U1'),  # (F:08) 1:신규 			2:정정  3:취소
		('원주문번호', 'U10'),  # (F:09) (매수/매도시 생략가능)
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('주문번호', 'U10'),  # (F:00) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABC160U3(BaseTR):
	NAME, DESCRIPTION = 'SABC160U3', '야간선옵_통합주문'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('계좌비밀번호', 'U9'),  # (F:01) 
		('종목코드', 'U12'),  # (F:02) 
		('주문수량', 'U10'),  # (F:03) 
		('주문단가', 'U13'),  # (F:04) 
		('주문조건구분코드', 'U1'),  # (F:05) 0 : 일반(FAS) / 3 IOC(FAK) / 4 FOK
		('선물옵션매매구분코드', 'U2'),  # (F:06) 01 : 매도 / 02 : 매수 / 03 : 청산매도 / 04 : 청산매수 / 05 : 만기매도 / 06 : 만기매수 / 09 : 만기매도(인수도) / 10 : 만기매수(인수도)
		('선물옵션호가유형코드', 'U1'),  # (F:07) B: 최유리지정가 / C 조건부지정가 / L 지정가 / M 시장가
		('차익거래구분코드', 'U1'),  # (F:08) 1: 차익거래 / 2: 헤지거래 / 3: 기타 / 4: 사후위탁증거금 차익 / 5 : 사후위탁증거금 해지 / 6: 사후위탁기타 / 7: 사후증거금 차익 / 8 : 사후할인증거금 해지 / 9: 사후할인 기타/ A 옵션매수전용계좌
		('처리구분', 'U1'),  # (F:09) 0 : 신규 / 1 : 정정 / 2 : 취소
		('일부전체구분코드', 'U1'),  # (F:10) 1: 전체 / 2: 일부(취소나 정정시 사용)
		('원주문번호', 'U10'),  # (F:11) 
		('예약주문여부', 'U1'),  # (F:12) 
		('주문착오확인여부', 'U1'),  # (F:13) 
		('선물옵션그룹코드', 'U10'),  # (F:14) 
		('MTS주문번호', 'U10'),  # (F:15) 
		('운용사지시번호', 'U12'),  # (F:16) 
		('채널주문번호', 'U20'),  # (F:17) 
		('예비필드', 'U20'),  # (F:18) 
		('희망체결기준여부', 'U1'),  # (F:19) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('주문번호', 'U10'),  # (F:00) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABC203Q2(BaseTR):
	NAME, DESCRIPTION = 'SABC203Q2', '선물옵션 매매내역 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) Ex>00111123456
		('비밀번호', 'U4'),  # (F:01) 
		('매매구분', 'U2'),  # (F:02) %: 전체
		('종목코드', 'U12'),  # (F:03) %: 전체
		('시장 ID코드', 'U3'),  # (F:04) “000”
		('옵션구분코드', 'U1'),  # (F:05) %: 전체 , 1: 선물, 콜 : 2, 풋 : 3
		('조회시작일', 'U8'),  # (F:06) 
		('조회종료일', 'U8'),  # (F:07) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('주문일자', 'U8'),  # (F:00) 
		('종목코드', 'U12'),  # (F:01) 
		('선물옵션 매매구분명', 'U30'),  # (F:02) 
		('체결수량', 'U18'),  # (F:03) 
		('체결단가', 'U20'),  # (F:04) 
		('체결금액', 'U20'),  # (F:05) 
		('매매손익금액', 'U20'),  # (F:06) 
		('수수료', 'U20'),  # (F:07) 
		('매체구분명', 'U20'),  # (F:08) 
		('선물옵션호가유형명', 'U20'),  # (F:09) 
		('계좌번호', 'U11'),  # (F:10) 
		('계좌명', 'U50'),  # (F:11) 
		('등록구분코드', 'U1'),  # (F:12) 
		('주문조건구분명', 'U20'),  # (F:13) 
		('자동취소수량', 'U18'),  # (F:14) 
		])


class SABC207Q5(BaseTR):
	NAME, DESCRIPTION = 'SABC207Q5', '증거금산출용 이론가격'
	INPUT_DTYPE = np.dtype([
		('조회일자', 'U8'),  # (F:00) 
		('구분', 'U1'),  # (F:01) 1: 위탁증거금, 2: 유지증거금
		('종목코드', 'U12'),  # (F:02) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),  # (F:00) 
		('선물옵션기준가문자', 'U20'),  # (F:01) 
		('이론가문자', 'U20'),  # (F:02) 
		('구간이론가1', 'U20'),  # (F:03) 
		('구간이론가2', 'U20'),  # (F:04) 
		('구간이론가3', 'U20'),  # (F:05) 
		('구간이론가4', 'U20'),  # (F:06) 
		('구간이론가5', 'U20'),  # (F:07) 
		('구간이론가6', 'U20'),  # (F:08) 
		('구간이론가7', 'U20'),  # (F:09) 
		('구간이론가8', 'U20'),  # (F:10) 
		('구간이론가9', 'U20'),  # (F:11) 
		('구간이론가10', 'U20'),  # (F:12) 
		('구간이론가11', 'U20'),  # (F:13) 
		('구간이론가12', 'U20'),  # (F:14) 
		('구간이론가13', 'U20'),  # (F:15) 
		('구간이론가14', 'U20'),  # (F:16) 
		('구간이론가15', 'U20'),  # (F:17) 
		('구간이론가16', 'U20'),  # (F:18) 
		('구간이론가17', 'U20'),  # (F:19) 
		('구간이론가18', 'U20'),  # (F:20) 
		('구간이론가19', 'U20'),  # (F:21) 
		('구간이론가20', 'U20'),  # (F:22) 
		('구간이론가21', 'U20'),  # (F:23) 
		('구간이론가22', 'U20'),  # (F:24) 
		('구간이론가23', 'U20'),  # (F:25) 
		('구간이론가24', 'U20'),  # (F:26) 
		('구간이론가25', 'U20'),  # (F:27) 
		('구간이론가26', 'U20'),  # (F:28) 
		('구간이론가27', 'U20'),  # (F:29) 
		('구간이론가28', 'U20'),  # (F:30) 
		('구간이론가29', 'U20'),  # (F:31) 
		('구간이론가30', 'U20'),  # (F:32) 
		('구간이론가31', 'U20'),  # (F:33) 
		('구간이론가32', 'U20'),  # (F:34) 
		('구간이론가33', 'U20'),  # (F:35) 
		('구간이론가34', 'U20'),  # (F:36) 
		('구간이론가35', 'U20'),  # (F:37) 
		('구간이론가36', 'U20'),  # (F:38) 
		('구간이론가37', 'U20'),  # (F:39) 
		('구간이론가38', 'U20'),  # (F:40) 
		('구간이론가39', 'U20'),  # (F:41) 
		('구간이론가40', 'U20'),  # (F:42) 
		('구간이론가41', 'U20'),  # (F:43) 
		('구간이론가42', 'U20'),  # (F:44) 
		('구간이론가43', 'U20'),  # (F:45) 
		('구간이론가44', 'U20'),  # (F:46) 
		('구간이론가45', 'U20'),  # (F:47) 
		('구간이론가46', 'U20'),  # (F:48) 
		('구간이론가47', 'U20'),  # (F:49) 
		('구간이론가48', 'U20'),  # (F:50) 
		('구간이론가49', 'U20'),  # (F:51) 
		('구간이론가50', 'U20'),  # (F:52) 
		('구간이론가51', 'U20'),  # (F:53) 
		('구간이론가52', 'U20'),  # (F:54) 
		('구간이론가53', 'U20'),  # (F:55) 
		('구간이론가54', 'U20'),  # (F:56) 
		('구간이론가55', 'U20'),  # (F:57) 
		('구간이론가56', 'U20'),  # (F:58) 
		('구간이론가57', 'U20'),  # (F:59) 
		('구간이론가58', 'U20'),  # (F:60) 
		('구간이론가59', 'U20'),  # (F:61) 
		('구간이론가60', 'U20'),  # (F:62) 
		('구간이론가61', 'U20'),  # (F:63) 
		('구간이론가62', 'U20'),  # (F:64) 
		('구간손익금액1', 'U20'),  # (F:65) 
		('구간손익금액2', 'U20'),  # (F:66) 
		('구간손익금액3', 'U20'),  # (F:67) 
		('구간손익금액4', 'U20'),  # (F:68) 
		('구간손익금액5', 'U20'),  # (F:69) 
		('구간손익금액6', 'U20'),  # (F:70) 
		('구간손익금액7', 'U20'),  # (F:71) 
		('구간손익금액8', 'U20'),  # (F:72) 
		('구간손익금액9', 'U20'),  # (F:73) 
		('구간손익금액10', 'U20'),  # (F:74) 
		('구간손익금액11', 'U20'),  # (F:75) 
		('구간손익금액12', 'U20'),  # (F:76) 
		('구간손익금액13', 'U20'),  # (F:77) 
		('구간손익금액14', 'U20'),  # (F:78) 
		('구간손익금액15', 'U20'),  # (F:79) 
		('구간손익금액16', 'U20'),  # (F:80) 
		('구간손익금액17', 'U20'),  # (F:81) 
		('구간손익금액18', 'U20'),  # (F:82) 
		('구간손익금액19', 'U20'),  # (F:83) 
		('구간손익금액20', 'U20'),  # (F:84) 
		('구간손익금액21', 'U20'),  # (F:85) 
		('구간손익금액22', 'U20'),  # (F:86) 
		('구간손익금액23', 'U20'),  # (F:87) 
		('구간손익금액24', 'U20'),  # (F:88) 
		('구간손익금액25', 'U20'),  # (F:89) 
		('구간손익금액26', 'U20'),  # (F:90) 
		('구간손익금액27', 'U20'),  # (F:91) 
		('구간손익금액28', 'U20'),  # (F:92) 
		('구간손익금액29', 'U20'),  # (F:93) 
		('구간손익금액30', 'U20'),  # (F:94) 
		('구간손익금액31', 'U20'),  # (F:95) 
		('구간손익금액32', 'U20'),  # (F:96) 
		('구간손익금액33', 'U20'),  # (F:97) 
		('구간손익금액34', 'U20'),  # (F:98) 
		('구간손익금액35', 'U20'),  # (F:99) 
		('구간손익금액36', 'U20'),  # (F:100) 
		('구간손익금액37', 'U20'),  # (F:101) 
		('구간손익금액38', 'U20'),  # (F:102) 
		('구간손익금액39', 'U20'),  # (F:103) 
		('구간손익금액40', 'U20'),  # (F:104) 
		('구간손익금액41', 'U20'),  # (F:105) 
		('구간손익금액42', 'U20'),  # (F:106) 
		('구간손익금액43', 'U20'),  # (F:107) 
		('구간손익금액44', 'U20'),  # (F:108) 
		('구간손익금액45', 'U20'),  # (F:109) 
		('구간손익금액46', 'U20'),  # (F:110) 
		('구간손익금액47', 'U20'),  # (F:111) 
		('구간손익금액48', 'U20'),  # (F:112) 
		('구간손익금액49', 'U20'),  # (F:113) 
		('구간손익금액50', 'U20'),  # (F:114) 
		('구간손익금액51', 'U20'),  # (F:115) 
		('구간손익금액52', 'U20'),  # (F:116) 
		('구간손익금액53', 'U20'),  # (F:117) 
		('구간손익금액54', 'U20'),  # (F:118) 
		('구간손익금액55', 'U20'),  # (F:119) 
		('구간손익금액56', 'U20'),  # (F:120) 
		('구간손익금액57', 'U20'),  # (F:121) 
		('구간손익금액58', 'U20'),  # (F:122) 
		('구간손익금액59', 'U20'),  # (F:123) 
		('구간손익금액60', 'U20'),  # (F:124) 
		('구간손익금액61', 'U20'),  # (F:125) 
		('구간손익금액62', 'U20'),  # (F:126) 
		('하향조정옵션이론가문자', 'U20'),  # (F:127) 
		('상승조정옵션이론가문자', 'U20'),  # (F:128) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABC256Q1(BaseTR):
	NAME, DESCRIPTION = 'SABC256Q1(BC921q_q)', '옵션 매도증거금 조회'
	INPUT_DTYPE = np.dtype([
		('월물', 'U6'),  # (F:00) Ex>200902
		('수량구분', 'U1'),  # (F:01) 0:정상 1:오류 2:송신중 3:승인중
		('수량값', 'U20'),  # (F:02) Ex> 수량 : 1, 2 ..
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('당일 Kospi200', 'U20'),  # (F:00) 
		('전일 Kospi200', 'U20'),  # (F:01) 
		])
	MULTI_OUTPUT_DTYPE = np.dtype([
		('콜증감', 'U20'),  # (F:00) 
		('콜 익일 증거금', 'U20'),  # (F:01) 
		('콜 당일 증거금', 'U20'),  # (F:02) 
		('콜 현재가', 'U20'),  # (F:03) 
		('콜 기준가', 'U20'),  # (F:04) 
		('행사가', 'U38'),  # (F:05) 
		('풋 현재가', 'U20'),  # (F:06) 
		('풋 기준가', 'U20'),  # (F:07) 
		('풋 당일 증거금', 'U20'),  # (F:08) 
		('풋 익일 증거금', 'U20'),  # (F:09) 
		('풋 증감', 'U20'),  # (F:10) 
		])


class SABC257Q1(BaseTR):
	NAME, DESCRIPTION = 'SABC257Q1(BC922q_q)', '선물옵션 주문 위탁증거금'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) Ex>00111123456
		('비밀번호', 'U4'),  # (F:01) 
		('매매구분', 'U2'),  # (F:02) 01:매도  02:매수  03:청산매도  04:청산매수  05:만기매도       06:만기매수
		('종목코드', 'U12'),  # (F:03) 
		('주문수량', 'U18'),  # (F:04) Ex>1
		('주문단가', 'U11'),  # (F:05) Ex>7.58
		('호가유형', 'U1'),  # (F:06) 지정가(L), 시장가(M),  조건부지정가(C), 최유리지정가(B)
		('청산가능수량반영여부', 'U1'),  # (F:07) Y
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('청산가능수량', 'U18'),  # (F:00) 
		('주문 증거금 현금', 'U20'),  # (F:01) 
		('주문 증거금 총액', 'U20'),  # (F:02) 
		('주문가능 현금', 'U20'),  # (F:03) 
		('주문가능 총액', 'U20'),  # (F:04) 
		('부족증거금 현금', 'U20'),  # (F:05) 
		('부족증거금 총액', 'U20'),  # (F:06) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABC258Q1(BaseTR):
	NAME, DESCRIPTION = 'SABC258Q1 ( bc927q_1 )', '선물/옵션 체결/미체결 내역조회'
	INPUT_DTYPE = np.dtype([
		('종합계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U8'),  # (F:01) 
		('상품구분', 'U1'),  # (F:02) 0:전체 			1:선물  2:옵션(지수옵션+ 주식옵션) 3:주식옵션만
		('시장ID코드', 'U3'),  # (F:03) 생략 또는 “000”
		('매매일자', 'U8'),  # (F:04) YYYYMMDD
		('조회구분', 'U1'),  # (F:05) 0:전체 			1:체결  2:미체결
		('합산구분', 'U1'),  # (F:06) 0:합산 			1:건별
		('Sort구분', 'U1'),  # (F:07) 0:주문번호순 		1:주문번호역순
		('종목별합산구분', 'U1'),  # (F:08) 0:일반조회 		1:종목별합산조회
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('주문완료여부', 'U1'),  # (F:00) 1:주문완료 		2:주문거부
		('종목코드', 'U12'),  # (F:01) 
		('종목명', 'U50'),  # (F:02) 
		('매매구분', 'U2'),  # (F:03) 01:매도 		02:매수
		('매매구분명', 'U30'),  # (F:04) 
		('주문수량', 'U18'),  # (F:05) 
		('주문단가', 'U20'),  # (F:06) 
		('체결수량', 'U18'),  # (F:07) 
		('체결단가', 'U20'),  # (F:08) 
		('미체결수량', 'U18'),  # (F:09) 
		('현재가', 'U20'),  # (F:10) 
		('호가구분', 'U20'),  # (F:11) 지정가, 시장가, 최유리, 조건부, 지정가전환시, 지정가전환최
		('주문처리상태', 'U10'),  # (F:12) 
		('주문번호', 'U18'),  # (F:13) 
		('원주문번호', 'U18'),  # (F:14) 
		('거래소접수번호', 'U18'),  # (F:15) 
		('접수시간', 'U9'),  # (F:16) 
		('작업자사번', 'U12'),  # (F:17) 
		('체결시간', 'U9'),  # (F:18) 
		('차익헤지구분', 'U10'),  # (F:19) 
		('주문조건', 'U20'),  # (F:20) ‘N:일반’ ‘F:FOK’   ‘I:IOK’
		('자동취소수량', 'U18'),  # (F:21) 
		('기초자산', 'U30'),  # (F:22) 
		('채널구분', 'U30'),  # (F:23) 
		('선물옵션상세구분', 'U1'),  # (F:24) 1 : KOSPI200선물,     2 : KOSPI200옵션,  3 : STAR 선물,        4 : 주식옵션,  5 : 주식선물,         6 : 신3년국채선물,  7 : 통안증권선물,     8 : 신5년국채선물,  9 : 신10년국채선물,   A : 미국달러선물,  B : 미국달러옵션,     C : 엔선물,  D : 유로선물,         E : 금선물,  F : 돈육선물,         G : FLEX미국달러선물,  H : 미니금선물,       I : 유렉스 L : 미니코스피선물,   M : 미니코스피옵션 T : ETF선물           W : 코스피위클리옵션
		('거래승수', 'U20'),  # (F:25) 
		('체결금액', 'U20'),  # (F:26) 
		('선물시장구분', 'U1'),  # (F:27) C : CME, E : 유렉스
		])


class SABC281Q1(BaseTR):
	NAME, DESCRIPTION = 'SABC281Q1', '롤오버 잔고'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U4'),  # (F:01) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),  # (F:00) 
		('선물옵션종목한글명', 'U80'),  # (F:01) 
		('매매구분코드', 'U2'),  # (F:02) 
		('매매구분명', 'U30'),  # (F:03) 
		('잔고수량', 'U18'),  # (F:04) 
		('가능수량', 'U18'),  # (F:05) 
		])


class SABC636Q3(BaseTR):
	NAME, DESCRIPTION = 'SABC636Q3', '특정일 미결제약정 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U4'),  # (F:01) 
		('처리일자', 'U8'),  # (F:02) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),  # (F:00) 
		('매도매수구분명', 'U10'),  # (F:01) 
		('잔고수량', 'U18'),  # (F:02) 
		('단가', 'U20'),  # (F:03) 
		('현재가', 'U20'),  # (F:04) 
		('평가손익', 'U20'),  # (F:05) 
		])


class SABC670Q2(BaseTR):
	NAME, DESCRIPTION = 'SABC670Q2', '선물옵션 매매일 손익 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) Ex>00111123456
		('비밀번호', 'U4'),  # (F:01) 
		('조회시작일', 'U8'),  # (F:02) 
		('조회종료일', 'U8'),  # (F:03) 
		('구분코드', 'U1'),  # (F:04) 0:전체 1:선물 2:옵션
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('매매일자', 'U8'),  # (F:00) 
		('선물정산차금', 'U20'),  # (F:01) 
		('옵션매매손익', 'U20'),  # (F:02) 
		('Eurex결제차금', 'U20'),  # (F:03) 
		('총손익', 'U20'),  # (F:04) 
		('선물수수료', 'U20'),  # (F:05) 
		('옵션수수료', 'U20'),  # (F:06) 
		('유렉스수수료', 'U20'),  # (F:07) 
		('총수수료', 'U20'),  # (F:08) 
		('실현손익금액', 'U20'),  # (F:09) 
		('당일손익', 'U11'),  # (F:10) 
		('당일누적손익금액', 'U50'),  # (F:11) 
		('선물평가손익금액', 'U1'),  # (F:12) 
		('옵션평가손익금액', 'U20'),  # (F:13) 
		('옵션전일대비평가손익금액', 'U18'),  # (F:14) 
		])


class SABC820Q1(BaseTR):
	NAME, DESCRIPTION = 'SABC820Q1', '매체별 손익 조회'
	INPUT_DTYPE = np.dtype([
		('조회일자', 'U8'),  # (F:00) 
		('계좌번호', 'U11'),  # (F:01) 
		('비밀번호', 'U4'),  # (F:02) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),  # (F:00) 
		('매체구분코드', 'U2'),  # (F:01) 인디 : 4K, HTS : 4H
		('잔고매도매수구분코드', 'U1'),  # (F:02) 매도 : 1, 매수 : 2, 잔고무 : 0
		('잔고수량', 'U18'),  # (F:03) 
		('단가', 'U20'),  # (F:04) 
		('현재가', 'U20'),  # (F:05) 
		('평가손익금액', 'U20'),  # (F:06) 
		('매수평균단가', 'U20'),  # (F:07) 
		('매수수량', 'U18'),  # (F:08) 
		('매도평균단가', 'U20'),  # (F:09) 
		('매도수량', 'U18'),  # (F:10) 
		('매매손익금액', 'U20'),  # (F:11) 
		('총손익', 'U20'),  # (F:12) 
		])


class SABC952Q1(BaseTR):
	NAME, DESCRIPTION = 'SABC952Q1 ( bc923q_1 )', '선물/옵션 예수금 내역조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U4'),  # (F:01) 
		('거래일구분', 'U1'),  # (F:02) 1:전일		 2:당일  현재 당일만 가능함
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('예수금총액', 'U20'),  # (F:00) 
		('예수금현금', 'U20'),  # (F:01) 
		('위탁증거금총액', 'U20'),  # (F:02) 
		('위탁증거금현금', 'U20'),  # (F:03) 
		('주문가능총액', 'U20'),  # (F:04) 
		('주문가능현금', 'U20'),  # (F:05) 
		('인출가능총액', 'U20'),  # (F:06) 
		('인출가능현금', 'U20'),  # (F:07) 
		('추가증거금총액', 'U20'),  # (F:08) 
		('추가증거금현금', 'U20'),  # (F:09) 
		('대용증감액', 'U20'),  # (F:10) 
		('대용매도체결금액', 'U20'),  # (F:11) 
		('정산차금총액', 'U20'),  # (F:12) 
		('정산차금현금', 'U20'),  # (F:13) 
		('옵션결제대금총액', 'U20'),  # (F:14) 
		('미수금', 'U20'),  # (F:15) 
		('수수료총액', 'U20'),  # (F:16) 
		('과대미결제여부', 'U2'),  # (F:17) Y:과대미결제
		('정산기준금총액', 'U20'),  # (F:18) 
		('정산기준금현금', 'U20'),  # (F:19) 
		('옵션가정산', 'U20'),  # (F:20) 
		('청산시평가', 'U20'),  # (F:21) 
		('매매손익', 'U20'),  # (F:22) 
		('평가손익', 'U20'),  # (F:23) 
		('전일대비손익', 'U20'),  # (F:24) 
		('선물매매손익', 'U20'),  # (F:25) 
		('옵션매매손익', 'U20'),  # (F:26) 
		('옵션매도대금', 'U20'),  # (F:27) 
		('옵션매수대금', 'U20'),  # (F:28) 
		('손익합계', 'U20'),  # (F:29) 
		('청산시평가현금', 'U20'),  # (F:30) 
		('주문가능총액위탁', 'U20'),  # (F:31) 
		('주문가능현금위탁', 'U20'),  # (F:32) 
		('수탁거부계좌구분', 'U1'),  # (F:33) 0:정상  1:매수거부 3:전체수탁거부  4:옵션매도매수수탁거부
		('지수선물정산차금', 'U20'),  # (F:34) 
		('주식선물정산차금', 'U20'),  # (F:35) 
		('지수선물매매손익', 'U20'),  # (F:36) 
		('주식선물매매손익', 'U20'),  # (F:37) 
		('실물인수도예정금액', 'U20'),  # (F:38) 
		])
	MULTI_OUTPUT_DTYPE = None


class SABC967Q1(BaseTR):
	NAME, DESCRIPTION = 'SABC967Q1 (bc924q_1)', '선물/옵션 잔고 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U4'),  # (F:01) 
		('구분', 'U1'),  # (F:02) 0:전체 			1:강세불리  2:약세불리
		('상품군', 'U1'),  # (F:03) 0:전체 (상품선물)	1:지수  2:주식옵션-> ASIS TOBE 1:선물			2:옵션
		('평균가구분코드', 'U1'),  # (F:04) 1: 단순평균가           2: 이동평균가
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U12'),  # (F:00) 
		('종목명', 'U20'),  # (F:01) 
		('매매구분', 'U2'),  # (F:02) 01:매도 02:매수 03:금전신탁
		('잔고수량', 'U18'),  # (F:03) 
		('청산가능수량', 'U18'),  # (F:04) 
		('미체결수량', 'U18'),  # (F:05) 
		('평균단가', 'U38'),  # (F:06) 소수점2자리
		('현재가', 'U20'),  # (F:07) 소수점2자리
		('전일대비', 'U20'),  # (F:08) 소수점2자리
		('전일대비율', 'U20'),  # (F:09) 소수점2자리
		('매입금액', 'U20'),  # (F:10) 
		('평가금액', 'U20'),  # (F:11) 
		('평가손익', 'U20'),  # (F:12) 
		('손익율', 'U20'),  # (F:13) 소수점2자리
		('전일대비손익', 'U20'),  # (F:14) 
		('손익가감액', 'U20'),  # (F:15) 
		('델타', 'U20'),  # (F:16) 소수점6자리
		('감마', 'U20'),  # (F:17) 소수점6자리
		('매매손익', 'U20'),  # (F:18) 
		('수수료', 'U20'),  # (F:19) 
		('계약당승수', 'U38'),  # (F:20) 
		('전일종가', 'U20'),  # (F:21) 
		('선물옵션구분', 'U1'),  # (F:22) 
		('베가', 'U20'),  # (F:23) 소수점6자리
		('세타', 'U20'),  # (F:24) 소수점6자리
		('기초자산', 'U30'),  # (F:25) 
		('원체결단가', 'U20'),  # (F:26) 
		])


class SABZ232Q1(BaseTR):
	NAME, DESCRIPTION = 'SABZ232Q1', '일별 계좌별 실현손익 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('상품', 'U2'),  # (F:01) 00: 전체     01: 종합계좌    10:코스피선물옵션 11: 코스닥선물옵션    21:증권저축잔고
		('비밀번호', 'U4'),  # (F:02) 
		('시작일', 'U8'),  # (F:03) 
		('종료일', 'U8'),  # (F:04) 
		('조회구분', 'U1'),  # (F:05) 0:전체, 1:이익, 2:손실, 3:보합
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('평균매수금액', 'U20'),  # (F:00) 
		('매도체결금액', 'U20'),  # (F:01) 
		('손익금액', 'U20'),  # (F:02) 
		('손익률', 'U20'),  # (F:03) 
		])
	MULTI_OUTPUT_DTYPE = np.dtype([
		('매매일자', 'U8'),  # (F:00) 
		('평균매수금액', 'U20'),  # (F:01) 
		('매도체결금액', 'U20'),  # (F:02) 
		('손익금액', 'U20'),  # (F:03) 
		('손익율', 'U20'),  # (F:04) 
		])


class SACA132Q1(BaseTR):
	NAME, DESCRIPTION = 'SACA132Q1', '거래원장 조회'
	INPUT_DTYPE = np.dtype([
		('관리자', 'U12'),  # (F:00) 
		('계좌번호', 'U11'),  # (F:01) 
		('상품', 'U2'),  # (F:02) 
		('비밀번호', 'U4'),  # (F:03) 
		('시작일', 'U8'),  # (F:04) 
		('종료일', 'U8'),  # (F:05) 
		('입력거래구분', 'U1'),  # (F:06) 0 : 전체, 1 : 매도. 2 : 매수, 3 : 입금, 4 : 출금,  5: 입고, 6: 출고, 8: 매도/매수, 9: 입금/출금,  A : 입고/출고, B : 환전, C : ELS/ELS, D : 배당금,  E : 대출이자, F : 신용이자
		('시장구분', 'U1'),  # (F:07) 0 : 전체, 1 : 국내, 2 : 해외
		('MMW내역포함', 'U1'),  # (F:08) 
		('RP상세여부', 'U1'),  # (F:09) 
		('종목코드', 'U12'),  # (F:10) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('일자', 'U8'),  # (F:00) 
		('출력거래구분', 'U40'),  # (F:01) 
		('적요', 'U50'),  # (F:02) 
		('종목번호', 'U12'),  # (F:03) 
		('종목명', 'U50'),  # (F:04) 
		('수량', 'U20'),  # (F:05) 
		('단가', 'U20'),  # (F:06) 
		('수수료', 'U20'),  # (F:07) 
		('제세금', 'U20'),  # (F:08) 
		('거래금액', 'U20'),  # (F:09) 
		('신용금액', 'U20'),  # (F:10) 
		('미수변제', 'U20'),  # (F:11) 
		('신용이자', 'U20'),  # (F:12) 
		('연체료', 'U20'),  # (F:13) 
		('대체계좌', 'U50'),  # (F:14) 
		('변동금액', 'U20'),  # (F:15) 
		('최종금액', 'U20'),  # (F:16) 
		('대출일', 'U8'),  # (F:17) 
		('만기일', 'U8'),  # (F:18) 
		('상품번호', 'U2'),  # (F:19) 
		('채권유형', 'U1'),  # (F:20) 
		('거래번호', 'U18'),  # (F:21) 
		('과표금액', 'U20'),  # (F:22) 
		('예탁금이용료', 'U20'),  # (F:23) 
		('주문자ID', 'U12'),  # (F:24) 
		('의뢰자명', 'U40'),  # (F:25) 
		('금융기관명', 'U40'),  # (F:26) 
		])
	MULTI_OUTPUT_DTYPE = None


class SACA108U1(BaseTR):
	NAME, DESCRIPTION = 'SACA108U1 ( ba201u_v )', '예수금 전환'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('출금상품번호', 'U2'),  # (F:01) 
		('증권비밀번호', 'U9'),  # (F:02) 
		('입금상품번호', 'U2'),  # (F:03) 
		('이체금액', 'U20'),  # (F:04) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('처리일자', 'U8'),  # (F:00) 
		('출금출납번호', 'U18'),  # (F:01) 
		('입금출납번호', 'U18'),  # (F:02) 
		('출금상품번호', 'U2'),  # (F:03) 
		('입금상품번호', 'U2'),  # (F:04) 
		('이체금액', 'U20'),  # (F:05) 
		])
	MULTI_OUTPUT_DTYPE = None


class SACA111Q1(BaseTR):
	NAME, DESCRIPTION = 'SACA111Q1', '전환가능예수금 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('상품구분', 'U2'),  # (F:01) 00: 전체     01: 종합계좌    10:코스피선물옵션 11: 코스닥선물옵션    21:증권저축잔고
		('비밀번호', 'U4'),  # (F:02) 
		('구분', 'U1'),  # (F:03) 항상 : ‘1’
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('상품', 'U2'),  # (F:00) 
		('상품명', 'U50'),  # (F:01) 
		('총예수금', 'U20'),  # (F:02) 
		('증거금사용액', 'U20'),  # (F:03) 
		('출금가능액', 'U20'),  # (F:04) 
		])


class SAGA504Q1(BaseTR):
	NAME, DESCRIPTION = 'SAGA504Q1', '대주가능종목조회'
	INPUT_DTYPE = np.dtype([
		('종목코드', 'U12'),  # (F:00) A+종목코드
		('자기유통구분코드', 'U1'),  # (F:01) 1:자기    2:유통
		('시장구분', 'U1'),  # (F:02) NULL: 전체  1: 거래소   0: 코스닥
		('구분코드', 'U1'),  # (F:03) NULL or 1:종목코드정렬, 2:대주수량정렬
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('종목코드2', 'U12'),  # (F:00) 
		('종목명', 'U50'),  # (F:01) 
		('대주한도수량', 'U18'),  # (F:02) 
		('대주한도금액', 'U20'),  # (F:03) 
		('대주수량', 'U18'),  # (F:04) 
		('당일대주신규주문수량', 'U18'),  # (F:05) 
		('당일대주신규체결수량', 'U18'),  # (F:06) 
		('전일대주신규체결수량', 'U18'),  # (F:07) 
		('당일대주상환체결수량', 'U18'),  # (F:08) 
		('전일대주상환체결수량', 'U18'),  # (F:09) 
		('대주결제기준한도금액', 'U20'),  # (F:10) 
		('기준일', 'U8'),  # (F:11) 
		('유통기준일', 'U8'),  # (F:12) 
		('현재가', 'U20'),  # (F:13) 
		('기준가', 'U20'),  # (F:14) 
		('수량', 'U18'),  # (F:15) 
		('금액', 'U20'),  # (F:16) 
		('수량1', 'U18'),  # (F:17) 
		('수량2', 'U18'),  # (F:18) 
		('수량3', 'U18'),  # (F:19) 
		('수량4', 'U18'),  # (F:20) 
		('수량5', 'U18'),  # (F:21) 
		('수량6', 'U18'),  # (F:22) 
		('금액1', 'U20'),  # (F:23) 
		('기준일자1', 'U8'),  # (F:24) 
		('기준일자2', 'U8'),  # (F:25) 
		('현재가격1', 'U20'),  # (F:26) 
		('기준가1', 'U20'),  # (F:27) 
		])


class SCDA601Q9(BaseTR):
	NAME, DESCRIPTION = 'SCDA601Q9', 'RP 매수가능금액조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U4'),  # (F:01) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('매수가능금액', 'U20'),  # (F:00) 
		])
	MULTI_OUTPUT_DTYPE = None


class SCDA601U2(BaseTR):
	'''** 이 TR은 10초이내 재호출이 불가능합니다. **
		펀드코드	 펀드명			펀드코드		펀드명
		1010		수시RP			1020		91일 RP
		2000		명품CMA용 RP	1030		182일 RP
		1015		28일 RP			1040		270일 RP
		1013		63일 RP			1050		365일 RP
	'''
	NAME, DESCRIPTION = 'SCDA601U2 ( be203u_B )', 'RP매수'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  #	
		('거래번호', 'U18'),  #	사용안함
		('처리지점', 'U3'),  #	사용안함
		('일자', 'U8'),  #	20081103
		('입출금액', 'U20'),  #	매수금액
		('수량', 'U18'),  #	매수금액
		('입금금액', 'U18'),  #	사용안함
		('순번', 'U17'),  #	사용안함
		('펀드코드', 'U4'),  #	5.4.5 RP 펀트코드표 참고
		('만기일자', 'U8'),  #	사용안함
		('약정이율', 'U20'),  #	사용안함
		('비밀번호', 'U33')  #	
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('거래번호', 'U18'), 
		('출납번호', 'U18'), 
		('예수금금잔', 'U20'), 
		('환매채금잔', 'U20'), 
		('평가금액', 'U20'), 
		('만기일자', 'U8'), 
		('약정이율', 'U20')
		])
	MULTI_OUTPUT_DTYPE = None


class SCDA601U4(BaseTR):
	'''** 이 TR은 10초이내 재호출이 불가능합니다. ** '''
	NAME, DESCRIPTION = 'SCDA601U4', 'RP매도'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('비밀번호', 'U33'),  # (F:01) 
		('펀드번호', 'U4'),  # (F:02) 5.4.5 RP 펀트코드표 참고
		('매도금액', 'U20'),  # (F:03) 전액환매일경우 매도금액을 999999999999로 고정
		('전액매도구분', 'U1'),  # (F:04) 전액환매일때에는 “1” 아닐경우 “0”
		('매수일자', 'U8'),  # (F:05) 사용안함
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('위탁예수금', 'U20'),  # (F:00) 
		('출납번호', 'U18'),  # (F:01) 
		('거래번호', 'U18'),  # (F:02) 
		('RP매도수량', 'U20'),  # (F:03) 
		])
	MULTI_OUTPUT_DTYPE = None


class SCDA703Q1(BaseTR):
	NAME, DESCRIPTION = 'SCDA703Q1', 'RP 거래내역 조회'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('시작일자', 'U8'),  # (F:01) 
		('종료일자', 'U8'),  # (F:02) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('거래일', 'U8'),  # (F:00) 
		('거래구분', 'U1'),  # (F:01) 
		('거래구분명', 'U20'),  # (F:02) 
		('종목코드', 'U4'),  # (F:03) 
		('종목명', 'U50'),  # (F:04) 
		('매수일', 'U8'),  # (F:05) 
		('만기일', 'U8'),  # (F:06) 
		('거래금액', 'U20'),  # (F:07) 
		('거래순번', 'U10'),  # (F:08) 
		('이자금액', 'U20'),  # (F:09) 
		('소득세', 'U20'),  # (F:10) 
		('주민세', 'U20'),  # (F:11) 
		('정산금액', 'U20'),  # (F:12) 
		('RP잔액', 'U20'),  # (F:13) 
		('매체구분명', 'U20'),  # (F:14) 
		('환매수가', 'U20'),  # (F:15) 
		('시간', 'U6'),  # (F:16) 
		])


class SGBA587Q2(BaseTR):
	NAME, DESCRIPTION = 'SGBA587Q2(Ea54061q_2	)', '일자별 잔고'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('상품', 'U2'),  # (F:01) 01: 종합계좌,          10:코스피선물옵션 11: 코스닥 선물옵션    21:증권저축잔고
		('일자', 'U8'),  # (F:02) 20081201
		('비밀번호', 'U4'),  # (F:03) 
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('종목코드', 'U7'),  # (F:00) Ex>A005930(삼성전자)
		('종목명', 'U'),  # (F:01) 
		('구분', 'U'),  # (F:02) Ex>”위탁현금”
		('결제잔고', 'U'),  # (F:03) 
		('평균단가', 'U'),  # (F:04) 
		('현재가', 'U'),  # (F:05) 
		('개별평가금액', 'U'),  # (F:06) 
		('손익금', 'U'),  # (F:07) 
		('손익율', 'U'),  # (F:08) 
		('대출일', 'U'),  # (F:09) 
		('만기일', 'U'),  # (F:10) 
		])


class SZAB105Q1(BaseTR):
	# ** 이 TR은 15초이내 재호출이 불가능합니다. **
	NAME, DESCRIPTION = 'SZAB105Q1', '일별 통화별 환율 조회'
	INPUT_DTYPE = np.dtype([
		('조회시작일', 'U8'),  # (F:00) 
		('조회종료일', 'U8'),  # (F:01) 
		('통화코드', 'U3'),  # (F:02) USD: 미국 달러
		('회차별조회', 'U1'),  # (F:03) N: 조회 하지 않음
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('통화코드', 'U3'),  # (F:00) 
		('고시일자', 'U8'),  # (F:01) 
		('통화명', 'U50'),  # (F:02) 
		('고시회차', 'U18'),  # (F:03) 
		('외국환기준율', 'U20'),  # (F:04) 
		('실시간기준율', 'U20'),  # (F:05) 
		('전신환매수율', 'U20'),  # (F:06) 
		('전신환매도율', 'U20'),  # (F:07) 
		('현찰매수율', 'U20'),  # (F:08) 
		('현찰매도율', 'U20'),  # (F:09) 
		('대미환산율', 'U20'),  # (F:10) 
		('고시시간', 'U14'),  # (F:11) 
		])


class TR_0100_M6(BaseTR):
	NAME, DESCRIPTION = 'TR_0100_M6', '1852화면 불성실공시지정/거래정지 종목 조회'
	INPUT_DTYPE = np.dtype([
		('장구분', 'U4'),  # (F:00) 0: 코스피, 1:코스닥, 9: 전체
		('시장조치구분', 'U1'),  # (F:01) 1: 불성실공시지정, 2: 거래정지
		('언어구분', 'U1'),  # (F:02) K or 공백: 한글, E: 영문
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U30'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U8'),  # (F:03) 
		('전일대비', 'U8'),  # (F:04) 
		('전일대비율', 'U8'),  # (F:05) 
		('매도1호가', 'U8'),  # (F:06) 
		('매수1호가', 'U8'),  # (F:07) 
		('누적거래량', np.uint64),  # (F:08) 
		('장구분', 'U1'),  # (F:09) 
		])


class TR_INDI004(BaseTR):
	NAME, DESCRIPTION = 'TR_INDI004', '기관 장중 매매현황 추정'
	INPUT_DTYPE = np.dtype([
		('거래소구분', 'U1'),  # (F:00) 0:코스피(거래소) 1:코스닥 2: 전체
		('정렬구분', 'U2'),  # (F:01) 01: 거래량순 02:보험순매수순 03:투신순매수순 04:은행순매수순 05:기타금융순매수순 06: 연기금순매수순 07:기타법인순매수순 08:개인순매수순 09:외국인순매수순 10:기관계순매수순
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('시간', 'U4'),  # (F:00) 
		])
	MULTI_OUTPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 
		('종목명', 'U40'),  # (F:01) 
		('현재가', np.uint32),  # (F:02) 
		('전일대비구분', 'U1'),  # (F:03) 
		('전일대비', 'U8'),  # (F:04) 
		('누적거래량', np.uint64),  # (F:05) 
		('보험매수', 'U20'),  # (F:06) 
		('보험매도', 'U20'),  # (F:07) 
		('보험순매수', 'U20'),  # (F:08) 
		('투신매수', 'U20'),  # (F:09) 
		('투신매도', 'U20'),  # (F:10) 
		('투신순매수', 'U20'),  # (F:11) 
		('은행매수', 'U20'),  # (F:12) 
		('은행매도', 'U20'),  # (F:13) 
		('은행순매수', 'U20'),  # (F:14) 
		('기타금융매수', 'U20'),  # (F:15) 
		('기타금융매도', 'U20'),  # (F:16) 
		('기타금융순매수', 'U20'),  # (F:17) 
		('연기금 매수', 'U20'),  # (F:18) 
		('연기금 매도', 'U20'),  # (F:19) 
		('연기금 순매수', 'U20'),  # (F:20) 
		('기타법인매수', 'U20'),  # (F:21) 
		('기타법인매도', 'U20'),  # (F:22) 
		('기타법인순매수', 'U20'),  # (F:23) 
		('개인매수', 'U20'),  # (F:24) 
		('개인매도', 'U20'),  # (F:25) 
		('개인순매수', 'U20'),  # (F:26) 
		('외국인매수', 'U20'),  # (F:27) 
		('외국인매도', 'U20'),  # (F:28) 
		('외국인순매수', 'U20'),  # (F:29) 
		('기관계매수', 'U20'),  # (F:30) 
		('기관계매도', 'U20'),  # (F:31) 
		('기관계순매수', 'U20'),  # (F:32) 
		])


class tr_5200(BaseTR):
	NAME, DESCRIPTION = 'tr_5200', '현물 실시간 주문체결 조회(고객용)'
	INPUT_DTYPE = np.dtype([
		('계좌수', 'U3'),  # (F:00) 계좌번호리스트의 개수
		('체결미체결구분', 'U1'),  # (F:01) 0:전체 			1:미체결  2:체결
		('종목코드', 'U12'),  # (F:02) 전체조회시 SPACE
		('합산구분', 'U1'),  # (F:03) 1: 주문별 합산 		2: 종목별합산
		('매매구분', 'U1'),  # (F:04) 0: 전체 		1: 매도  2: 매수
		('ECN구분', 'U1'),  # (F:05) 현재 사용안함
		('계좌번호리스트', 'U1024'),  # (F:06) 계좌번호리스트
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('처리구분', 'U2'),  # (F:00) 00:정상주문 		01:정정주문  02:취소주문 		03:체결  04:정정확인		05:취소확인  09:주문거부 		19:접수거부  99:반대거부
		('지점번호', 'U3'),  # (F:01) 
		('계좌번호', 'U11'),  # (F:02) 
		('시장구분', 'U2'),  # (F:03) 1:KOSPI			2:KOSDAQ  3:선물/옵션/개별주식 	4:제3시장  5:ECN 			6:KOFEX
		('상품구분', 'U2'),  # (F:04) 
		('주문번호', 'U7'),  # (F:05) 
		('원주문번호', 'U7'),  # (F:06) 
		('주문구분', 'U2'),  # (F:07) 01:보통 		02:희망대량  03:신고대량 		05:시장가  06:조건부지정가 	09:자사주  26:조건부희망대량 	71:시간외종가  72:시간외대량 		79:시간외자기대량  81:ECN 일반 		82:ECN 대량
		('매도매수구분', 'U2'),  # (F:08) 01:매도			02:매수
		('매매유형', 'U2'),  # (F:09) 01:현금매도 		02:현금매수  03:신용매도 		04:신용매수   05:저축매도 		06:저축매수  11:선물일반매도 	12:선물반대매도  13: 프로그램매도 	14:프로그램매수  15:종가현금매도 	16:종가현금매수  17:종가신용매도 	18:종가신용매수  19:종가저축매도 	20:종가저축매수  21:종가대량매도 	22:종가대량매수  23:선물대용매도 	25:종가저축매도   26:종가저축매수 	27:예탁담보매도
		('상태', 'U2'),  # (F:10) 01:접수 		02:확인  03:거부
		('종목코드', 'U12'),  # (F:11) 
		('종목명', 'U20'),  # (F:12) 
		('계좌명', 'U20'),  # (F:13) 
		('주문수량', 'U8'),  # (F:14) 
		('주문가격', np.uint32),  # (F:15) 
		('체결수량합', 'U8'),  # (F:16) 
		('정정수량합계', 'U8'),  # (F:17) 
		('취소수량합계', 'U8'),  # (F:18) 
		('확인수량', 'U8'),  # (F:19) 
		('미체결수량', 'U8'),  # (F:20) 
		('접수시간', 'U8'),  # (F:21) 
		('체결번호', 'U7'),  # (F:22) 
		('체결수량', 'U8'),  # (F:23) 
		('체결단가', 'U10'),  # (F:24) 
		('체결시간', 'U8'),  # (F:25) 
		('채널', 'U2'),  # (F:26) 
		('입력자', 'U12'),  # (F:27) 
		('관리자', 'U12'),  # (F:28) 
		('일련번호', 'U8'),  # (F:29) 
		('체결금액', 'U12'),  # (F:30) 
		('현재가', 'U12'),  # (F:31) 
		('주문조건', 'U12'),  # (F:32) 
		('체결금액합', 'U12'),  # (F:33) 
		])


class tr_5300(BaseTR):
	NAME, DESCRIPTION = 'tr_5300', '선물 실시간 주문체결 조회(고객용)'
	INPUT_DTYPE = np.dtype([
		('계좌수', 'U3'),  # (F:00) 계좌번호리스트의 개수
		('체결미체결구분', 'U1'),  # (F:01) 0:전체 			1:미체결 2:체결
		('종목코드', 'U12'),  # (F:02) 전체조회시 SPACE
		('합산구분', 'U1'),  # (F:03) 1:주문별 합산		2:종목별합산
		('매매구분', 'U1'),  # (F:04) 0:전체			1:매도 2:매수
		('계좌번호리스트', 'U1024'),  # (F:05) 계좌번호 최대 200개
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, True
	SINGLE_OUTPUT_DTYPE = None
	MULTI_OUTPUT_DTYPE = np.dtype([
		('처리구분', 'U2'),  # (F:00) 00:정상주문 		01:정정주문 	 02:취소주문 		03:체결 04:정정확인 		05:취소확인  09:주문거부
		('지점번호', 'U3'),  # (F:01) 
		('계좌번호', 'U11'),  # (F:02) 
		('시장구분', 'U2'),  # (F:03) 1:KOSPI			2:KOSDAQ 3:선물/옵션/개별주식	4:제3시장 5:ECN			6:KOFEX
		('상품구분', 'U2'),  # (F:04) 
		('주문번호', 'U7'),  # (F:05) 
		('원주문번호', 'U7'),  # (F:06) 
		('주문구분', 'U2'),  # (F:07) 
		('매도매수구분', 'U2'),  # (F:08) 
		('상태', 'U2'),  # (F:09) 
		('종목코드2', 'U12'),  # (F:10) 
		('종목명', 'U20'),  # (F:11) 
		('계좌명', 'U20'),  # (F:12) 
		('주문수량', 'U8'),  # (F:13) 
		('주문가격', np.uint32),  # (F:14) 
		('체결수량합계', 'U8'),  # (F:15) 
		('정정수량합계', 'U8'),  # (F:16) 
		('취소수량합계', 'U8'),  # (F:17) 
		('확인수량', 'U8'),  # (F:18) 
		('미체결수량', 'U8'),  # (F:19) 
		('접수시간', 'U8'),  # (F:20) 
		('체결번호', 'U7'),  # (F:21) 
		('체결수량', 'U8'),  # (F:22) 
		('체결단가', 'U10'),  # (F:23) 
		('체결시간', 'U8'),  # (F:24) 
		('채널', 'U2'),  # (F:25) 
		('입력자', 'U12'),  # (F:26) 
		('관리자', 'U12'),  # (F:27) 
		('일련번호', 'U8'),  # (F:28) 
		('체결금액', 'U0'),  # (F:29) 
		('현재가', 'U0'),  # (F:30) 
		('체결금액합', 'U12'),  # (F:31) 
		('주문조건', 'U12'),  # (F:32) 
		('기초자산명', 'U12'),  # (F:33) 
		])


class TR_5440(BaseTR):
	NAME, DESCRIPTION = 'TR_5440', '실시간잔고 조회(선물/옵션)'
	INPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('상품구분', 'U2'),  # (F:01) “10”
		('조회구분', 'U1'),  # (F:02) “0”
		('종목코드2', 'U12'),  # (F:03) “%”
		])
	REALTIME_AVAILABLE = False
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, True
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('선물총매매손익', np.uint64),  # (F:00) 
		('옵션총매매손익', np.uint64),  # (F:01) 
		('총매매손익', np.uint64),  # (F:02) 
		])
	MULTI_OUTPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 
		('상품구분', 'U2'),  # (F:01) 
		('종목코드', 'U12'),  # (F:02) 
		('종목명', 'U20'),  # (F:03) 
		('계좌명', 'U20'),  # (F:04) 
		('매도매수구분', 'U2'),  # (F:05) 01: 매도 		02 :매수
		('당일잔고', 'U8'),  # (F:06) 
		('평균단가', 'U8'),  # (F:07) 
		('청산가능수량', 'U8'),  # (F:08) 
		('미체결수량', 'U8'),  # (F:09) 
		('현재가', np.uint32),  # (F:10) 
		('전일대비', np.uint32),  # (F:11) 
		('전일대비율', 'U4'),  # (F:12) 
		('평가금액', 'U12'),  # (F:13) 
		('평가손익', 'U12'),  # (F:14) 
		('손익률', 'U6'),  # (F:15) 
		('수수료', 'U12'),  # (F:16) 
		('세금', 'U12'),  # (F:17) 
		('시스널', 'U1'),  # (F:18) 사용안함.
		('매입금액', np.uint64),  # (F:19) 
		('승수', 'U12'),  # (F:20) 
		('종목구분', 'U1'),  # (F:21) 1:선물 2:지수옵션 3:주식옵션
		('매매손익', 'U12'),  # (F:22) 
		('기초자산명', 'U20'),  # (F:23) 
		])




class AA(BaseRealtime):
	NAME, DESCRIPTION = 'AA', '현물실시간주문체결'
	INPUT_DTYPE = "*"
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('처리구분', 'U2'),         # (F:00) 00: 정상주문 03: 체결 04: 정정확인	05: 취소확인 09: 주문거부 19: 접수거부 99: 반대거부 98: 취소거부
		('지점번호', 'U3'),         # (F:01)
		('계좌번호', 'U11'),        # (F:02)
		('시장구분', 'U2'),         # (F:03) 01: KOSPI 02:KOSDAQ 03:선물/옵션/개별주식 04:제3시장 05:ECN 06:KOFEX
		('상품구분', 'U2'),         # (F:04)
		('주문번호', 'U7'),         # (F:05)
		('원주문번호', 'U7'),       # (F:06) 정정, 취소 주문일경우만
		('주문구분', 'U2'),         # (F:07) 01:보통 02:희망대량 03:신고대량 05:시장가 06:조건부지정가 	09:자사주 10:자사주직접스탁옵션 11:금전신탁자기주식 12: 최유리지정가 13:최우선지정가 26:조건부희망대량	61:장개시전시간외종가 71:시간외종가 72:시간외대량 79:시간외자기대량 81:시간외 단일가 82:ECN 대량
		('매도매수구분', 'U2'),     # (F:08) 01:매도 02:매수
		('매매구분(유형)', 'U2'),   # (F:09) 01:현금매도 		02:현금매수  03:신용매도 04:신용매수  05:저축매도 		06:저축매수  11:선물일반매도 	12:선물반대매도  13:프로그램매도 	14:프로그램매수  15:시간외종가현금매도 	16:시간외종가현금매수 17:시간외종가신용매도	18:시간외종가신용매수 19:시간외종가저축매도	20:시간외종가저축매수 21:시간외종가대량매도	22:시간외종가대량매수 23:시간외선물대용매도 	25:시간외저축매도 26:시간외저축매수 	27:예탁담보매도
		('상태', 'U2'),             # (F:10) 01:접수 		02:확인  03:거부
		('종목코드', 'U12'),        # (F:11)
		('종목명', 'U20'),         # (F:12)
		('계좌명', 'U20'),         # (F:13)
		('주문수량', np.uint32),    # (F:14)
		('주문가격', np.uint32),    # (F:15)
		('체결수량합', np.uint32),  # (F:16)
		('정정수량합계', np.uint32),# (F:17)
		('취소수량합계', np.uint32),# (F:18)
		('확인수량', np.uint32),    # (F:19)
		('미체결수량', np.uint32),  # (F:20)
		('접수시간', np.uint32),    # (F:21)
		('체결번호', 'U7'),         # (F:22)
		('체결수량', np.uint32),    # (F:23)
		('체결단가', np.uint32),    # (F:24)
		('체결시간', np.uint32),    # (F:25)
		('채널', 'U2'),           # (F:26)
		('입력자', 'U12'),         # (F:27)
		('관리자', 'U12'),         # (F:28)
		('일련번호', 'U8'),         # (F:29)
		('현재가', np.uint32),     # (F:30)
		('주문조건', 'U2'),         # (F:31)
		('원주문구분', 'U1')        # (F:32) “0”: 정상주문 결과 “1”:원주문에 대한 결과( 정정/취소 일 때)
		])
	MULTI_OUTPUT_DTYPE = None

	def reg_realtime(self, account_num: str = INPUT_DTYPE) -> bool:
		return super().reg_realtime(code=account_num)
	def unreg_realtime(self, account_num: str) -> bool:
		return super().unreg_realtime(code=account_num)



class AB(BaseRealtime):
	NAME, DESCRIPTION = 'AB', '선물 옵션 실시간 주문 체결'
	INPUT_DTYPE = "*"
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('처리구분', 'U2'),  # (F:00) 00:정상주문 	      03:체결 04:정정확인 	      05:취소확인  07: 지정가전환        09:주문거부
		('지점번호', 'U3'),  # (F:01) 
		('계좌번호', 'U11'),  # (F:02) 
		('시장구분', 'U2'),  # (F:03) 1=KOSPI, 2=KOSDAQ, 3=파생, 4=프리보드 5=일반채권, C=CME, 야간달러선물 H=EUREX, D=소액채권, E=REPO채권, F=코넥스, G=KTS채권,  K=금현물
		('상품구분', 'U2'),  # (F:04) 
		('주문번호', 'U7'),  # (F:05) 
		('원주문번호', 'U7'),  # (F:06) 
		('주문구분', 'U2'),  # (F:07) L:지정가 		M:시장가  C:조건부지정가 		B:최유리지정가
		('매도매수구분', 'U2'),  # (F:08) 01: 매도 		02 :매수
		('상태', 'U2'),  # (F:09) 01:접수 		02:확인  03:거부
		('종목코드', 'U12'),  # (F:10) 
		('종목명', 'U20'),  # (F:11) 
		('계좌명', 'U20'),  # (F:12) 
		('주문수량', 'U8'),  # (F:13) 
		('주문단가', np.uint32),  # (F:14) 
		('체결수량 합계', 'U8'),  # (F:15) 
		('정정수량 합계', 'U8'),  # (F:16) 
		('취소수량 합계', 'U8'),  # (F:17) 
		('확인수량', 'U8'),  # (F:18) 
		('미체결수량', 'U8'),  # (F:19) 
		('접수시간', 'U8'),  # (F:20) 
		('체결번호', 'U7'),  # (F:21) 
		('체결수량', 'U8'),  # (F:22) 
		('체결단가', 'U10'),  # (F:23) 
		('체결시간', 'U8'),  # (F:24) 
		('채널', 'U2'),  # (F:25) 
		('입력자', 'U12'),  # (F:26) 
		('관리자', 'U12'),  # (F:27) 
		('일련번호', 'U8'),  # (F:28) 
		('현재가', 'U10'),  # (F:29) 
		('원주문구분', 'U1'),  # (F:30) “0”: 정상주문 결과 “1”:원주문에 대한 결과( 정정/취소 일 때)
		('주문조건', 'U1'),  # (F:31) ‘:일반’ ‘F:FOK’   ‘I:IOC’M:IFM D:DIFM
		('기초자산명', 'U20'),  # (F:32) 
		('최근월물 주문가격', np.uint32),  # (F:33) 
		('차근월물 주문가격', np.uint32),  # (F:34) 
		('실시간가격제한주문정보', 'U1'),  # (F:35) 처리구분 00 일 경우 “1”이면 즉시전환 처리구분 07 일 경우 “1”이면 접수 후 전환 처리구분 05 일 경우 “1”이면 거래소 자동취소
		])
	MULTI_OUTPUT_DTYPE = None

	def reg_realtime(self, account_num: str = INPUT_DTYPE) -> bool:
		return super().reg_realtime(code=account_num)
	def unreg_realtime(self, account_num: str) -> bool:
		return super().unreg_realtime(code=account_num)


class AD(BaseRealtime, BaseTR):
	NAME, DESCRIPTION = 'AD', '현물 실시간 주문 체결'
	INPUT_DTYPE = "*"
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),  # (F:00) 계좌번호
		('상품구분', 'U2'),  # (F:01) 상품구분
		('종목코드', 'U12'),  # (F:02) 종목코드
		('주식구분', 'U1'),  # (F:03) 
		('종목명', 'U20'),  # (F:04) 
		('계좌명', 'U20'),  # (F:05) 
		('당일잔고', 'U8'),  # (F:06) 
		('당일이동평균단가', 'U8'),  # (F:07) 
		('주문가능수량', 'U8'),  # (F:08) 
		('매도미체결수량', 'U8'),  # (F:09) 
		('평가금액', 'U12'),  # (F:10) 
		('평가손익', 'U12'),  # (F:11) 
		('손익률', 'U8'),  # (F:12) 
		('실현손익', 'U12'),  # (F:13) 
		('미실현손익', 'U12'),  # (F:14) 
		('수수료', 'U12'),  # (F:15) 
		('세금', 'U12'),  # (F:16) 
		('총실현손익', 'U15'),  # (F:17) 
		('총실현손익률', 'U15'),  # (F:18) 신규 항목
		('총평가금액', 'U15'),  # (F:19) 신규 항목
		('현재가', 'U8'),  # (F:20) Index 변경
		])
	MULTI_OUTPUT_DTYPE = None
	def reg_realtime(self) -> bool:
		return super().reg_realtime(code=self.INPUT_DTYPE)
	def unreg_realtime(self) -> bool:
		return super().unreg_realtime(code=self.INPUT_DTYPE)


class AE(BaseRealtime):
	NAME, DESCRIPTION = 'AE', '실시간 잔고(선물/옵션)'
	INPUT_DTYPE = "*" or np.dtype(['계좌번호', 'U11'])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('계좌번호', 'U11'),	
		('상품구분', 'U2'),	
		('종목코드', 'U12'),	
		('종목명', 'U30'),	
		('계좌명', 'U20'),	
		('매수매도구분', 'U2'),	 # 01: 매도 02 :매수
		('당일잔고', np.uint32),	
		('평균단가', np.float32),
		('미체결수량', np.uint32),	
		('청산가능수량', np.uint32),	
		('총매입금액', np.uint64),	
		('평가금액', np.uint64),	
		('평가손익', np.uint64),	
		('손익률', 'U8'),	
		('수수료', np.uint64),	
		('세금', np.uint64),	
		('시그널', 'U1'),		# 사용안함.
		('현재가', np.float32),		#	
		('총실현손익', np.uint64),	# 사용안함
		('총미현손익', np.uint64),	# 사용안함
		('총손익', np.uint64),		# 사용안함
		('총수수료', np.uint64),	# 사용안함
		('총세금', np.uint64),		# 사용안함
		('거래승수', np.uint32),		#
		('종목구분', 'U1'),		# 1:선물  2:지수옵션  3:주식옵션
		('종목매매손익', np.uint64),	#
		('선물총매매손익', np.uint64),	 #
		('옵션총매매손익', np.uint64),	#
		('기초자산명', 'U20'),		# 
		('이동평균단가', np.float32),  #  	
		('원체결단가', np.float32),    # 	
		('이동평균매매손익', np.uint64),  #
		])
	MULTI_OUTPUT_DTYPE = None

	def reg_realtime(self, account_num: str = INPUT_DTYPE) -> bool:
		return super().reg_realtime(code=account_num)
	def unreg_realtime(self, account_num: str) -> bool:
		return super().unreg_realtime(code=account_num)



class IM(BaseRealtime):
	NAME, DESCRIPTION = 'IM', '시장조치 정보 실시간'
	INPUT_DTYPE = np.dtype([
		('시장구분', 'U1'),  # (F:00) *: 전체 0:유가증권 1:코스닥, 2:K200지수선물,  3:K300지수옵션 6:스타지수선물, 8:코넥스 V:변동성지수선물, S:섹터지수선물
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('시장구분', 'U1'),  # (F:00) 0:유가증권 1:코스닥, 2:K200지수선물,  3:K300지수옵션 6:스타지수선물, 8:코넥스 V:변동성지수선물, S:섹터지수선물
		('조치구분', 'U1'),  # (F:01) 1:CB, 2:사이드카, 3:SHUTDOWN,  4:가격제한폭확대예고 5:파생장중추가증거금발동
		('시간', 'U6'),  # (F:02) 
		('상태', 'U1'),  # (F:03) 1:발동, 2:해제  (해제는 CB, 사이드카인 경우만 해당)
		('적용단계', 'U2'),  # (F:04) 
		('기준종목가격확대발생코드', 'U1'),  # (F:05) <파생> U:상승, D:하락
		('가격확대예정시각', 'U8'),  # (F:06) <파생>
		('메시지', 'U200'),  # (F:07) 
		])
	MULTI_OUTPUT_DTYPE = None


class TI(BaseRealtime):
	NAME, DESCRIPTION = 'TI', '현물 종목상태정보2 (VI)'
	INPUT_DTYPE = np.dtype([
		('단축코드', 'U6'),  # (F:00) 전종목: *
		])
	REALTIME_AVAILABLE = True
	IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = True, False
	SINGLE_OUTPUT_DTYPE = np.dtype([
		('전송시간', 'U6'),  # (F:00) 발생시간
		('단계구분값', 'U1'),  # (F:01) 1: 기준가대비 9.5% 상승 2: 기준가대비 9.0% 상승 3: 기준가대비 8.5% 상승 4: 기준가대비 8.5% 하락 5: 기준가대비 9.0% 하락 6: 기준가대비 8.5% 하락 7: 1~3단계 진입 후 기준가 대비 7.% 도달 V: VI 발동 – 상승 I: VI 발동 – 하락 A: VI 해제 임박 (진입 후 2분) R: VI 해제
		('기준값', np.uint32),  # (F:02) 
		('VI종류', 'U1'),  # (F:03) S: 정적 D: 동적 B: 정적 + 동적 동시
		('단축코드', 'U6'),  # (F:04) 
		])
	MULTI_OUTPUT_DTYPE = None


