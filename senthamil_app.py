"""Serve the combined Senthamil AI and Aakkam app on this computer."""

import json
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import senthamil_marabu as sm
from ai_console import explain_result


ROOT = Path(__file__).resolve().parent
MAX_REQUEST_SIZE = 8_192
PAGE = r"""<!doctype html>
<html lang="ta">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#145c50">
<title>செந்தமிழ்</title>
<style>
@font-face {
  font-family: "Noto Sans Tamil";
  src: url("/fonts/NotoSansTamil-Variable.ttf") format("truetype");
  font-weight: 100 900;
  font-display: swap;
}
:root { color-scheme: light; --bg:#f3f6f3; --surface:#fff; --ink:#20332d;
  --muted:#53675e; --line:#d5dfd9; --accent:#145c50; --soft:#e6f0eb; }
* { box-sizing:border-box; }
body { margin:0; height:100vh; height:100dvh; display:grid; grid-template-rows:auto 1fr;
  overflow:hidden; background:var(--bg); color:var(--ink);
  font-family:"Noto Sans Tamil","Latha",sans-serif; }
header { background:var(--surface); border-bottom:1px solid var(--line); padding:12px 20px 0; }
.brand { display:flex; align-items:center; gap:12px; }
h1 { color:var(--accent); margin:0; font-size:clamp(21px,4vw,27px); }
.caption { color:var(--muted); font-size:13px; margin:0 0 10px; }
nav { display:flex; gap:6px; }
nav button { padding:9px 18px; border:0; border-bottom:3px solid transparent;
  background:transparent; color:var(--muted); font:inherit; font-weight:700; cursor:pointer; }
nav button[aria-selected="true"] { color:var(--accent); border-bottom-color:var(--accent); }
main { min-height:0; }
.tab { height:100%; min-height:0; }
#ai { max-width:1000px; margin:auto; padding:16px; display:grid; grid-template-rows:1fr auto; gap:12px; }
#chat { min-height:0; overflow:auto; background:var(--surface); border:1px solid var(--line);
  border-radius:12px; padding:18px; }
.message { white-space:pre-wrap; overflow-wrap:anywhere; margin:0 0 14px; line-height:1.75; }
.message strong { color:var(--accent); display:block; margin-bottom:2px; }
.message.error strong { color:#a03333; }
form { display:grid; grid-template-columns:1fr auto; gap:8px; align-items:center;
  background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:10px; }
input { min-width:0; width:100%; padding:11px 12px; border:1px solid var(--line);
  border-radius:8px; background:#fff; color:var(--ink); font:inherit; font-size:16px; }
button:focus-visible,input:focus-visible { outline:3px solid #65a99a; outline-offset:2px; }
.send { border:0; border-radius:8px; padding:10px 20px; color:white; background:var(--accent);
  font:inherit; font-weight:700; cursor:pointer; }
.examples { grid-column:1/-1; display:flex; align-items:center; flex-wrap:wrap; gap:7px; color:var(--muted); font-size:13px; }
.examples button { font:inherit; color:var(--accent); background:var(--soft); border:0; border-radius:20px; padding:6px 11px; cursor:pointer; }
#aakkam { width:100%; height:100%; border:0; background:white; }
@media(max-width:520px) {
  header { padding:10px 12px 0; }
  nav button { padding:8px 13px; }
  #ai { padding:10px; gap:8px; }
  #chat { padding:13px; }
  .send { padding:10px 14px; }
}
</style>
</head>
<body>
<header>
  <div class="brand"><h1>செந்தமிழ்</h1></div>
  <p class="caption">நூல்வழி AI உதவியும் செந்தமிழ் ஆக்கமும் — ஒரே செயலியில்</p>
  <nav role="tablist" aria-label="செயலி">
    <button id="ai-tab" type="button" role="tab" aria-selected="true" aria-controls="ai">செந்தமிழ் AI</button>
    <button id="write-tab" type="button" role="tab" aria-selected="false" aria-controls="write">செந்தமிழ் ஆக்கம்</button>
  </nav>
</header>
<main>
  <section id="ai" class="tab" role="tabpanel" aria-labelledby="ai-tab">
    <div id="chat" aria-live="polite">
      <p class="message"><strong>செந்தமிழ் AI</strong>வணக்கம்! வினாவை கீழே எழுதுங்கள். இந்த உதவி திட்டத்தின் நூல் மற்றும் விதிகளைப் பயன்படுத்துகிறது; பொதுவான இணைய AI அல்ல.<br><br>எடுத்துக்காட்டுகள்: <b>ezhu.3</b>, <b>தேடு: நிலம்</b>, <b>மரம் + கிளை</b></p>
    </div>
    <form id="ask-form">
      <input id="question" type="text" autocomplete="off" placeholder="உங்கள் வினாவை இங்கே எழுதுங்கள்…" aria-label="வினா" autofocus>
      <button class="send" type="submit">கேள்</button>
      <div class="examples"><span>எடுத்துக்காட்டு:</span>
        <button type="button" data-query="ezhu.3">நூற்பா</button>
        <button type="button" data-query="தேடு: நிலம்">சொல் தேடல்</button>
        <button type="button" data-query="மரம் + கிளை">புணர்ச்சி</button>
      </div>
    </form>
  </section>
  <section id="write" class="tab" role="tabpanel" aria-labelledby="write-tab" hidden>
    <iframe id="aakkam" title="செந்தமிழ் ஆக்கம்" src="/app/aakkam/index.html"></iframe>
  </section>
</main>
<script>
const question = document.getElementById("question");
const chat = document.getElementById("chat");
function addMessage(name, text, isError=false) {
  const p = document.createElement("p");
  p.className = "message" + (isError ? " error" : "");
  const title = document.createElement("strong");
  title.textContent = name;
  p.append(title, document.createTextNode(text));
  chat.append(p);
  chat.scrollTop = chat.scrollHeight;
}
async function ask(text) {
  const value = (text || question.value).trim();
  if (!value) { question.focus(); return; }
  question.value = "";
  addMessage("நீங்கள்", value);
  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: value })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "விடை பெற முடியவில்லை.");
    addMessage("செந்தமிழ் AI", result.answer);
  } catch (error) {
    addMessage("சிக்கல்", error.message || "இணைப்பில் சிக்கல். மீண்டும் முயலுங்கள்.", true);
  }
}
document.getElementById("ask-form").addEventListener("submit", event => {
  event.preventDefault();
  ask();
});
document.querySelectorAll("[data-query]").forEach(button => {
  button.addEventListener("click", () => ask(button.dataset.query));
});
const tabs = [
  [document.getElementById("ai-tab"), document.getElementById("ai")],
  [document.getElementById("write-tab"), document.getElementById("write")]
];
tabs.forEach(([button, panel]) => button.addEventListener("click", () => {
  tabs.forEach(([otherButton, otherPanel]) => {
    const active = otherButton === button;
    otherButton.setAttribute("aria-selected", String(active));
    otherPanel.hidden = !active;
  });
  if (panel.id === "ai") question.focus();
}));
window.addEventListener("load", () => question.focus());
</script>
</body>
</html>"""


class SenthamilHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if urlsplit(self.path).path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != "/api/ask":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json_response(400, {"error": "வினாவை மீண்டும் எழுதுங்கள்."})
            return
        if length <= 0 or length > MAX_REQUEST_SIZE:
            self._json_response(413, {"error": "வினா காலியாக உள்ளது அல்லது மிக நீளமானது."})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json_response(400, {"error": "வினாவைப் படிக்க முடியவில்லை."})
            return
        question = payload.get("question", "") if isinstance(payload, dict) else ""
        if not isinstance(question, str) or not question.strip():
            self._json_response(400, {"error": "வினாவை எழுதுங்கள்."})
            return
        try:
            answer = explain_result(sm.kel(question))
        except (ValueError, KeyError) as error:
            self._json_response(422, {"error": str(error)})
            return
        except Exception as error:
            self.log_error("Question processing failed: %s", error)
            self._json_response(500, {"error": "வினாவைச் செயலாக்கும்போது சிக்கல் ஏற்பட்டது."})
            return
        self._json_response(200, {"answer": answer})

    def _json_response(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), SenthamilHandler)
    server.daemon_threads = True
    address, port = server.server_address
    url = f"http://{address}:{port}/"
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    print(f"செந்தமிழ் செயலி திறக்கிறது: {url}")
    print("செயலியை மூட இந்தச் சாளரத்தை மூடுங்கள்.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
