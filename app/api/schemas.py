from pydantic import BaseModel


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
