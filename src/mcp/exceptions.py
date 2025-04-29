from fastapi import HTTPException, status

class ModelNotSupportedException(HTTPException):
    def __init__(self, model: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model {model} not supported"
        )

class NoUserMessageException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user message found"
        )