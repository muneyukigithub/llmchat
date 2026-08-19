class DomainException(Exception):
    """ドメイン層の基底例外クラス"""
    pass


class InvalidValueError(DomainException):
    """値オブジェクト等の事前条件違反"""
    pass


class InvalidThreadOperationError(DomainException):
    """スレッドに対する不正な操作違反"""
    pass


class ThreadNotFoundError(DomainException):
    """指定されたスレッドが存在しない"""
    pass


class SessionMismatchError(DomainException):
    """セッションIDがスレッドと一致しない"""
    pass