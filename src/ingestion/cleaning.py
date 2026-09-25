from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import re

import pandas as pd

from core.utils import compact_join, normalize_whitespace
from ingestion.crossref import PaperRecord


def _format_text_for_embedding(row: dict | pd.Series) -> str:
    """Tạo cấu trúc 5 phần chuẩn cho văn bản nhúng vector."""
    return (
        f"Title: {row['title']}\n"
        f"Authors: {row['authors_joined']}\n"
        f"Published: {row['published']}\n"
        f"Categories: {row['categories_joined']}\n"
        f"Summary: {row['summary']}"
    )


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Làm sạch raw records thành DataFrame chuẩn hóa sẵn sàng để embed và kiểm định chất lượng."""
    if not records:
        return pd.DataFrame()

    rows: list[dict] = [asdict(r) for r in records]
    df = pd.DataFrame(rows)

    # 1. Khử trùng lặp theo paper_id (giữ bản ghi đầu tiên)
    df = df.drop_duplicates(subset=["paper_id"]).copy()

    # 2. Chuẩn hóa các trường text
    df["title"] = df["title"].astype(str).apply(normalize_whitespace)
    df["summary"] = df["summary"].astype(str).apply(normalize_whitespace)
    df["primary_category"] = df["primary_category"].astype(str).apply(normalize_whitespace)

    # 3. Tạo các cột helper
    df["authors_joined"] = df["authors"].apply(
        lambda a: compact_join(a) if isinstance(a, list) else str(a)
    )
    df["categories_joined"] = df["categories"].apply(
        lambda c: compact_join(c) if isinstance(c, list) else str(c)
    )
    df["summary_chars"] = df["summary"].apply(len)

    # 4. Tính toán age_days
    ref_date = run_date.date() if isinstance(run_date, datetime) else run_date

    def _calc_age(pub_str: str) -> int:
        try:
            pub_date = datetime.fromisoformat(str(pub_str)[:10]).date()
            return max(0, (ref_date - pub_date).days)
        except Exception:
            return 0

    df["age_days"] = df["published"].apply(_calc_age)

    # 5. Tạo trường text_for_embedding
    df["text_for_embedding"] = df.apply(_format_text_for_embedding, axis=1)

    # 6. Lọc bỏ các dòng không hợp lệ
    df = df[df["title"].str.strip().str.len() > 0]
    df = df[df["summary_chars"] >= 10]

    # 7. Sắp xếp theo ngày xuất bản giảm dần
    df = df.sort_values(by="published", ascending=False).reset_index(drop=True)

    return df
