import numpy as np
from time import time
import pythoncom

from . import APIErrors, Logger

#import TelegramBot
#bot = TelegramBot.get_instance()
#channel_id = TelegramBot.get_channel_id()


class Base:
    NAME, DESCRIPTION = None, None
    IS_SINGLE_OUTPUT, IS_MULTI_OUTPUT = False, False
    REALTIME_AVAILABLE = False
    INPUT_DTYPE = None
    SINGLE_OUTPUT_DTYPE = None
    MULTI_OUTPUT_DTYPE = None
    INSTANCES = {}

    def __init__(self, indi_instance):
        self._indi_instance = indi_instance
        self._initialize_base()
        self.INSTANCES[self.NAME] = self

    def _initialize_base(self):
        if self.IS_SINGLE_OUTPUT:
            self.single_output: np.ndarray = np.empty([1], dtype=self.SINGLE_OUTPUT_DTYPE)
        if self.IS_MULTI_OUTPUT:
            self.multi_output: np.ndarray = np.empty([1], dtype=self.MULTI_OUTPUT_DTYPE)        


class BaseTR(Base):
    """
    TR Base class.
    각 TR의 class는 본 class를 상속받아 Override로 작성
    Override할 variables : class variables
    Override할 methods : _set_input_data()
    """

    def __init__(self, indi_instance, implicit_wait: int = 3, *args, **kwargs):
        super().__init__(indi_instance, *args, **kwargs)
        self.is_waiting: bool = False
        self.implicit_wait: int = implicit_wait
        self._initialize_tr_inst()

    def _initialize_tr_inst(self):

        if self.IS_SINGLE_OUTPUT:
            if self.IS_MULTI_OUTPUT:
                self.proc_rcvd_data = self._proc_rcvd_single_multi_data
            else:
                self.proc_rcvd_data = self._proc_rcvd_single_data
        else:
            if self.IS_MULTI_OUTPUT:
                self.proc_rcvd_data = self._proc_rcvd_multi_data
            else:
                raise APIErrors.TRCreationError(
                    f"{self.__class__.__name__} : Both IS_SINGLE_OUTPUT and IS_MULTI_OUTPUT are Falses")

    def _proc_rcvd_single_data(self) -> None:
        self._get_rcvd_single_data()
        self.is_waiting = False

    def _proc_rcvd_multi_data(self) -> None:
        self._get_rcvd_multi_data()
        self.is_waiting = False

    def _proc_rcvd_single_multi_data(self) -> None:
        self._get_rcvd_single_data()
        self._get_rcvd_multi_data()
        self.is_waiting = False

    def _get_rcvd_single_data(self) -> None:
        """
        싱글데이터(single_data)를 수신(received)한 경우의 처리 루틴
        :param indi_inst: tr_instance
        :return:    None
        """
        for j in range(len(self.SINGLE_OUTPUT_DTYPE)):
            self.single_output[0][j] = self._indi_instance.dynamicCall("GetSingleData(int)", j)
        return

    def _get_rcvd_multi_data(self) -> None:
        """
        멀티데이터(multi_data)를 수신(Received)한 경우의 처리 루틴
        :param indi_inst:
        :return:
        """
        nCnt = self._indi_instance.dynamicCall("GetMultiRowCount()")
        if self.multi_output.shape[0] != nCnt:
            del self.multi_output
            self.multi_output = np.empty([nCnt], dtype=self.MULTI_OUTPUT_DTYPE)
        for i in range(nCnt):
            for j in range(len(self.MULTI_OUTPUT_DTYPE)):
                self.multi_output[i][j] = self._indi_instance.dynamicCall("GetMultiData(int, int)", i, j)
        self.multi_output = self.multi_output[::-1]
        return

    def rq_data(self, *args, **kwargs):
        """
        데이터를 요청한다.

        """
        #self._pre_rq_func()
        #self._set_input_data(*args, **kwargs)
        #rqid = self._indi_instance.dynamicCall("RequestData()")
        #self._post_rq_func(rqid)
        #return self._get_output_data()
        try:
            self._pre_rq_func()
            self._set_input_data(*args, **kwargs)
            rqid = self._indi_instance.dynamicCall("RequestData()")
            self._post_rq_func(rqid)
            return self._get_output_data()
        except APIErrors.TimeOutError as toe:
            print(toe)
            self._pre_rq_func()
            self._set_input_data(*args, **kwargs)
            rqid = self._indi_instance.dynamicCall("RequestData()")
            self._post_rq_func(rqid)
            return self._get_output_data()

    def _pre_rq_func(self) -> int:
        """
        쿼리를 준비한다.
        :param indi_inst: TR_instance
        :return: (bool) is_ok
        """
        ok = self._indi_instance.dynamicCall("SetQueryName(QString)", self.NAME)
        if not ok: raise APIErrors.SetQueryNameError(self.__class__.__name__)
        self.is_waiting = True
        return ok

    def _set_input_data(self, *args, **kwargs) -> None:
        """ request_data(데이터 요청)에서의 args, kwargs에 대해 처리.
        *args 및 **kwargs의 처리가 필요한 경우 Override하여 사용한다."""
        if args:
            inst = self._indi_instance
            for i, arg in enumerate(args):
                inst.dynamicCall("SetSingleData(int, QString)", i, str(arg))
        elif kwargs:
            self._set_input_data(*list(kwargs.values()))
        else:
            pass

    def _post_rq_func(self, rqid) -> None:
        self._indi_instance._rqidD[rqid] = self

        s = time()
        while self.is_waiting:
            pythoncom.PumpWaitingMessages()

            # implicit_wait 초 이상 응답 안오면 에러로 간주
            if time() - s > self.implicit_wait:
                self.is_waiting = False
                errstr = f'A TimeOutError has occured. rqid : {rqid} str_name: {self._indi_instance._owner} tr_name: {self.NAME}'
                Logger.write_log(errstr)
                #bot.sendMessage(chat_id=channel_id, text=errstr)
                raise APIErrors.TimeOutError("Time Out!!!")


    def _get_output_data(self):
        if self.IS_SINGLE_OUTPUT:
            if self.IS_MULTI_OUTPUT:
                return self.single_output, self.multi_output
            else:
                return self.single_output
        else:
            if self.IS_MULTI_OUTPUT:
                return self.multi_output
            else:
                raise APIErrors.TROutputTypeError(
                    f"{self.__class__.__name__} : Both IS_SINGLE_OUTPUT and IS_MULTI_OUTPUT are Falses")


