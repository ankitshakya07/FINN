import subprocess
import json
import urllib.request
import urllib.error
import sys

print("=" * 80)
print("CREATING PRIVATE GITHUB REPOSITORY: FINN")
print("=" * 80)

# 1. Retrieve credentials from Git Credential Manager
p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
out, _ = p.communicate(input='protocol=https\nhost=github.com\n\n')

data = {}
for line in out.splitlines():
    if '=' in line:
        k, v = line.split('=', 1)
        data[k] = v

token = data.get('password')
user = data.get('username')

if not token or not user:
    print("ERROR: Could not retrieve GitHub credentials from Git Credential Manager.")
    sys.exit(1)

print(f"Creating repository under GitHub account: {user}")

# 2. Call GitHub API to create private repository
payload = {
    "name": "FINN",
    "description": "FINN — Investment intelligence platform for Indian stock markets, combining corporate announcements, market anomalies, financial research and AI-powered insights.",
    "private": True,
    "has_issues": True,
    "has_wiki": False,
    "has_projects": False
}

req = urllib.request.Request(
    'https://api.github.com/user/repos',
    data=json.dumps(payload).encode('utf-8'),
    headers={
        'Authorization': f'Bearer {token}',
        'User-Agent': 'FINN-Publisher',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req) as resp:
        repo_data = json.loads(resp.read().decode('utf-8'))
        print("Repository created successfully!")
        print(f"HTML URL: {repo_data.get('html_url')}")
        print(f"Clone URL: {repo_data.get('clone_url')}")
        print(f"Private: {repo_data.get('private')}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    print(f"HTTPError {e.code}: {err_body}")
    sys.exit(1)

# 3. Configure git remote origin
remote_url = repo_data.get('clone_url')
print(f"\nAdding remote origin: {remote_url}")
subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)

# 4. Push to GitHub
print("\nPushing main branch to origin...")
push_res = subprocess.run(['git', 'push', '-u', 'origin', 'main'], capture_output=True, text=True)
print("STDOUT:", push_res.stdout)
print("STDERR:", push_res.stderr)

if push_res.returncode == 0:
    print("\nSUCCESS: FINN repository published successfully to GitHub!")
else:
    print(f"\nERROR: git push failed with exit code {push_res.returncode}")
    sys.exit(push_res.returncode)

