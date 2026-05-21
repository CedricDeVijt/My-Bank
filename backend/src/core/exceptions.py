class EmailAlreadyRegisteredError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class RefreshTokenError(Exception):
    pass


# Transaction-related exceptions
class TransactionError(Exception):
    """Base class for transaction errors"""

    pass


class AccountNotFoundError(TransactionError):
    """Raised when an account doesn't exist"""

    pass


class InsufficientBalanceError(TransactionError):
    """Raised when an account doesn't have enough balance"""

    pass


class InvalidAccountStatusError(TransactionError):
    """Raised when an account is not in active status"""

    pass


class InvalidTransactionError(TransactionError):
    """Raised for invalid transaction details (e.g., same account, zero amount)"""

    pass


class CurrencyMismatchError(TransactionError):
    """Raised when accounts have different currencies"""

    pass
