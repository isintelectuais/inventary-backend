from ninja.errors import HttpError

class ArmazemNotFound(HttpError):
    def __init__(self):
        super().__init__(status_code=404, message="Armazém não encontrado")

class DuplicateArmazemCode(HttpError):
    def __init__(self):
        super().__init__(status_code=400, message="Código de armazém já existe")

class InvalidArmazemData(HttpError):
    def __init__(self, message):
        super().__init__(status_code=422, message=message)

class PermissionDenied(HttpError):
    def __init__(self, message="Acesso não autorizado"):
        super().__init__(status_code=403, message=message)