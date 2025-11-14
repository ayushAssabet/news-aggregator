from __future__ import annotations
import re
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# -----------------------------
# Nepali calendar data
# -----------------------------
# Truncated BS→AD mapping for performance; sufficient for 2000–2099 BS
from typing import Dict, List

NEPALI_CALENDAR: Dict[int, List[int]] = {
    2080: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2081: [31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2082: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2083: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2084: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2085: [31, 32, 31, 32, 31, 31, 30, 30, 29, 30, 30, 30],
    2086: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2087: [31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30],
    2088: [30, 31, 32, 32, 30, 31, 30, 30, 29, 30, 30, 30],
    2089: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2090: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
}

BS_REFERENCE_YEAR = 2000
BS_REFERENCE_DATE = datetime(1943, 4, 14)  # 2000-01-01 BS = 1943-04-14 AD

# -----------------------------
# Nepali → English digit conversion
# -----------------------------
def nepali_to_english_digits(text: str) -> str:
    nep = "०१२३४५६७८९"
    eng = "0123456789"
    return text.translate(str.maketrans(nep, eng))

# -----------------------------
# Nepali month mapping
# -----------------------------
NEPALI_MONTHS = {
    "बैशाख": 1, "जेष्ठ": 2, "जेठ": 2, "असार": 3, "असाढ": 3,
    "साउन": 4, "श्रावण": 4, "भदौ": 5, "भाद्र": 5, "आश्विन": 6, "असोज": 6,
    "कार्तिक": 7, "कात्तिक": 7, "मंसिर": 8, "मङ्सिर": 8,
    "पौष": 9, "पुष": 9, "पूस": 9,
    "माघ": 10, "फाल्गुण": 11, "फागुन": 11, "चैत": 12, "चैत्र": 12,
}

# -----------------------------
# BS → AD conversion
# -----------------------------
def bs_to_ad(year: int, month: int, day: int) -> datetime:
    """Convert Nepali date (BS) → English date (AD)."""
    if year not in NEPALI_CALENDAR:
        raise ValueError(f"Unsupported BS year: {year}")
    if not (1 <= month <= 12):
        raise ValueError(f"Invalid month: {month}")
    if not (1 <= day <= NEPALI_CALENDAR[year][month - 1]):
        raise ValueError(f"Invalid day {day} for {year}-{month}")

    days_count = 0
    for y in range(BS_REFERENCE_YEAR, year):
        if y in NEPALI_CALENDAR:
            days_count += sum(NEPALI_CALENDAR[y])
    for m in range(month - 1):
        days_count += NEPALI_CALENDAR[year][m]
    days_count += (day - 1)

    ad_date = BS_REFERENCE_DATE + timedelta(days=days_count)
    return ad_date.replace(tzinfo=timezone.utc)

# -----------------------------
# Parsers for sources
# -----------------------------
def parse_onlinekhabar(text: str) -> datetime:
    """Example: २०८२ कात्तिक २७ गते १०:५९"""
    text = nepali_to_english_digits(text).replace("गते", "").strip()
    time_match = re.search(r'(\d{1,2}):(\d{1,2})', text)
    hour, minute = (0, 0)
    if time_match:
        hour, minute = map(int, time_match.groups())
        text = re.sub(r'\d{1,2}:\d{1,2}', '', text).strip()

    parts = text.split()
    if len(parts) < 3:
        raise ValueError(f"Invalid OnlineKhabar format: {text}")

    year, month_name, day = int(parts[0]), parts[1], int(parts[2])
    month = NEPALI_MONTHS.get(month_name)
    if not month:
        raise ValueError(f"Unknown month: {month_name}")

    base = bs_to_ad(year, month, day)
    return base.replace(hour=hour, minute=minute)

def parse_kantipur(text: str) -> datetime:
    """Example: कार्तिक २७, २०८२"""
    text = nepali_to_english_digits(text.replace(",", "").strip())
    parts = text.split()
    if len(parts) < 3:
        raise ValueError(f"Invalid Kantipur format: {text}")

    month_name, day, year = parts[0], int(parts[1]), int(parts[2])
    month = NEPALI_MONTHS.get(month_name)
    if not month:
        raise ValueError(f"Unknown month: {month_name}")

    return bs_to_ad(year, month, day)

def parse_generic_nepali_date(text: str) -> datetime | None:
    """Attempt to parse any Nepali date pattern."""
    text = nepali_to_english_digits(text.replace(",", "").replace("गते", "").strip())
    parts = text.split()

    try:
        if len(parts) == 3 and parts[0].isdigit():
            return bs_to_ad(int(parts[0]), NEPALI_MONTHS.get(parts[1]), int(parts[2]))
        elif len(parts) == 3 and parts[1].isdigit():
            return bs_to_ad(int(parts[2]), NEPALI_MONTHS.get(parts[0]), int(parts[1]))
        elif '-' in text:
            y, m, d = map(int, text.split('-'))
            return bs_to_ad(y, m, d)
    except Exception:
        pass
    return None

# -----------------------------
# Unified entrypoint
# -----------------------------
def parse_nepali_date(text: str, source_url: str = "") -> datetime | None:
    """Detect format and convert Nepali date to UTC datetime."""
    if not text:
        return None

    text = text.strip()
    try:
        if "onlinekhabar" in source_url:
            return parse_onlinekhabar(text)
        if "kantipur" in source_url or "ekantipur" in source_url:
            return parse_kantipur(text)
        return parse_generic_nepali_date(text)
    except Exception as e:
        logger.warning(f"Failed to parse Nepali date from '{text}' ({source_url}): {e}")
        return None

# -----------------------------
# Test (optional)
# -----------------------------
if __name__ == "__main__":
    samples = [
        ("२०८२ कात्तिक २७ गते १०:५९", "onlinekhabar.com"),
        ("कार्तिक २७, २०८२", "ekantipur.com"),
        ("२०८२ कात्तिक २७", "generic"),
        ("कात्तिक २७ २०८२", "generic"),
        ("२०८२-१०-२७", "generic"),
    ]
    for txt, src in samples:
        print(f"{txt} → {parse_nepali_date(txt, src)}")
