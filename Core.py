import sys
import time
from functools import partial
from typing import Dict

import pythoncom
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget

from . import APIErrors, Logger, Config, TRRT


if not QApplication.instance():
    app = QApplication(sys.argv)


def _register_handlers(target_inst) -> None:
    """ TR 및 realtime_TR의 Request 데이터 수신 처리 핸들러를 등록한다. """
    partial_func0 = partial(__received_tr_data_handler, target_inst)
    partial_func1 = partial(__received_sys_msg_handler, target_inst)
    target_inst.ReceiveData.connect(partial_func0)
    target_inst.ReceiveSysMsg.connect(partial_func1)
    if target_inst._is_realtime:
        target_inst.ReceiveRTData.connect(__receive_realtime_data_handler)
    #print(" <<< 이벤트 핸들러 연결 완료 >>> ")


def __received_tr_data_handler(target_inst, rqid: int) -> None:
    """ TR의 Request 데이터 수신 처리 핸들러 """
    tr_inst = target_inst._rqidD.pop(rqid, None)
    if tr_inst is None:
        # 23-04-19 make this code as a comment. and make it logged.
        #raise APIErrors.RqIdNotExistError(f"rqid : {rqid} does not exist in the rqid Dictionary")
        Logger.write_log(f"rqid : {rqid} does not exist in the rqid Dictionary")
    else:
        tr_inst.proc_rcvd_data()


def __received_sys_msg_handler(target_inst, Msgid: int) -> None:
    """ 시스템(접속 관리 시스템)의 이벤트 처리 핸들러
    시스템 이벤트 ID : Msg
    3 : 체결통보 데이터 재조회 필요.
    7 : 통신 실패 후 재접속 성공.
    10: 시스템이 종료됨.
    11: 시스템이 시작됨.
    """
    print("System Message Received = ", Msgid)
    if Msgid == 3:
        msg = "<<< 체결통보 데이터 재조회 필요 >>>"
    elif Msgid == 7:
        msg = "<<< 통신 실패 후 재접속 성공 >>>"
    elif Msgid == 10:
        target_inst._connected = False
        msg = "<<< Indi 서버 접속 해제 >>>"
    elif Msgid == 11:
        target_inst._connected = True
        msg = "<<< Indi 서버 접속 완료 >>>"
    else:
        msg = f" 알 수 없는 에러 코드 발생 :: {Msgid} "
    print(msg), Logger.write_log(msg)


def __receive_realtime_data_handler(realtime_name: str) -> None:
    """ 등록(register)된 realtime TR의 실시간 데이터 처리 핸들러 """
    realtime_inst = TRRT.BaseRealtime.INSTANCES.get(realtime_name)
    #realtime_inst = TRRT.__dict__.get(realtime_name, None)  ### returns a RT class obj, not a RT instance.
    if realtime_inst is None:
        raise APIErrors.RealtimeNotDefinedError()
    realtime_inst.proc_rcvd_real_data() 


def __start_indi(indi_inst, id_, pw_, cert_,
                 indi_starter_path=Config.INDI_OBJ_PATH,
                 wait_sec: int = 60) -> None:
    if not indi_inst.GetCommState():
        print("It is already connected to Shinhan i-Indi server.")
    else:
        is_successful = indi_inst._StartIndi(id_, pw_, cert_, indi_starter_path)
        if not is_successful: raise APIErrors.ServerNotConnectedError("An error occurs when executing StartIndi().")

        # 접속이 성공&완료될 때까지 대기한다.
        _s = time.time()
        while not indi_inst._connected: # not indi_inst.GetCommState():
            print("Starting Indi and Connecting to it's server ...")
            pythoncom.PumpWaitingMessages()
            time.sleep(2)
            if time.time() - _s > wait_sec:
                raise TimeoutError("Time-out when trying to connect to api server.")
        del _s


