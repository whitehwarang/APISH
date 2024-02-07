# 신한투자증권의 API[i indi] 이용 Python Package
 - (TR) 신한투자증권의 TR 데이터를 동기식으로 요청하여 받을 수 있다.
 - (실시간) 실시간(Realtime) 데이터는 지속적으로 받아 같은 변수에 저장한다.
 - 본 package는 비동기 TR을 지원하지 않는다.
 - 요청한 데이터가 SingleData만 제공하면, 그 데이터를 TR_instance.single_output에 저장하고,
 - 요청한 데이터가 MultiData만 제공하면, 그 데이터를 TR_instance.multi_output에 저장하며,
 - 요청한 데이터가 SingleData와 MultiData 모두를 제공하면, 그 데이터를 TR_instance.single_output, TR_instance.multi_output에 각각 저장한다.

## TR 이용 예제코드
```
    import APISH2 as api
    
    # indi를 시작하기 위한 indi 객체 생성
    indi_instance = api.new_indi('strategy1')
    
    # indi 접속
    indi_instance.StartIndi('id', 'password', 'cert_password')
    
    # TR 객체 생성 : 해당 TR이 이용할 indi 객체를 반드시 지정하여야 함.
    tr_schart = api.TR_SCHART(indi_instance=indi_instance)

    # 데이터 요청(request)하여 수신
    chart = tr_schart.rq_data(code6='005930', 
                              그래프종류=IBook.그래프종류.일데이터, 
                              시간간격='1',
                              시작일='20230101',
                              종료일='20231231',
                              조회갯수='250')
    
    # 출력
    print(chart)
    print(tr_schart.multi_output)
    assert chart == tr_schart.multi_output
    indi_instance.CloseIndi()
```

## 실시간 이용 예제코드
```
    import time
    import datetime
    import APISH2 as api
    
    # indi를 시작하기 위한 indi 객체 생성
    main_indi_instance = api.new_indi('strategy1')
    
    # indi 접속
    main_indi_instance.StartIndi('id', 'password', 'cert_password')
    
    # 실시간(realtime) 기능 이용을 위한 별도 indi 객체 생성
    rt_indi_instance_1 = api.new_indi('rt_1', is_realtime=True)
    rt_indi_instance_2 = api.new_indi('rt_2', is_realtime=True)
    
    # 실시간 객체 생성
    sc1 = api.SC(indi_instance=rt_indi_instance_1)
    sc2 = api.SC(indi_instance=rt_indi_instance_2)

    # 실시간 등록
    cd1, cd2 = '005930', '005380'
    sc1.reg_realtime(cd1)  # 삼성전자
    sc2.reg_realtime(cd2)  # 현대차

    # 출력    
    for i in range(60):
        print(sc1.single_output)
        print(sc2.single_output)
        time.sleep(1)
    
    # 등록해제
    sc1.unreg_realtime(cd1)
    sc2.unreg_realtime(cd2)
    
    # indi 접속 해제
    indi_instance.CloseIndi()
```