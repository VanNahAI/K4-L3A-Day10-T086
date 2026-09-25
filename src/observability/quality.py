from __future__ import annotations

from pathlib import Path
from typing import Any
import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd

from core.config import Settings
from core.utils import write_json


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Run automated data quality checks on DataFrame using Great Expectations 1.x Ephemeral mode.

    Expectations:
    1. Row count between 5 and 5000.
    2. paper_id, title, text_for_embedding must not be null.
    3. paper_id must be unique.
    4. summary length must be >= 30 characters.
    """
    context = gx.get_context(mode="ephemeral")
    data_source = context.data_sources.add_pandas(name=f"papers_source_{report_name}")
    data_asset = data_source.add_dataframe_asset(name=f"papers_asset_{report_name}")
    batch_def = data_asset.add_batch_definition_whole_dataframe(f"papers_batch_{report_name}")

    suite_name = f"papers_suite_{report_name}"
    suite = context.suites.add(gx.ExpectationSuite(name=suite_name))

    # 1. Row count check
    suite.add_expectation(gxe.ExpectTableRowCountToBeBetween(min_value=5, max_value=5000))

    # 2. Not null checks
    for col in ["paper_id", "title", "text_for_embedding"]:
        if col in df.columns:
            suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column=col))

    # 3. Unique check on paper_id
    if "paper_id" in df.columns:
        suite.add_expectation(gxe.ExpectColumnValuesToBeUnique(column="paper_id"))

    # 4. Summary length check (>= 30 chars)
    if "summary" in df.columns:
        suite.add_expectation(gxe.ExpectColumnValueLengthsToBeBetween(column="summary", min_value=30))

    val_def = context.validation_definitions.add(
        gx.ValidationDefinition(name=f"papers_val_{report_name}", data=batch_def, suite=suite)
    )

    validation_result = val_def.run(batch_parameters={"dataframe": df})

    results = validation_result.results
    total_expectations = len(results)
    successful_expectations = sum(1 for r in results if r.success)

    failed_expectations: list[dict[str, Any]] = []
    for r in results:
        if not r.success:
            exp_type = getattr(r.expectation_config, "type", str(r.expectation_config))
            kwargs = getattr(r.expectation_config, "kwargs", {})
            failed_expectations.append(
                {
                    "expectation_type": exp_type,
                    "kwargs": kwargs,
                    "success": False,
                }
            )

    payload = {
        "report_name": report_name,
        "success": bool(validation_result.success),
        "total_expectations": int(total_expectations),
        "successful_expectations": int(successful_expectations),
        "failed_expectations": failed_expectations,
    }

    # Save report JSON
    settings.paths.quality_dir.mkdir(parents=True, exist_ok=True)
    filename = report_name if report_name.endswith(".json") else f"{report_name}.json"
    output_path = settings.paths.quality_dir / filename
    write_json(output_path, payload)

    return payload


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path: Path | str) -> dict[str, Any]:
    """Aggregate data freshness metrics and check against the Freshness SLA (<= 180 days).

    SLA Rule: If more than 25% of papers have age_days > 180, is_fresh = False.
    """
    if df.empty:
        payload = {
            "latest_published": "N/A",
            "oldest_published": "N/A",
            "stale_rows": 0,
            "total_rows": 0,
            "stale_ratio": 0.0,
            "threshold_days": settings.freshness_threshold_days,
            "is_fresh": True,
        }
        write_json(report_path, payload)
        return payload

    latest_published = str(df["published"].max()) if "published" in df.columns else "N/A"
    oldest_published = str(df["published"].min()) if "published" in df.columns else "N/A"

    if "age_days" in df.columns:
        stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum())
    else:
        stale_rows = 0

    total_rows = len(df)
    stale_ratio = float(stale_rows / total_rows) if total_rows > 0 else 0.0
    is_fresh = bool(stale_ratio <= 0.25)

    payload = {
        "latest_published": latest_published,
        "oldest_published": oldest_published,
        "stale_rows": stale_rows,
        "total_rows": total_rows,
        "stale_ratio": round(stale_ratio, 4),
        "threshold_days": settings.freshness_threshold_days,
        "is_fresh": is_fresh,
    }

    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    write_json(report_path, payload)
    return payload
