from google import genai
from google.genai import types

from app.api.schemas import SearchResult, AskResponse
from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def build_prompt(query: str, results: list[SearchResult]) -> str:
    context = "\n\n".join(f"{r.name}: {r.description}" for r in results)
    return f"""You are a Path of Exile 2 game assistant.    
Answer the question using only context below. \
If the answer isn't in the context say so explicitly.
        
Context:
{context}
        
Question: {query}
"""


async def generate_answer(query: str, results: list[SearchResult]) -> AskResponse:
    prompt = build_prompt(query, results)
    answer = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0)),
    )
    text = answer.text or "No answer could be generated for this question."
    return AskResponse(answer=text, sources=results)
