from fastapi import HTTPException, status


class AppError(Exception):
    def __init__(self, message: str, code: str = "app_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppError):
    pass


class ValidationError(AppError):
    pass


def not_found(entity: str, entity_id: int | str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity} {entity_id} not found",
    )
