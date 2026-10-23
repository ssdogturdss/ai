import subprocess
from typing import Optional

def build(path: str, tag: str) -> str:
    result = subprocess.run(
        ["docker", "build", "-t", tag, path],
        capture_output=True, text=True
    )
    return (result.stdout + result.stderr).strip()

def run(image: str, name: str, ports: str = "", env: str = "") -> str:
    cmd = ["docker", "run", "-d", "--name", name, "--restart", "unless-stopped"]
    if ports:
        for p in ports.split(","):
            cmd.extend(["-p", p.strip()])
    if env:
        for e in env.split(","):
            cmd.extend(["-e", e.strip()])
    cmd.append(image)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return (result.stdout + result.stderr).strip()

def stop(name: str) -> str:
    result = subprocess.run(
        ["docker", "stop", name],
        capture_output=True, text=True
    )
    subprocess.run(["docker", "rm", name], capture_output=True)
    return (result.stdout + result.stderr).strip() or f"Stopped {name}"

def ps() -> str:
    result = subprocess.run(
        ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
        capture_output=True, text=True
    )
    return result.stdout.strip()