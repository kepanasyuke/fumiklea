import re

def normalize_answer(ans: str) -> str:
    if not ans:
        return ""
    ans = ans.strip().lower().replace(" ", "").replace(",", ".")
    if ans == "":
        return ""
    m = re.fullmatch(r"(-?\d+)/(\d+)", ans)
    if m:
        num = int(m.group(1))
        den = int(m.group(2))
        if den != 0:
            return f"{num/den:.6f}"
        return ans
    try:
        val = float(ans)
        return f"{val:.6f}"
    except ValueError:
        pass
    return ans