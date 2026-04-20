from pydantic import BaseModel, Field, field_validator
 
 
class PredictionRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="Текстовый промпт для модели",
        min_length=1,
        max_length=4096
    )
    max_tokens: int = Field(default=256, ge=1, le=2048)
 
    @field_validator("prompt")
    @classmethod
    def prompt_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Промпт не может быть пустым")
        return v
 
 
class PredictionResponse(BaseModel):
    prompt: str
    generated_text: str
    model: str
    tokens_used: int