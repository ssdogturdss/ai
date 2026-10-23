#!/usr/bin/env python3
"""
Minimal persistent AI agent for Ubuntu 22.04
Tools: git, docker, systemctl, file operations
"""

import json
import ollama
from pathlib import Path
from datetime import datetime
from tools import git_tools, docker_tools, system_tools, file_tools

STATE_DIR = Path("state")
CONV_FILE = STATE_DIR / "conversation.json"
AUDIT = STATE_DIR / "audit.log"

TOOLS = {
    "git_clone": git_tools.clone,
    "git_pull": git_tools.pull,
    "docker_build": docker_tools.build,
    "docker_run": docker_tools.run,
    "docker_stop": docker_tools.stop,
    "docker_ps": docker_tools.ps,
    "systemctl_status": system_tools.status,
    "systemctl_restart": system_tools.restart,
    "read_file": file_tools.read,
    "write_file": file_tools.write,
    "list_dir": file_tools.list_dir,
}

def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text())
    return default

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))

def audit(msg: str):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {msg}\n")

def main():
    conversation = load_json(CONV_FILE, [])
    system = Path("prompts/system.txt").read_text()

    print("=" * 50)
    print("  AI Server Agent ready")
    print("  Type a task or 'quit'")
    print("=" * 50)

    while True:
        try:
            user = input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if user.lower() in {"quit", "exit", "q"}:
            break
        if not user:
            continue

        conversation.append({"role": "user", "content": user})
        audit(f"USER: {user}")

        try:
            response = ollama.chat(
                model="llama3.1:8b",          # change if you pulled a different model
                messages=[{"role": "system", "content": system}] + conversation,
                tools=list(TOOLS.keys()),
            )
        except Exception as e:
            print(f"Model error: {e}")
            print("Is Ollama running? Try: ollama serve")
            continue

        msg = response["message"]
        conversation.append(msg)

        if msg.get("tool_calls"):
            for call in msg["tool_calls"]:
                name = call["function"]["name"]
                args = call["function"].get("arguments", {})
                audit(f"TOOL {name} {args}")

                if name not in TOOLS:
                    result = f"Unknown tool: {name}"
                else:
                    try:
                        result = TOOLS[name](**args) if args else TOOLS[name]()
                    except Exception as e:
                        result = f"Error: {e}"

                conversation.append({"role": "tool", "content": str(result)})
                print(f"\n[{name}] → {result}")
        else:
            print(f"\nAgent: {msg.get('content', '')}")

        save_json(CONV_FILE, conversation)

if __name__ == "__main__":
    main()