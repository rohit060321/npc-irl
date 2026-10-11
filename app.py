
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import urllib.request

MODEL = "llama3.2:3b"


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/quest":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length))
        mode = data.get("mode", "chaos")

        prompt = f"""
You are NPC IRL, a hilarious real-world adventure game master.
Generate ONE safe outdoor quest for an ordinary neighborhood walk.
Quest category: {mode}

Rules:
- Must take 1-5 minutes.
- No trespassing, traffic risks, touching wildlife, or approaching strangers.
- Encourage observing surroundings, nature, or architecture.
- Be weird, imaginative, and funny.
- Never ask users to buy anything.
- Return ONLY valid JSON with keys:
  title, mission, xp, fun_fact

Example:
{{"title":"Suspicious Leaf","mission":"Find a leaf that looks like it is hiding a secret. Give it a name.","xp":30,"fun_fact":"Leaves come in wildly different shapes."}}
"""

        payload = json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }).encode()

        try:
            request = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(request, timeout=90) as response:
                result = json.loads(response.read())
                quest = json.loads(result["response"])

            body = json.dumps(quest).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        except Exception as e:
            body = json.dumps({
                "error": str(e),
                "message": "Could not reach the local AI. Check that Ollama is running."
            }).encode()

            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)


HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()