from pathlib import Path

def read(path: str) -> str:
    p = Path(path).expanduser()
    if not p.exists():
        return f"File not found: {path}"
    return p.read_text()

def write(path: str, content: str) -> str:
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {len(content)} bytes to {path}"

def list_dir(path: str = ".") -> str:
    p = Path(path).expanduser()
    if not p.exists():
        return f"Path not found: {path}"
    items = sorted(p.iterdir())
    lines = []
    for item in items:
        kind = "DIR " if item.is_dir() else "FILE"
        lines.append(f"{kind}  {item.name}")
    return "\n".join(lines) or "(empty)"