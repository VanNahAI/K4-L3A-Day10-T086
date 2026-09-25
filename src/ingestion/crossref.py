from __future__ import annotations

from dataclasses import asdict, dataclass
import logging
from pathlib import Path
import re
import time
from typing import Any

import requests

from core.config import Settings
from core.utils import normalize_whitespace, read_json, write_json

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _clean_abstract(raw_abstract: str) -> str:
    """Loại bỏ các thẻ XML/HTML như <jats:p>, </jats:p>, và khoảng trắng thừa."""
    if not raw_abstract:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", raw_abstract)
    return normalize_whitespace(cleaned)


def _format_date(date_parts: list[int] | None) -> str:
    if not date_parts:
        return "2026-01-01"
    year = date_parts[0] if len(date_parts) > 0 else 2026
    month = date_parts[1] if len(date_parts) > 1 else 1
    day = date_parts[2] if len(date_parts) > 2 else 1
    return f"{year:04d}-{month:02d}-{day:02d}"


def parse_crossref_payload(payload: dict[str, Any]) -> list[PaperRecord]:
    """Parse Crossref API payload JSON thành list đối tượng PaperRecord chuẩn hóa."""
    items = payload.get("message", {}).get("items", [])
    records: list[PaperRecord] = []

    for item in items:
        paper_id = str(item.get("DOI", "")).strip()
        if not paper_id:
            continue

        raw_title = item.get("title", [])
        if isinstance(raw_title, list):
            title = " ".join(str(t) for t in raw_title if t).strip()
        else:
            title = str(raw_title).strip()
        title = normalize_whitespace(title)
        if not title:
            continue

        raw_abstract = item.get("abstract", "")
        summary = _clean_abstract(raw_abstract)

        authors: list[str] = []
        for author in item.get("author", []):
            given = author.get("given", "").strip()
            family = author.get("family", "").strip()
            full_name = f"{given} {family}".strip()
            if full_name:
                authors.append(full_name)
        if not authors:
            authors = ["Unknown Author"]

        raw_subjects = item.get("subject", [])
        if isinstance(raw_subjects, list) and raw_subjects:
            categories = [normalize_whitespace(str(s)) for s in raw_subjects if s]
        else:
            categories = ["Computer Science"]
        primary_category = categories[0] if categories else "Computer Science"

        pub_parts = item.get("published", {}).get("date-parts", [[]])[0]
        published = _format_date(pub_parts)

        upd_parts = (
            item.get("updated", {}).get("date-parts", [[]])[0]
            or item.get("created", {}).get("date-parts", [[]])[0]
            or pub_parts
        )
        updated = _format_date(upd_parts)

        abs_url = item.get("URL", f"https://doi.org/{paper_id}")
        pdf_url = abs_url
        for link in item.get("link", []):
            if isinstance(link, dict) and link.get("content-type") == "application/pdf" and link.get("URL"):
                pdf_url = link["URL"]
                break

        records.append(
            PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=abs_url,
                pdf_url=pdf_url,
                comment=f"Crossref record {paper_id}",
            )
        )

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Thu thập records từ Crossref API hoặc Fallback sang local snapshot khi offline/lỗi mạng."""
    payload: dict[str, Any] | None = None

    if settings.refresh_source:
        url = "https://api.crossref.org/works"
        params = {
            "query": settings.source_query,
            "filter": settings.source_filter,
            "rows": settings.max_results,
        }
        headers = {"User-Agent": "DataObservabilityLab/1.0 (mailto:student@lab.edu)"}

        for attempt in range(1, 4):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    payload = response.json()
                    write_json(settings.paths.raw_api_response, payload)
                    logger.info("Successfully fetched %d records from Crossref API.", len(payload.get("message", {}).get("items", [])))
                    break
                logger.warning("Attempt %d: API returned status %d. Retrying...", attempt, response.status_code)
                time.sleep(1.0)
            except Exception as exc:
                logger.warning("Attempt %d failed with error: %s", attempt, exc)
                time.sleep(1.0)

    # Nếu không bật refresh_source hoặc request thất bại, dùng file snapshot có sẵn
    if payload is None:
        if settings.paths.raw_api_response.exists():
            logger.info("Using local snapshot response at %s", settings.paths.raw_api_response)
            payload = read_json(settings.paths.raw_api_response)
        elif settings.paths.raw_records_json.exists():
            logger.info("Using local raw records snapshot at %s", settings.paths.raw_records_json)
            return load_raw_records(settings.paths.raw_records_json)
        else:
            raise FileNotFoundError(
                f"Cannot find raw source snapshot at {settings.paths.raw_api_response} or {settings.paths.raw_records_json}."
            )

    records = parse_crossref_payload(payload)
    records_payload = [asdict(r) for r in records]
    write_json(settings.paths.raw_records_json, records_payload)
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Đọc snapshot JSON và chuyển đổi thành danh sách PaperRecord."""
    data = read_json(path)
    if isinstance(data, dict) and "message" in data:
        return parse_crossref_payload(data)
    if isinstance(data, list):
        return [PaperRecord(**item) for item in data]
    raise ValueError(f"Unsupported payload format in {path}")
