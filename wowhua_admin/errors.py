#!usr/bin/env python
# -*- coding: utf-8 -*-


class AdminOperationalError(BaseException):
    pass


class TicketSwapError(AdminOperationalError):
    pass


class ResultingError(AdminOperationalError):
    pass
