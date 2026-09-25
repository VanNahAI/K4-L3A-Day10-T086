from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import write_json


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path: Path | str) -> pd.DataFrame:
    """Giả lập 6 dạng data corruption thường gặp trong thực tế.

    1. Drop latest records: Bỏ rơi 20% bản ghi mới nhất.
    2. Blank summary: Xóa rỗng trường tóm tắt.
    3. Inject noise: Chèn chuỗi rác vô nghĩa vào tóm tắt.
    4. Truncate title: Cắt ngắn tiêu đề xuống < 8 ký tự.
    5. Stale date: Lùi ngày xuất bản về 365 ngày trước (vi phạm Freshness SLA).
    6. Duplicate rows: Nhân đôi bản ghi (vi phạm tính duy nhất của paper_id).
    """
    if df.empty:
        write_json(Path(output_log_path), {"error": "Empty dataframe provided"})
        return df

    corrupted = df.copy().reset_index(drop=True)
    total_original = len(corrupted)
    logs: list[dict[str, Any]] = []

    # 1. Drop latest records (20% bản ghi mới nhất)
    drop_count = max(1, int(len(corrupted) * 0.20))
    dropped_ids = corrupted.iloc[:drop_count]["paper_id"].tolist()
    corrupted = corrupted.iloc[drop_count:].copy().reset_index(drop=True)
    logs.append(
        {
            "corruption_type": "drop_latest_records",
            "description": f"Dropped {drop_count} newest records (~20%)",
            "count": drop_count,
            "affected_paper_ids": dropped_ids,
        }
    )

    # 2. Blank summary (xóa rỗng 2 dòng đầu tiên còn lại)
    blank_indices = [0, 1] if len(corrupted) >= 2 else [0]
    blank_ids = corrupted.iloc[blank_indices]["paper_id"].tolist()
    for idx in blank_indices:
        corrupted.at[idx, "summary"] = ""
        corrupted.at[idx, "summary_chars"] = 0
    logs.append(
        {
            "corruption_type": "blank_summary",
            "description": f"Set summary to empty string for {len(blank_indices)} records",
            "count": len(blank_indices),
            "affected_paper_ids": blank_ids,
        }
    )

    # 3. Inject noise (chèn ký tự rác vào 2 dòng tiếp theo)
    noise_indices = [2, 3] if len(corrupted) >= 4 else []
    noise_ids = corrupted.iloc[noise_indices]["paper_id"].tolist()
    noise_text = " [CORRUPTED_NOISE: %$#@! NULL_POINTER_EXCEPTION 0xDEADBEEF MEMORY_LEAK] "
    for idx in noise_indices:
        current_summary = str(corrupted.at[idx, "summary"])
        corrupted.at[idx, "summary"] = current_summary + noise_text
        corrupted.at[idx, "summary_chars"] = len(corrupted.at[idx, "summary"])
    logs.append(
        {
            "corruption_type": "inject_noise",
            "description": f"Injected random noise string into summary for {len(noise_indices)} records",
            "count": len(noise_indices),
            "affected_paper_ids": noise_ids,
        }
    )

    # 4. Truncate title (cắt ngắn tiêu đề xuống < 8 ký tự cho 2 dòng tiếp theo)
    trunc_indices = [4, 5] if len(corrupted) >= 6 else []
    trunc_ids = corrupted.iloc[trunc_indices]["paper_id"].tolist()
    for idx in trunc_indices:
        current_title = str(corrupted.at[idx, "title"])
        corrupted.at[idx, "title"] = current_title[:6].strip() or "Paper"
    logs.append(
        {
            "corruption_type": "truncate_title",
            "description": f"Truncated title length to < 8 chars for {len(trunc_indices)} records",
            "count": len(trunc_indices),
            "affected_paper_ids": trunc_ids,
        }
    )

    # 5. Stale date (lùi ngày xuất bản về 365 ngày trước cho ~35% bản ghi)
    stale_count = max(2, int(len(corrupted) * 0.35))
    stale_indices = list(range(6, min(6 + stale_count, len(corrupted))))
    stale_ids = corrupted.iloc[stale_indices]["paper_id"].tolist()
    for idx in stale_indices:
        try:
            pub_date = datetime.fromisoformat(str(corrupted.at[idx, "published"])[:10])
            stale_pub = pub_date - timedelta(days=365)
            corrupted.at[idx, "published"] = stale_pub.strftime("%Y-%m-%d")
            corrupted.at[idx, "age_days"] = int(corrupted.at[idx, "age_days"]) + 365
        except Exception:
            corrupted.at[idx, "published"] = "2024-01-01"
            corrupted.at[idx, "age_days"] = 600
    logs.append(
        {
            "corruption_type": "stale_date",
            "description": f"Pushed published date back 365 days for {len(stale_indices)} records to trigger Freshness SLA violation",
            "count": len(stale_indices),
            "affected_paper_ids": stale_ids,
        }
    )

    # 6. Duplicate rows (nhân bản 2-3 dòng bất kỳ vào cuối dataframe)
    dup_rows = corrupted.iloc[0:2].copy()
    dup_ids = dup_rows["paper_id"].tolist()
    corrupted = pd.concat([corrupted, dup_rows], ignore_index=True)
    logs.append(
        {
            "corruption_type": "duplicate_rows",
            "description": f"Duplicated {len(dup_rows)} records to trigger GX paper_id uniqueness violation",
            "count": len(dup_rows),
            "affected_paper_ids": dup_ids,
        }
    )

    # Rebuild text_for_embedding trên toàn bộ DataFrame đã bị làm bẩn
    def _rebuild_text(row: pd.Series) -> str:
        return (
            f"Title: {row['title']}\n"
            f"Authors: {row['authors_joined']}\n"
            f"Published: {row['published']}\n"
            f"Categories: {row['categories_joined']}\n"
            f"Summary: {row['summary']}"
        )

    corrupted["text_for_embedding"] = corrupted.apply(_rebuild_text, axis=1)

    log_payload = {
        "timestamp": datetime.now().isoformat(),
        "total_original_records": total_original,
        "total_corrupted_records": len(corrupted),
        "corruptions_count": len(logs),
        "corruptions": logs,
    }
    write_json(Path(output_log_path), log_payload)

    return corrupted
