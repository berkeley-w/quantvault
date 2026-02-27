from fastapi import HTTPException


class NotFoundError(HTTPException):
    def __init__(self, entity: str, id: int | str):
        super().__init__(status_code=404, detail=f"{entity} with id {id} not found")


class ValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)


class ConflictError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=409, detail=message)

