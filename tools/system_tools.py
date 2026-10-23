import subprocess

def status(service: str) -> str:
    result = subprocess.run(
        ["systemctl", "status", service, "--no-pager"],
        capture_output=True, text=True
    )
    return (result.stdout + result.stderr).strip()

def restart(service: str) -> str:
    result = subprocess.run(
        ["sudo", "systemctl", "restart", service],
        capture_output=True, text=True
    )
    return (result.stdout + result.stderr).strip() or f"Restarted {service}"