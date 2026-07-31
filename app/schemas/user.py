from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    current_grade: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    current_grade: str | None = None


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)