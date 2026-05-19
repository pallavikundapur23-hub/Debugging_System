import json
import urllib.request

payload = {
    "action": "opened",
    "repository": {
        "full_name": "charishmap3/buggy-todo-api",
        "clone_url": "https://github.com/charishmap3/buggy-todo-api.git",
    },
    "issue": {
        "number": 1,
        "title": "Test issue for remediation",
        "body": "Please analyze and fix the repository code.",
    },
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/webhook/github",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "X-GitHub-Event": "issues",
        "X-Hub-Signature-256": "sha256=invalid",
    },
)

with urllib.request.urlopen(req) as resp:
    print(resp.status)
    print(resp.read().decode())
