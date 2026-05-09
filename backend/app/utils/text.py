def count_cn_words(text: str | None) -> int:
    return len((text or "").replace(" ", "").replace("\n", "").replace("\r", ""))


def compact(text: str | None, limit: int = 600) -> str:
    value = text or ""
    return value if len(value) <= limit else value[:limit] + "..."
