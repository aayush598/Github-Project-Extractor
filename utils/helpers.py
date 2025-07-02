# utils/helpers.py
import re
from typing import List, Tuple

###############################################################################
# 1.  Generic helpers you already had
###############################################################################
def chunk_text(text: str, max_length: int = 3_000) -> List[str]:
    """Yield slices of `text` ≤ max_length characters."""
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]

###############################################################################
# 2.  NEW: Clean Groq / LLM output & extract structured data
###############################################################################
_CODE_FENCE_RX = re.compile(
    r"```[\w+-]*\n([\s\S]*?)```",              # ```python\n ... ```
    flags=re.MULTILINE,
)

_BULLET_RX = re.compile(r"^(?:\s*[-*+]\s+|\s*\d+[.)]\s+)", flags=re.MULTILINE)

def _strip_code_fences(text: str) -> str:
    """Remove ```fenced``` code blocks, whatever language tag they use."""
    return _CODE_FENCE_RX.sub("", text)

def parse_llm_summary(summary_text: str) -> Tuple[List[str], List[str]]:
    """
    Robustly pull **features** and **tech‑stack items** from Groq output.

    • Works whether the LLM uses bullets, numbers, or plain “Label: …” lines.  
    • Ignores code‑fenced blocks entirely.  
    • Treats the first ‘features’ section it sees as authoritative, likewise
      for the tech‑stack section.
    """
    clean = _strip_code_fences(summary_text)

    # Split into lines and normalise whitespace
    lines = [ln.strip() for ln in clean.splitlines() if ln.strip()]

    features, tech = [], []
    mode = None

    for ln in lines:
        low = ln.lower()

        # Detect section switches (very forgiving)
        if "feature" in low and "tech" not in low:
            mode = "features"
            continue
        if "tech stack" in low or ("stack" in low and "tech" in low):
            mode = "tech"
            continue

        # If we are inside a section, try to recognise list‑ish lines
        if mode and ln:  # ignore blank lines
            # Strip leading bullets / numbers
            entry = _BULLET_RX.sub("", ln).strip()

            # Split “Label: description”  → keep the whole line for now
            if mode == "features":
                features.append(entry)
            elif mode == "tech":
                tech.append(entry)

    return features, tech
