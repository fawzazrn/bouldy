from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Gym(Base):
    __tablename__ = "gyms"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True
    )

    location: Mapped[str] = mapped_column(
        String(200)
    )

    routes = relationship("Route", back_populates="gym")
    sessions = relationship("Session", back_populates="gym")