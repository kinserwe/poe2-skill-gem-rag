from google import genai
from google.genai import types

from app.api.schemas import SearchResult, AskResponse
from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def build_prompt(query: str, results: list[SearchResult]) -> str:
    context = "\n\n".join(f"{r.name}: {r.description}" for r in results)
    return f"""You are a Path of Exile 2 game assistant. Answer the player's question \
using only the skill gems listed below.

Write as if answering from your own knowledge of the game. Never mention the list, \
the search, or how you were given this information. Do not use phrases like \
"based on the context", "the context provided", "listed here", or "in the data". \
Reply in plain prose. Do not use markdown, bullet points, asterisks, or headings.

If no listed gem answers the question, say plainly that you don't know of a matching \
skill gem, without explaining why.

Skill gems:
{context}

Question: {query}
"""


async def generate_answer(query: str, results: list[SearchResult]) -> AskResponse:
    prompt = build_prompt(query, results)
    answer = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW)
        ),
    )
    text = answer.text or "No answer could be generated for this question."
    return AskResponse(answer=text, sources=results)
