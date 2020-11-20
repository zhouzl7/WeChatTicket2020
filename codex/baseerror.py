# -*- coding: utf-8 -*-
#



__author__ = "Epsirom"


class BaseError(Exception):

    def __init__(self, code, msg):
        super(BaseError, self).__init__(msg)
        self.code = code
        self.msg = msg

    def __repr__(self):
        return '[ERRCODE=%d] %s' % (self.code, self.msg)


class InputError(BaseError):

    def __init__(self, msg):
        super(InputError, self).__init__(1, msg)


class LogicError(BaseError):

    def __init__(self, msg):
        super(LogicError, self).__init__(2, msg)


class ValidateError(BaseError):

    def __init__(self, msg):
        super(ValidateError, self).__init__(3, msg)

class ActivityNotFoundError(BaseError):

    def __init__(self, msg="活动不存在"):
        super(ActivityNotFoundError, self).__init__(4, msg)

class ActivityNotPublishedError(BaseError):

    def __init__(self, msg="该活动尚未发布"):
        super(ActivityNotPublishedError, self).__init__(5, msg)

class AuthenticationError(BaseError):

    def __init__(self, msg="未登录管理员账号"):
        super(AuthenticationError, self).__init__(6, msg)

class PasswordError(BaseError):

    def __init__(self, msg="用户名或密码错误"):
        super(PasswordError, self).__init__(7, msg)

class TicketNotFoundError(BaseError):

    def __init__(self, msg="电子票不存在"):
        super(TicketNotFoundError, self).__init__(8, msg)
