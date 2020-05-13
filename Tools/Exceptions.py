class WrongExtensionException(Exception):
    def __str__(self):
        return 'Wrong extension. Must be: .cs, .csproj, .sln.'


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
