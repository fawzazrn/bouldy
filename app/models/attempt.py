from sqlalchemy import ForeignKey, Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id")
    )

    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id")
    )

    num_attempts: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    result: Mapped[str] = mapped_column(
        String(20)
    )

    notes: Mapped[str | None]

    session = relationship(
        "Session",
        back_populates="attempts"
    )

    route = relationship(
        "Route",
        back_populates="attempts"
    )