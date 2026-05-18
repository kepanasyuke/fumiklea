class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class UserNotFound(AppException):
    def __init__(self):
        super().__init__(404, "Пользователь не найден")

class AttemptNotFound(AppException):
    def __init__(self):
        super().__init__(404, "Попытка не найдена")

class AccessDenied(AppException):
    def __init__(self):
        super().__init__(403, "Доступ запрещён")

class TimeExpired(AppException):
    def __init__(self):
        super().__init__(400, "Время выполнения истекло")