import hashlib
import json
import re
import logging
from pathlib import Path

import httpx
from bs4 import BeautifulSoup, Tag

from app.api.schemas import GemPayload
from app.logging_config import configure_logging

_SKILL_GEMS_PAGE_URL = "https://poe2db.tw/us/Skill_Gems"
_GEMS_JSON_PATH = Path(__file__).parent.parent / "data" / "skills.json"
_WEAPON_DEFAULT_SKILLS = frozenset(
    {
        "Axe Slash",
        "Bow Shot",
        "Claw Stab",
        "Crossbow Shot",
        "Dagger Stab",
        "Flail Strike",
        "Mace Strike",
        "Punch",
        "Quarterstaff Strike",
        "Spear Stab",
        "Sword Slash",
    }
)
_SHORT_DESCRIPTION_LIMIT = 32
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

logger = logging.getLogger(__name__)


def _fetch_gems_html() -> str:
    try:
        headers = {"User-Agent": _USER_AGENT}
        resp = httpx.get(_SKILL_GEMS_PAGE_URL, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    except httpx.HTTPError as exc:
        logger.error("HTTP error fetching %s: %s", _SKILL_GEMS_PAGE_URL, exc)
        return ""


def _extract_name(gem: Tag) -> str:
    name_link = gem.select_one("div.flex-grow-1 a[href^='/us/']")
    return name_link.get_text(strip=True) if name_link else ""


def _extract_tags(gem: Tag) -> list[str]:
    return [tag.get_text(strip=True) for tag in gem.select("div.default a.GemTags")]


def _gem_slug(gem: Tag) -> str:
    link = gem.select_one("div.flex-grow-1 a[href^='/us/']")
    return link["href"].removeprefix("/us/") if link else ""


def _gem_id(slug: str) -> int:
    return int.from_bytes(hashlib.blake2b(slug.encode(), digest_size=6).digest(), "big")


def _extract_description(gem: Tag) -> str:
    body = gem.select_one("div.flex-grow-1")
    if body is None:
        return ""

    tags_div = body.select_one("div.default")
    if tags_div is None:
        return ""

    parts = [
        node.get_text() if isinstance(node, Tag) else str(node) for node in tags_div.next_siblings
    ]
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def _is_indexable_gem(name: str, description: str) -> bool:
    if name in _WEAPON_DEFAULT_SKILLS:
        return False
    if "{" in name:
        return False
    return bool(description.strip())


def _parse_gems_html(html_data: str) -> list[GemPayload]:
    soup = BeautifulSoup(html_data, "html.parser")
    gem_summary = soup.select_one("#SkillGemsSummary")
    gem_container = gem_summary.select("div.d-flex.border-top.rounded")
    best: dict[str, tuple[tuple, GemPayload]] = {}
    unlisted_defaults: set[str] = set()
    for gem_data in gem_container:
        slug = _gem_slug(gem_data)
        name = _extract_name(gem_data)
        tags = _extract_tags(gem_data)
        description = _extract_description(gem_data)
        if not _is_indexable_gem(name, description):
            continue
        if len(description) < _SHORT_DESCRIPTION_LIMIT:
            unlisted_defaults.add(name)

        rank = (len(tags), len(description), description)
        if slug not in best or rank > best[slug][0]:
            best[slug] = (
                rank,
                GemPayload(
                    id=_gem_id(slug),
                    name=name,
                    tags=tags,
                    description=description,
                ),
            )

    if unlisted_defaults:
        logger.warning("Short descriptions not in denylist: %s", sorted(unlisted_defaults))

    return sorted((payload for _, payload in best.values()), key=lambda gem: gem.name)


def _write_gems_json(gems: list[GemPayload], path: Path = _GEMS_JSON_PATH) -> None:
    with open(path, "w") as f:
        json.dump(list(map(lambda g: g.model_dump(mode="json"), gems)), f, indent=2)


if __name__ == "__main__":
    configure_logging()
    html = _fetch_gems_html()
    gems = _parse_gems_html(html)
    _write_gems_json(gems)
