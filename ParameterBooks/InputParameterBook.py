
class 시장구분:
    전체 = '0'
    코스피 = '1'
    코스닥 = '2'


class 선물대용매도여부:
    일반 = '0'
    KOSPI = '1'
    KOSDAQ = '2'
    예탁담보 = '3'


class 신용거래구분:
    보통 = '00'
    유통융자매수 = '01'
    자기융자매수 = '03'
    유통대주매도 = '05'
    자기대주매도 = '07'
    차입매도 = '08'
    유통융자매도상환 = '11'
    유통융자현금상환 = '12'
    자기융자매도상환 = '33'
    자기융자현금상환 = '34'
    유통대주매수상환 = '55'
    유통대주현물상환 = '56'
    자기대주매수상환 = '77'
    차입매수 = '88'
    예탁담보대출 = '91'
    예탁담보매도상환 = '92'
    예탁담보현금상환 = '93'
    주식청약대출 = '96'
    주식청약상환 = '97'


class 매도매수구분:  # OutputParameterBook과 중복
    매도 = '1'
    매수 = '2'
    정정 = '3'
    취소 = '4'


class 정규시간외구분코드:
    정규장 = '1'
    장개시전시간외 = '2'
    장종료후시간외종가 = '3'
    장종료후시간외단일가 = '4'
    장종료후시간외대량 = '5'


class 호가유형코드:
    시장가 = '1'
    지정가 = '2'
    조건부지정가 = 'I'
    최유리 = 'X'
    최우선 = 'Y'
    변동없음 = 'Z'  # 정정주문시


class 주문조건코드:
    일반 = '0'
    IOC = '3'
    FOK = '4'


class 신용대출통합주문구분코드:  # (매도상환의 경우)
    해당없음 = '0'
    대출일 = '1'
    선입선출 = '2'
    후입선출 = '3'


class 결과메세지_처리여부:
    네 = 'Y'
    아니오 = 'N'


class 그래프종류:
    분데이터 = '1'
    일데이터 = 'D'
    주데이터 = 'W'
    월데이터 = 'M'


class 단위:
    기본 = 1
    억원 = 10000 * 10000
    만원 = 10000


class 언어구분:     # TR_0100_M8
    한글 = 'K'
    영문 = 'E'


class 단기과열구분:     # TR_0100_M8
    지정예고 = '1'
    지정 = '2'

    
