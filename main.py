#!/usr/bin/env python3
"""Entry point – run web UI by default"""
import sys
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from agent import main as cli_main
        cli_main()
    else:
        import uvicorn
        uvicorn.run("web.app:app", host="0.0.0.0", port=8000, reload=True)