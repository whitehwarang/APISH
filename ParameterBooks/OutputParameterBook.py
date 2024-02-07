
처리구분 = {
    '00': '정상주문', '03': '체결', '04': '정정확인', '05': '취소확인',
    '09': '주문거부', '19': '접수거부', '99': '반대거부', '98': '취소거부'
}

주문구분 = {
    '01': '보통',  '02': '희망대량', '03': '신고대량',
    '05': '시장가', '06': '조건부지정가',	'09': '자사주',
    '26': '조건부희망대량',   '71': '시간외종가',
    '72': '시간외대량',      '79': '시간외자기대량',
    '81':'시간외 단일가',    '82': 'ECN 대량'
}

매도매수구분 = {
    '01': '매도', '02': '매수'
}

매매구분 = {
    '01': '현금매도', 		    '02': '현금매수',
    '03': '신용매도', 		    '04': '신용매수',
    '05': '저축매도', 		    '06': '저축매수',
    '11': '선물일반매도', 	    '12': '선물반대매도',
    '13': '프로그램매도', 	    '14': '프로그램매수',
    '15': '시간외종가현금매도',   '16': '시간외종가현금매수',
    '17': '시간외종가신용매도',   '18': '시간외종가신용매수',
    '19': '시간외종가저축매도',   '20': '시간외종가저축매수',
    '21': '시간외종가대량매도',   '22': '시간외종가대량매수',
    '23': '시간외선물대용매도',   '25': '시간외저축매도',
    '26': '시간외저축매수', 	    '27': '예탁담보매도'
}

상태 = {'01': '접수', '02': '확인', '03': '거부'}

원주문구분 = {'0': '정상주문 결과', '1': '원주문에 대한 결과(정정/취소일 때)'}

장구분 = {
    '1': '정규장', '2': '장개시전시간외', '3': '장종료후시간외종가', '4': '장종료후시간외단일가',
    '7': '일반BUY-IN', '8': '당일BUY-IN'
}
#장구분 = {'0': 'KOSPI', '1': 'KOSDAQ'}
시장구분 = {
    '0': 'KOSPI', '1': 'KOSDAQ',
    '01': 'KOSPI', '02': 'KOSDAQ', '03': '선물/옵션/개별주식',
    '04': '제3시장', '05': 'ECN', '06': 'KOFEX'
}

KOSPI200세부업종 = {
    '0': '미분류',    '1': '제조업',    '2': '전기통신',
    '3': '건설',    '4': '유통서비스',    '5': '금융',
    '6': '금융',    '7': '필수소비재',    '8': '자유소비재',
    '9': '기타',    'A': '거래소외국주',    'B': '코스닥외국주',
    'Y': '산업재',    'Z': '건강관리',    'X': '커뮤니케이션서비스'
}

거래정지구분 = {'0': '정상', '1': '정지', '5': 'CB발동'}

관리구분 = {'0': '정상', '1': '관리'}

시장경보구분코드 = {'0': '정상', '1': '주의', '2': '경고', '3': '위험'}

락구분 = {'00': '발생안함', '01': '권리락', '02':'배당락', '03': '분배락',
         '04': '권배락', '05': '중간배당락', '06': '권리중간배당락', '99': '기타'}

# 증거금구분 = {'A': '15%', 'B': '20%', 'C': '25%', 'D': '100%', 'E': 'E', 'Z': 'Z'}
# :: 현금/대용에 따라 다름

ETF구분자 = {'0':'일반형', '1':'투자회사형', '2':'수익증권형'}

소속구분 = {
    'ST':'주식',          'MF':'증권투자회사',      'RT':'리츠',
    'SC':'선박투자회사',   'IF':'인프라투융자회사',   'DR':'예탁증서',
    'SW':'신주인수권증권', 'SR':'신주인수권증서',     'BW':'주식워런트증권(ELW)',
    'FU':'선물',          'OP':'옵션',              'EF':'상장지수펀드(ETF)',
    'BC':'수익증권',        'FE':'해외ETF',           'FS':'해외원주',
    'EN': 'ETN'}
