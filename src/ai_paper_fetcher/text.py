import re


def slugify(value: str, fallback: str = "papers") -> str:
    """Return a filesystem-friendly slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or fallback


def clean_whitespace(value: str) -> str:
    return " ".join(value.split())


def safe_filename(value: str, fallback: str = "paper") -> str:
    filename = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip())
    filename = re.sub(r"_+", "_", filename).strip("._")
    return filename[:140] or fallback
