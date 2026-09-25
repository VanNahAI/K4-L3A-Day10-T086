from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import write_json


def build_test_set(df: pd.DataFrame, output_path: Path | str) -> list[dict[str, Any]]:
    """Build a standardized benchmark evaluation test set of 10 questions across 4 categories:

    - summary (3 questions)
    - authors (3 questions)
    - date (2 questions)
    - categories (2 questions)
    """
    if len(df) < 4:
        raise ValueError("DataFrame must contain at least 4 documents to build the test set.")

    # Sort or pick rows to ensure deterministic test set generation
    records = df.to_dict(orient="records")
    n_records = len(records)

    def get_authors_str(row: dict[str, Any]) -> str:
        if "authors_joined" in row and row["authors_joined"]:
            return str(row["authors_joined"])
        authors = row.get("authors", [])
        if isinstance(authors, list):
            return ", ".join(str(a) for a in authors)
        return str(authors)

    def get_categories_str(row: dict[str, Any]) -> str:
        if "categories_joined" in row and row["categories_joined"]:
            return str(row["categories_joined"])
        categories = row.get("categories", [])
        if isinstance(categories, list):
            return ", ".join(str(c) for c in categories)
        return str(categories)

    def get_first_sentence(text: str) -> str:
        text = str(text).strip()
        if not text:
            return ""
        parts = text.split(".")
        first_part = parts[0].strip()
        return f"{first_part}." if first_part else text

    # Question distribution plan: 3 summary, 3 authors, 2 date, 2 categories
    plan = [
        ("summary", 0),
        ("summary", 1),
        ("summary", 2),
        ("authors", 3 % n_records),
        ("authors", 4 % n_records),
        ("authors", 5 % n_records),
        ("date", 6 % n_records),
        ("date", 7 % n_records),
        ("categories", 8 % n_records),
        ("categories", 9 % n_records),
    ]

    test_set: list[dict[str, Any]] = []
    for idx, (q_type, row_idx) in enumerate(plan, start=1):
        row = records[row_idx]
        paper_id = str(row.get("paper_id", ""))
        title = str(row.get("title", ""))

        if q_type == "summary":
            question = f"What is the summary of the paper '{title}'?"
            ground_truth = get_first_sentence(str(row.get("summary", "")))
        elif q_type == "authors":
            question = f"Who authored the paper '{title}'?"
            ground_truth = get_authors_str(row)
        elif q_type == "date":
            question = f"When was the paper '{title}' published?"
            ground_truth = str(row.get("published", ""))
        elif q_type == "categories":
            question = f"What categories does the paper '{title}' belong to?"
            ground_truth = get_categories_str(row)
        else:
            question = f"What is the summary of the paper '{title}'?"
            ground_truth = str(row.get("summary", ""))

        test_set.append(
            {
                "id": f"eval_{idx:03d}",
                "question_type": q_type,
                "question": question,
                "ground_truth": ground_truth,
                "ground_truth_doc_ids": [paper_id],
            }
        )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_file, test_set)

    return test_set

