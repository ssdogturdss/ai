from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import asyncio
from pathlib import Path
from datetime import datetime
import ollama
from tools import git_tools, docker_tools, system_tools, file_tools

app = FastAPI(title="AI Server Agent Web UI")
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

STATE_DIR = Path("state")
CONV_FILE = STATE_DIR / "conversation.json"

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

def load_conversation():
    if CONV_FILE.exists():
        return json.loads(CONV_FILE.read_text())
    return []

def save_conversation(conv):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    CONV_FILE.write_text(json.dumps(conv, indent=2))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conversation = load_conversation()
    system_prompt = Path("prompts/system.txt").read_text()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "chat":
                user_input = message["content"]
                conversation.append({"role": "user", "content": user_input})

                try:
                    response = ollama.chat(
                        model="llama3.1:8b",
                        messages=[{"role": "system", "content": system_prompt}] + conversation,
                        tools=list(TOOLS.keys()),
                    )
                    msg = response["message"]
                    conversation.append(msg)

                    if msg.get("tool_calls"):
                        for call in msg["tool_calls"]:
                            name = call["function"]["name"]
                            args = call["function"].get("arguments", {})
                            if name in TOOLS:
                                try:
                                    result = TOOLS[name](**args) if args else TOOLS[name]()
                                except Exception as e:
                                    result = f"Error: {e}"
                            else:
                                result = f"Unknown tool: {name}"
                            conversation.append({"role": "tool", "content": str(result)})
                            await websocket.send_json({
                                "type": "tool",
                                "name": name,
                                "result": str(result)
                            })
                    else:
                        await websocket.send_json({
                            "type": "message",
                            "content": msg.get("content", "")
                        })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "content": str(e)
                    })

                save_conversation(conversation)

            elif message["type"] == "clear":
                conversation = []
                save_conversation(conversation)
                await websocket.send_json({"type": "cleared"})

    except WebSocketDisconnect:
        pass
