from datetime import date

from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    gym_id: Mapped[int] = mapped_column(
        ForeignKey("gyms.id")
    )

    session_date: Mapped[date] = mapped_column(Date)

    duration_minutes: Mapped[int]

    notes: Mapped[str | None]

    user = relationship("User", back_populates="sessions")

    gym = relationship("Gym", back_populates="sessions")

    attempts = relationship(
        "Attempt",
        back_populates="session"
    )