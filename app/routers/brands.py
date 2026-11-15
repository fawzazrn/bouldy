from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.grading import get_brand, get_brands
from app.database import get_db
from app.schemas.grading import GymBrandDetailResponse, GymBrandResponse

router = APIRouter(
    prefix="/brands",
    tags=["Brands"],
)


@router.get(
    "/",
    response_model=list[GymBrandResponse],
)
def read_brands(
    db: Session = Depends(get_db),
):
    return get_brands(db)


@router.get(
    "/{brand_id}",
    response_model=GymBrandDetailResponse,
)
def read_brand(
    brand_id: int,
    db: Session = Depends(get_db),
):
    brand = get_brand(db, brand_id)

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    return brand
