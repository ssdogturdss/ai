#!/usr/bin/env bash
echo "=== AI Agent Status ==="
echo "Location  : $(pwd)"
echo "Python    : $(.venv/bin/python --version 2>/dev/null || echo 'venv missing')"
echo "Ollama    : $(command -v ollama >/dev/null && ollama list 2>/dev/null | head -5 || echo 'not found')"
echo "Docker    : $(docker --version 2>/dev/null || echo 'missing')"
echo "Workspaces: $(ls ~/workspaces 2>/dev/null | wc -l) projects"
echo "Audit log : $(wc -l < state/audit.log 2>/dev/null || echo 0) entries"