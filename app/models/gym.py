from sqlalchemy import Boolean, Float, ForeignKey, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Gym(Base):
    """One physical gym location. Locations of a chain share a GymBrand."""

    __tablename__ = "gyms"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True
    )

    location: Mapped[str] = mapped_column(
        String(200)
    )

    # Everything below is optional so existing gyms and clients keep working.
    brand_id: Mapped[int | None] = mapped_column(
        ForeignKey("gym_brands.id"),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    opening_hours: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    brand = relationship("GymBrand", back_populates="gyms")
    routes = relationship("Route", back_populates="gym")
    sessions = relationship("Session", back_populates="gym")
