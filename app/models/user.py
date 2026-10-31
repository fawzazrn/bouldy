from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False)

    current_grade: Mapped[str] = mapped_column(
        String(10),
        nullable=True
    )

    # user, gym_admin or super_admin. Stored as text so a new role later does
    # not need a Postgres enum migration. Only a super admin can change it.
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.USER.value,
        server_default=UserRole.USER.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    sessions = relationship("Session", back_populates="user")

    gym_admin_links = relationship(
        "UserGymAdmin",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def admin_gym_ids(self) -> list[int]:
        """Gyms this user may manage when their role is gym_admin."""
        return sorted(link.gym_id for link in self.gym_admin_links)


class UserGymAdmin(Base):
    """Links a gym admin to one gym (a location) they are allowed to edit."""

    __tablename__ = "user_gym_admins"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    gym_id: Mapped[int] = mapped_column(
        ForeignKey("gyms.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user = relationship("User", back_populates="gym_admin_links")
