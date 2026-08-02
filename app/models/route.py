from datetime import date

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.models.enums import RouteStatus

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    String,
)

from app.database import Base


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    gym_id: Mapped[int] = mapped_column(
        ForeignKey("gyms.id"),
        nullable=False,
    )

    grade: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    colour: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )

    wall: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )

    setter: Mapped[str] = mapped_column(
        String(50),
        nullable=True
    )
    
    set_date: Mapped[Date] = mapped_column(
        Date,
        nullable=True
    )
    
    retired_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    
    # to describe route style. each route may have multiple styles. many-to-many relationship
    styles = relationship(
        "RouteStyleAssociation",
        back_populates="route",
        cascade="all, delete-orphan"
    )
    
    route_name: Mapped[str] = mapped_column(
    String(100),
    nullable=False,
    )
    
    status: Mapped[RouteStatus] = mapped_column(
    Enum(
        RouteStatus,
        name="route_status_enum",
        values_callable=lambda enum: [
            item.value for item in enum
        ],
    ),
    nullable=False,
    default=RouteStatus.ACTIVE,
    server_default="active",
    )

    gym = relationship("Gym", back_populates="routes")

    attempts = relationship("Attempt", back_populates="route")