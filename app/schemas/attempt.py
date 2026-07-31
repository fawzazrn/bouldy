from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import AttemptResult


class AttemptBase(BaseModel):
    session_id: int
    route_id: int
    num_attempts: int
    result: AttemptResult
    notes: str | None = None


class AttemptCreate(BaseModel):
    route_id: int
    num_attempts: int = Field(ge=1)
    result: AttemptResult = AttemptResult.PROJECT
    notes: str | None = None
    
    # to restrict Flash attempts to only 1 attempt
    @model_validator(mode="after")
    def validate_flash(self):
        if (
            self.result == AttemptResult.FLASH
            and self.num_attempts != 1
        ):
            raise ValueError(
                "Flash must have exactly 1 attempt"
            )

        return self


class AttemptUpdate(BaseModel):
    num_attempts: int | None = Field(
        default=None,
        ge=1,
    )
    result: AttemptResult | None = None
    notes: str | None = None


class AttemptResponse(BaseModel):
    id: int
    session_id: int
    route_id: int
    num_attempts: int
    result: AttemptResult
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)