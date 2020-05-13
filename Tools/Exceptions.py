class ParseException(Exception):
    pass


class NotAMethodException(ParseException):
    pass


class NotAFieldException(ParseException):
    pass


class NotAPropertyException(ParseException):
    pass


class MissingQuoteException(ParseException):
    pass


class MissingBracketException(ParseException):
    pass


class WrongExpressionException(ParseException):
    pass
