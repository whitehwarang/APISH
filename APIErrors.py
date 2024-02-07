from . import Logger


class __APIError(Exception):
    def __init__(self, message=""):
        self.message = message
        Logger.write_log(message)

    def __str__(self):
        return f"An API_Error Occurs.\n" \
               f"Exception class : {self.__class__.__name__}\n" \
               f"message : {self.message}"


class SetQueryNameError(__APIError):    pass
class SetSingleDataError(__APIError):   pass
class PriceSettingError(__APIError):    pass
class RequestDataError(__APIError):     pass
class RequestRTRegError(__APIError):    pass
class OrderRequestError(__APIError):    pass
class NoAccountNumError(__APIError):    pass
class NoResponseError(__APIError):      pass
class ServerNotConnectedError(__APIError):  pass
class DisconnectTryError(__APIError):   pass
class RealtimeNotDefinedError(__APIError):  pass
class TROutputTypeError(__APIError):    pass
class RqIdNotExistError(__APIError):    pass
class TimeOutError(__APIError):         pass