def new_indi(owner='master', is_realtime: bool = False, implicitly_wait: int = 60):
    """ 신한금융투자 서버와 연결하기 위한 indi instance를 생성한다.
        TR instance 생성 시 indi instance를 등록해야만 하며, 
        해당 TR instance는 등록된 indi instance로 서버와 통신한다.
        <parameters>
        owner(object-type)      : indi instance에 이름을 부여하기 위한 변수
        is_realtime(bool:False) : 실시간(realtime) 요청 가능 여부
        implicit_wait(int:60)   : 최대 대기시간. 시간 넘기면 raise TimeOutError
    """
    inst = QAxWidget("GIEXPERTCONTROL.GiExpertControlCtrl.1")
    inst._owner: 'Strategy' = owner
    inst._is_realtime: bool = is_realtime
    inst._implicitly_wait = implicitly_wait

    # request_ID dictionary for matching rq with TR.
    inst._rqidD: Dict['rqid:int', "TR"] = {}

    # connection state :: True: connected / False: not connected
    inst._connected = not inst.GetCommState()

    # replace the internal behavior of the function StartIndi with the one having waiting mode.
    inst._StartIndi = inst.StartIndi
    setattr(inst, 'StartIndi', __start_indi)
    inst.StartIndi = partial(__start_indi, inst)

    # register data-receiving event handler.
    _register_handlers(target_inst=inst)

    return inst



'''
def set_single_data(self, index, data) -> bool:
    """요청할 Single TR 정보를 설정"""
    return self._inst.dynamicCall("SetSingleData(int, QString)", index, data)
def set_multi_data(self, row, index, data) -> bool:
    """요청할 Multi TR 정보를 설정 """
    return self._inst.dynamicCall("SetSingleData(int, int, QString)", row, index, data)
def get_query_name(self) -> str:
    """요청할 TR 명을 설정"""
    return self._inst.GetQueryName()
def set_query_name(self, tr_name) -> bool:
    """Object의 TR 명을 리턴"""
    return self._inst.dynamicCall("SetQueryName(QString)", tr_name)
def request_data(self) -> int:
    """조회 TR 요청을 실행
        0    : 실패
        이외 : 조회 ID"""
    return self._inst.RequestData()
def request_rt_reg(self, rt_name, code) -> bool:
    """리얼 데이터 요청을 실행"""
    return self._inst.dynamicCall("RequestRTReg(QString, QString)", rt_name, code)
def unrequest_rt_reg(self, rt_name, code) -> bool:
    """리얼 데이터 요청을 해제"""
    return self._inst.dynamicCall("RequestRTReg(QString, QString)", rt_name, code)
def unrequest_rt_reg_all(self) -> bool:
    """현재 등록된 모든 리얼 데이터 요청을 해제"""
    return self._inst.UnRequestRTRegAll()
def set_rq_count(self, count) -> None:
    """조회데이터 개수를 설정
        SetRQCount 메소드는 조회시 입력값 또는 결과값이 복수개인 TR에 대해서 설정한다.
        모든 TR에 대해서 설정해줄 필요는 없고 필요로하는 특정 TR을 사용할 경우 설정한다.
    """
    return self._inst.dynamicCall("SetRQCount(int)", count)
def clear_receive_buffer(self) -> None:
    """조회된 데이터를 삭제한다. 모든 실시간, 조회 데이터를 삭제함.
        컨트롤에 SetQueryName 메소드를 사용할 경우 기존의 설정된 데이터는 모두 삭제된다.
        예를 들면
        Object.SetSingleData(0, “12345”)
        Object.SetQueryName(“TR_1500”)

        이와 같이 사용할 경우 SetQueryName을 사용하기 전 데이터 설정 값들은 모두 무시된다. 또 실시간 데이터를 처리하고 있던 컨트롤일 경우 실시간 통신을 해제(UnRequestRTReg 함수를 사용한거 같은) 하게 된다.
        그러나, ClearReceiveBuffer는 현재 컨트롤에서 조회, 실시간 데이터만을 삭제한다.
    """
    return self._inst.ClearReceiveBuffer()
def self_mem_free(self, self_mem_free: bool) -> None:
    """시세 수신할 때 메모리 Leak이 발생하는 경우에 사용한다. 주로, VC++로 개발할 때 발생한다.
        Application을 개발하고 시세 수신할 때 메모리 Leak이 발생하는 경우에 사용한다.
        주로, VC++로 개발할 때 발생한다. Parameter에 TRUE를 주면 내부에서 메모리를 정리한다.
    """
    return self._inst.dynamicCall("SelfMemFree(BOOL)", self_mem_free)

def get_single_data(self, index) -> str:
    """요청한 단일 레코드 TR 결과에 대한 특정값을 리턴"""
    return self._inst.dynamicCall("GetSingleData(int)", index)
'''

