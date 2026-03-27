from workers import WorkerEntrypoint, Response
import json
import js

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloudflare AI Assistant</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: system-ui, sans-serif; max-width: 650px; margin: 40px auto; padding: 20px; background: #f4f4f9; }
        h2 { display: flex; align-items: center; gap: 10px; }
        #session-badge { font-size: 13px; background: #f38020; color: white; padding: 3px 10px; border-radius: 20px; font-weight: normal; }
        #chat { height: 380px; overflow-y: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 15px; }
        .msg { margin-bottom: 15px; padding: 12px; border-radius: 8px; line-height: 1.4; }
        .user { background: #000; color: #fff; margin-left: 20%; border-bottom-right-radius: 0; }
        .ai { background: #f38020; color: #fff; margin-right: 20%; border-bottom-left-radius: 0; }
        .system-area { display: flex; gap: 10px; margin-bottom: 10px; }
        .system-area input { flex-grow: 1; padding: 10px; border-radius: 6px; border: 1px solid #ccc; font-size: 14px; color: #555; }
        .system-area button { padding: 10px 15px; background: #555; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
        .system-area button:hover { background: #333; }
        .input-area { display: flex; gap: 10px; }
        .input-area input { flex-grow: 1; padding: 12px; border-radius: 6px; border: 1px solid #ccc; font-size: 16px; }
        .input-area button { padding: 12px 20px; background: #000; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .input-area button:hover { background: #333; }
        #clear-btn { margin-top: 10px; width: 100%; padding: 9px; background: transparent; color: #999; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; font-size: 13px; }
        #clear-btn:hover { background: #fee; color: #c00; border-color: #c00; }
    </style>
</head>
<body>
    <h2>🤖 Cloudflare AI Assistant <span id="session-badge" style="display:none">History Loaded</span></h2>

    <div class="system-area">
        <input type="text" id="system-prompt" placeholder='System prompt (e.g. "You are a pirate assistant")' />
        <button onclick="setSystem()">Set</button>
    </div>

    <div id="chat"></div>

    <div class="input-area">
        <input type="text" id="msg" placeholder="Type a message..." onkeypress="if(event.key === 'Enter') send()" />
        <button onclick="send()" id="btn">Send</button>
    </div>
    <button id="clear-btn" onclick="clearHistory()">🗑 Clear conversation history</button>

    <script>
        window.onload = async () => {
            const res = await fetch('/?history=1');
            const data = await res.json();
            const chat = document.getElementById('chat');

            if (data.messages && data.messages.length > 0) {
                document.getElementById('session-badge').style.display = 'inline';
                data.messages.forEach(m => {
                    if (m.role === 'user') chat.innerHTML += `<div class="msg user">${m.content}</div>`;
                    if (m.role === 'assistant') chat.innerHTML += `<div class="msg ai">${m.content}</div>`;
                });
            } else {
                chat.innerHTML = `<div class="msg ai">Hello! I'm your Llama 3.3 assistant. How can I help you today?</div>`;
            }
            chat.scrollTop = chat.scrollHeight;
        };

        async function setSystem() {
            const val = document.getElementById('system-prompt').value.trim();
            if (!val) return;
            await fetch('/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ set_system: val }) });
            document.getElementById('chat').innerHTML = `<div class="msg ai">✅ System prompt updated. Starting fresh!</div>`;
            document.getElementById('system-prompt').value = '';
        }

        async function send() {
            const input = document.getElementById('msg');
            const chat = document.getElementById('chat');
            const btn = document.getElementById('btn');
            const text = input.value.trim();
            if (!text) return;

            chat.innerHTML += `<div class="msg user">${text}</div>`;
            input.value = '';
            btn.disabled = true;
            btn.innerText = 'Thinking...';
            chat.scrollTop = chat.scrollHeight;

            try {
                const res = await fetch('/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                chat.innerHTML += `<div class="msg ai">${data.reply}</div>`;
            } catch (err) {
                chat.innerHTML += `<div class="msg ai" style="background:red;">Error communicating with AI.</div>`;
            }

            chat.scrollTop = chat.scrollHeight;
            btn.disabled = false;
            btn.innerText = 'Send';
        }

        async function clearHistory() {
            await fetch('/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ clear: true }) });
            document.getElementById('chat').innerHTML = `<div class="msg ai">🗑 History cleared. Let's start fresh!</div>`;
            document.getElementById('session-badge').style.display = 'none';
        }
    </script>
</body>
</html>
"""

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        session_id = "default_user_session"

        # GET — serve HTML or return history
        if request.method == "GET":
            if request.url.find("history=1") != -1:
                history_str = await self.env.CHAT_HISTORY.get(session_id)
                messages = json.loads(history_str) if history_str else []
                visible = [m for m in messages if m["role"] != "system"]
                return Response(json.dumps({"messages": visible}), headers={"content-type": "application/json"})
            return Response(HTML_PAGE, headers={"content-type": "text/html;charset=UTF-8"})

        # POST — handle all actions
        if request.method == "POST":
            data = json.loads(await request.text())

            # Clear history
            if data.get("clear"):
                await self.env.CHAT_HISTORY.delete(session_id)
                return Response(json.dumps({"ok": True}), headers={"content-type": "application/json"})

            # Set custom system prompt
            if data.get("set_system"):
                new_system = data["set_system"]
                messages = [{"role": "system", "content": new_system}]
                await self.env.CHAT_HISTORY.put(session_id, json.dumps(messages))
                return Response(json.dumps({"ok": True}), headers={"content-type": "application/json"})

            # Regular chat message
            user_msg = data.get("message", "")
            history_str = await self.env.CHAT_HISTORY.get(session_id)
            if history_str:
                messages = json.loads(history_str)
            else:
                messages = [{"role": "system", "content": "You are a helpful assistant. Keep your answers short."}]

            messages.append({"role": "user", "content": user_msg})

            # Convert Python dict to native JS object to satisfy Workers AI binding
            payload_str = json.dumps({"messages": messages})
            js_payload = js.JSON.parse(payload_str)

            ai_response = await self.env.AI.run("@cf/meta/llama-3.3-70b-instruct-fp8-fast", js_payload)

            try:
                reply = ai_response.to_py().get("response", "Error generating response")
            except:
                reply = getattr(ai_response, 'response', "Error parsing response")

            messages.append({"role": "assistant", "content": reply})
            await self.env.CHAT_HISTORY.put(session_id, json.dumps(messages))

            return Response(json.dumps({"reply": reply}), headers={"content-type": "application/json"})

        return Response("Method Not Allowed", status=405)