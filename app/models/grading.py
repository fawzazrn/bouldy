from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GradeScale(Base):
    """A fixed, ordered list of grades that one or more gym brands share."""

    __tablename__ = "grade_scales"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # "numeric" (1 to 15) or "colour_tier" (Camp 5). Stored as text on purpose,
    # so adding a kind later does not need a Postgres enum migration.
    kind: Mapped[str] = mapped_column(String(30), nullable=False)

    # Bump when grades are added or reordered, so old sends stay interpretable.
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )

    grades = relationship(
        "Grade",
        back_populates="scale",
        order_by="Grade.order",
        cascade="all, delete-orphan",
    )
    brands = relationship("GymBrand", back_populates="grade_scale")


class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (
        UniqueConstraint("scale_id", "label", name="uq_grades_scale_label"),
        UniqueConstraint("scale_id", "order", name="uq_grades_scale_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    scale_id: Mapped[int] = mapped_column(
        ForeignKey("grade_scales.id", ondelete="CASCADE"),
        nullable=False,
    )

    # What the climber sees: "7", "Yellow". At most 10 characters, because it
    # is copied into the legacy routes.grade column.
    label: Mapped[str] = mapped_column(String(10), nullable=False)

    # Difficulty position within the scale, 1 = easiest.
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    colour_hex: Mapped[str | None] = mapped_column(String(7), nullable=True)

    # Reference text only. Camp 5 tiers overlap in V-scale, so these are
    # never used for ordering or arithmetic.
    v_range_label: Mapped[str | None] = mapped_column(String(30), nullable=True)
    font_range_label: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )
    description: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # beginner / intermediate / advanced / expert. Null when not decided.
    band: Mapped[str | None] = mapped_column(String(20), nullable=True)

    scale = relationship("GradeScale", back_populates="grades")


class GymBrand(Base):
    __tablename__ = "gym_brands"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    grade_scale_id: Mapped[int] = mapped_column(
        ForeignKey("grade_scales.id"),
        nullable=False,
    )

    grade_scale = relationship("GradeScale", back_populates="brands")
    gyms = relationship("Gym", back_populates="brand")
    route_kinds = relationship(
        "BrandRouteKind",
        back_populates="brand",
        cascade="all, delete-orphan",
    )

    @property
    def allowed_route_kinds(self) -> list[str]:
        return [item.route_kind for item in self.route_kinds]


class BrandRouteKind(Base):
    """A special route type a brand uses (wildcard, signature send, ...)."""

    __tablename__ = "brand_route_kinds"

    brand_id: Mapped[int] = mapped_column(
        ForeignKey("gym_brands.id", ondelete="CASCADE"),
        primary_key=True,
    )
    route_kind: Mapped[str] = mapped_column(String(30), primary_key=True)

    brand = relationship("GymBrand", back_populates="route_kinds")
