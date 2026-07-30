from anthropic import Anthropic
from dotenv import load_dotenv
import re
import datetime

load_dotenv()
client = Anthropic()

MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10,
              "nov": 11, "dec": 12}

def tag_company(text, known_companies):
    note = text[:2000]
    prompt = f"""You are tagging an internal meeting note with the single company it is primarily about.

Here are the companies already in our system. If the note is primarily about one of them, return that company's name EXACTLY as written here:
{known_companies}

Rules:
- Return ONLY the company name, on one line — no quotes, no JSON, no explanation.
- Prefer an exact match from the list above when the note is about one of those companies.
- If the note is primarily about a company NOT in the list, return that company's name as best you can determine it from the note.
- If the note is not clearly about any single company, return exactly: Unknown

NOTE:
{note}
"""
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=100,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip().strip('"')
def to_yyyymmdd(year, month, day):
    try:
        datetime.date(year, month, day)
    except ValueError:
        return 0
    return year * 10000 + month * 100 + day

def read_yyyymmdd(m):
    year = int(m.group(1))
    month = int(m.group(2))
    day = int(m.group(3))
    return to_yyyymmdd(year, month, day)

def read_yymmdd(m):
    year = 2000 + int(m.group(1))
    month = int(m.group(2))
    day = int(m.group(3))
    return to_yyyymmdd(year, month, day)

def read_yyyy_mm_dd(m):
    year = int(m.group(1))
    month = int(m.group(2))
    day = int(m.group(3)) if m.group(3) else 1
    return to_yyyymmdd(year, month, day)

def read_mdy_numeric(m):
    month = int(m.group(1))
    day = int(m.group(2))
    year = int(m.group(3)) if int(m.group(3)) > 1000 else 2000 + int(m.group(3))
    return to_yyyymmdd(year, month, day)

def read_month_name(m):
    month = MONTHS[m.group(1).lower()]
    year = int(m.group(2))
    day = 1
    return to_yyyymmdd(year, month, day)

def read_year_only(m):
    year = int(m.group(1))
    month = 1
    day = 1
    return to_yyyymmdd(year, month, day)

def tag_date(filename):
    TODAY = int(datetime.date.today().strftime("%Y%m%d"))
    PATTERNS = [
                (re.compile(r"(\d{4})(\d{2})(\d{2})"),read_yyyymmdd),
                (re.compile(r"(\d{4})[-_.](\d{2})(?:[-_.](\d{2}))?"), read_yyyy_mm_dd),
                (re.compile(r"(\d{2})(\d{2})(\d{2})"),read_yymmdd),
                (re.compile(r"(\d{1,2})[-_./:](\d{1,2})[-_./:](\d{4}|\d{2})"),read_mdy_numeric),
                (re.compile(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[ _-]?(\d{4})",re.I),read_month_name),
                (re.compile(r"(\d{4})"),read_year_only)
    ]
    for pat, read in PATTERNS:
        m = pat.search(filename)
        if m:
            result = read(m)
            if 20050101 <= result <= TODAY:
                return result
    return 0
