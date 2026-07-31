from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import RouteStyle


class RouteStyleAssociation(Base):
    __tablename__ = "route_style_association"

    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"),
        primary_key=True,
    )

    style: Mapped[RouteStyle] = mapped_column(
        Enum(
            RouteStyle,
            name="routestyle",
            values_callable=lambda enum: [
                item.value for item in enum
            ],
        ),
        primary_key=True,
    )

    route = relationship(
        "Route",
        back_populates="styles",
    )