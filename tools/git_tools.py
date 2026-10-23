import subprocess
from pathlib import Path

def clone(url: str, target_dir: str = None) -> str:
    if not target_dir:
        name = Path(url).stem.replace(".git", "")
        target_dir = str(Path.home() / "workspaces" / name)
    Path(target_dir).parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", url, target_dir],
        capture_output=True, text=True
    )
    return (result.stdout + result.stderr).strip() or f"Cloned into {target_dir}"

def pull(path: str) -> str:
    result = subprocess.run(
        ["git", "-C", path, "pull"],
        capture_output=True, text=True
    )
    return (result.stdout + result.stderr).strip()