class BaseRealtime(Base):
    """
    Realtime Base class.
    각 Realtime의 class는 본 class를 상속받아 Override로 작성
    Override할 variables : class variables
    Override할 methods : request_data()
    """
    REALTIME_AVAILABLE = True

    def __init__(self, indi_instance, *args, **kwargs):
        #assert indi_instance._is_realtime
        super().__init__(indi_instance, *args, **kwargs)
        self._registered = False
        self._initialize_rt_inst()

    def _initialize_rt_inst(self):
        if self.IS_SINGLE_OUTPUT:
            if self.IS_MULTI_OUTPUT:
                self.proc_rcvd_real_data = self._proc_rcvd_single_multi_real_data
            else:
                self.proc_rcvd_real_data = self._proc_rcvd_single_real_data
        else:
            if self.IS_MULTI_OUTPUT:
                self.proc_rcvd_real_data = self._proc_rcvd_multi_real_data
            else:
                raise APIErrors.TRCreationError(
                    f"{self.__class__.__name__} : Both IS_SINGLE_OUTPUT and IS_MULTI_OUTPUT are Falses")

    def _proc_rcvd_single_real_data(self) -> None:
        self._get_rcvd_single_real_data()

    def _proc_rcvd_multi_real_data(self) -> None:
        self._get_rcvd_multi_real_data()

    def _proc_rcvd_single_multi_real_data(self) -> None:
        self._get_rcvd_single_real_data()
        self._get_rcvd_multi_real_data()

    def _get_rcvd_single_real_data(self) -> None:
        """
        싱글데이터(single_data)를 수신(received)한 경우의 처리 루틴
        :param indi_inst: tr_instance
        :return:    None
        """
        for j in range(len(self.SINGLE_OUTPUT_DTYPE)):
            self.single_output[0][j] = self._indi_instance.dynamicCall("GetSingleData(int)", j)
        return

    def _get_rcvd_multi_real_data(self) -> None:
        """
        멀티데이터(multi_data)를 수신(Received)한 경우의 처리 루틴
        :param indi_inst:
        :return:
        """
        nCnt = self._indi_instance.dynamicCall("GetMultiRowCount()")
        if self.multi_output.shape[0] != nCnt:
            del self.multi_output
            self.multi_output = np.empty([nCnt], dtype=self.MULTI_OUTPUT_DTYPE)
        for i in range(nCnt):
            for j in range(len(self.MULTI_OUTPUT_DTYPE)):
                self.multi_output[i][j] = self._indi_instance.dynamicCall("GetMultiData(int, int)", i, j)
        self.multi_output = self.multi_output[::-1]
        return

    def reg_realtime(self, code: str) -> bool:
        """
        realtime을 등록한다.
        :param realtime_name:    realtime_symbol
        :return if 등록성공 시, True
                   등록실패 시, False
        """
        if self.REALTIME_AVAILABLE:
            ok = self._indi_instance.dynamicCall("RequestRTReg(QString, QString)", self.NAME, code)
            self._registered = True if ok else self._registered
            return ok
        return False

    def unreg_realtime(self, code: str) -> bool:
        """
        realtime의 등록을 해지한다.
        :param Real_inst: realtime_instance
        """
        if self.REALTIME_AVAILABLE:
            ok = self._indi_instance.dynamicCall("UnRequestRTReg(QString, QString)", self.NAME, code)
            self._registered = False if ok else self._registered
            return ok
        return False

    def unreg_realtime_all(self) -> bool:
        """
        모든 realtime의 등록을 해지한다.
        """
        if self.REALTIME_AVAILABLE:
            ok = self._indi_instance.UnRequestRTRegAll()
            self._registered = False if ok else self._registered
            return ok
        return False

# unit test
if __name__ == "__main__":
    pass
