from __future__ import annotations

from datetime import date
from typing import Any


def _parse_year_month(value: str | None) -> date | None:
    if not value or value == "PRESENT":
        return None

    try:
        year_text, month_text = value.split("-", maxsplit=1)
        return date(int(year_text), int(month_text), 1)
    except (TypeError, ValueError):
        return None


def _month_index(value: date) -> int:
    return (value.year * 12) + value.month


def _format_year_month(value: date) -> str:
    return f"{value.year:04d}-{value.month:02d}"


def _add_months(value: date, months: int) -> date:
    total = (_month_index(value) - 1) + months
    year = total // 12
    month = (total % 12) + 1
    return date(year, month, 1)


def _severity_for_gap(months: int) -> str:
    if months >= 12:
        return "HIGH"
    if months >= 6:
        return "MEDIUM"
    return "LOW"


def detect_gaps(experience: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized_experience: list[tuple[date, date | None]] = []
    for item in experience:
        if not isinstance(item, dict):
            continue

        start_date = _parse_year_month(item.get("start"))
        if start_date is None:
            continue

        end_date = _parse_year_month(item.get("end")) or start_date
        if end_date < start_date:
            end_date = start_date

        normalized_experience.append((start_date, end_date))

    normalized_experience.sort(key=lambda item: item[0])

    gaps: list[dict[str, Any]] = []
    for previous, current in zip(normalized_experience, normalized_experience[1:]):
        previous_end = previous[1]
        current_start = current[0]

        gap_start = _add_months(previous_end, 1)
        gap_months = _month_index(current_start) - _month_index(previous_end) - 1
        if gap_months < 3:
            continue

        gap_end = _add_months(current_start, -1)
        gaps.append(
            {
                "start": _format_year_month(gap_start),
                "end": _format_year_month(gap_end),
                "months": gap_months,
                "severity": _severity_for_gap(gap_months),
            }
        )

    return gaps
