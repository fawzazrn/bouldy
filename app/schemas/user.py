from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRole


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


class MeResponse(UserResponse):
    """The signed-in user, including what they are allowed to administer."""

    role: UserRole
    admin_gym_ids: list[int]


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    admin_gym_ids: list[int]

    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(BaseModel):
    role: UserRole
