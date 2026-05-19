import os
import httpx

token = os.getenv('GITHUB_TOKEN')
print('TOKEN_PRESENT', bool(token))
if not token:
    raise SystemExit(0)
headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'}
with httpx.Client(timeout=20) as client:
    response = client.get('https://api.github.com/user', headers=headers)
    print('STATUS', response.status_code)
    print(response.text)
