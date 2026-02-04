from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Segment:
    segment_id: str
    text: str
    chapter: str | None
    paragraph_index: int


def segment_text(text: str, max_chars: int) -> list[Segment]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    segments: list[Segment] = []
    chapter = None
    paragraph_index = 0

    for para in paragraphs:
        if len(para) < 80 and para.upper().startswith("CHAPTER"):
            chapter = para
            continue

        for chunk in _split_long_paragraph(para, max_chars):
            segment_id = f"p{paragraph_index:05d}"
            segments.append(
                Segment(
                    segment_id=segment_id,
                    text=chunk,
                    chapter=chapter,
                    paragraph_index=paragraph_index,
                )
            )
            paragraph_index += 1

    return segments


def _split_long_paragraph(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        start = end
    return chunks
