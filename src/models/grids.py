from pydantic import BaseModel, Field


class Grid(BaseModel):
    id: int = Field(ge=0, default=0)

    def to_str(self) -> str:
        return f"The ID of a grid is: {str(self.id)}"
