from pydantic import BaseModel

class Error400(BaseModel):
    status: str = "failure"
    message: str = "Bad request"
    code: int = 400

class Error401(BaseModel):
    status: str = "failure"
    message: str = "Invalid token or Authorization"
    code: int = 401

class Error404(BaseModel):
    status: str = "failure"
    message: str = "Not found"
    code: int = 404

class Error500(BaseModel):
    status: str = "failure"
    message: str = "Internal server error"
    code: int = 500

