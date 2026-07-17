from pydantic import BaseModel, Field


class GemPayload(BaseModel):
    id: int
    name: str
    tags: list[str]
    description: str


class SearchResult(BaseModel):
    id: int
    name: str
    tags: list[str]
    description: str


class AskRequest(BaseModel):
    q: str = Field(min_length=3)
    limit: int = Field(default=3, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    sources: list[SearchResult]
