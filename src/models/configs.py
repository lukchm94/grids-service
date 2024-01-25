from pydantic import BaseModel, Field


class Config(BaseModel):
    id: int = Field(ge=0, default=0)

    def to_str(self) -> str:
        return f"The ID of a config is: {str(self.id)}"
