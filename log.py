import requests
import time
import zipfile
import io
import os
from dotenv import load_dotenv

load_dotenv()

# GitHub Repo Info
OWNER = "Dinesh-4"
REPO = "Devops"
BRANCH = "main"
WORKFLOW_FILENAME = "main.yml"
TOKEN = os.getenv('TOKEN')

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# 1. Trigger workflow dispatch
def trigger_workflow():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_FILENAME}/dispatches"
    payload = {"ref": BRANCH}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 204:
        print("✅ Workflow triggered.")
    else:
        print("❌ Trigger failed:", response.text)
        exit(1)

# 2. Get latest run ID
def get_latest_run_id():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"
    while True:
        response = requests.get(url, headers=HEADERS)
        runs = response.json().get("workflow_runs", [])
        if runs:
            return runs[0]["id"]
        time.sleep(3)

# 3. Wait for completion
def wait_for_run(run_id):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}"
    while True:
        response = requests.get(url, headers=HEADERS).json()
        status = response["status"]
        print(f"🔄 Status: {status}")
        if status == "completed":
            return response["conclusion"]
        time.sleep(5)

# 4. Download logs
def download_and_extract_logs(run_id):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}/logs"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall("logs")
        print("📦 Logs downloaded to 'logs/'")
    else:
        print("❌ Failed to download logs:", response.text)
        exit(1)

# 5. Print step-by-step logs like GitHub UI
def print_logs():
    for root, dirs, files in os.walk("logs"):
        for file in sorted(files):
            path = os.path.join(root, file)
            print(f"\n📄 === {file.replace('.txt', '')} ===")
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                print(f.read())

# 6. Generate Summary
def summarize_run(run_id):
    print("\n📋 Generating summary...")

    # Get workflow run info
    run_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}"
    run_info = requests.get(run_url, headers=HEADERS).json()

    commit_sha = run_info["head_sha"]
    actor = run_info["actor"]["login"]
    status = run_info["conclusion"]
    trigger = run_info["event"]
    branch = run_info["head_branch"]
    workflow_name = run_info["name"]
    duration = run_info.get("run_duration_ms", 0) / 1000

    # Get commit info
    commit_url = f"https://api.github.com/repos/{OWNER}/{REPO}/commits/{commit_sha}"
    commit_data = requests.get(commit_url, headers=HEADERS).json()
    message = commit_data["commit"]["message"]

    # Get job step names from downloaded logs
    steps = []
    for root, dirs, files in os.walk("logs"):
        for file in sorted(files):
            if file.endswith(".txt"):
                steps.append(file.replace(".txt", ""))

    # Detect actions performed
    actions = []
    for step in steps:
        lower = step.lower()
        if "pytest" in lower:
            actions.append("✅ Ran unit tests using Pytest")
        if "docker" in lower and "login" in lower:
            actions.append("🔐 Logged in to Docker Hub")
        if "docker image" in lower or "build docker" in lower:
            actions.append("📦 Built Docker image")
        if "push" in lower:
            actions.append("🚀 Pushed Docker image to Docker Hub")

    # Create summary text
    summary = f"""✅ CI/CD Pipeline Summary
----------------------------

📦 Commit Info:
- Message       : {message}
- Author        : {actor}
- Commit SHA    : {commit_sha}
- Branch        : {branch}

🧪 Workflow Run: {workflow_name}
- Status        : {'✅ Success' if status == 'success' else '❌ Failed'}
- Triggered by  : {trigger}
- Duration      : {duration:.2f} seconds

📋 Job Steps:
""" + "\n".join([f"{i+1}. {step} ✅" for i, step in enumerate(steps)]) + "\n\n"

    summary += "🛠️ Actions Performed:\n"
    for action in actions:
        summary += f"- {action}\n"

    summary += "\n📄 Logs saved in: ./logs/\n📝 Summary saved in: ./ci_summary.txt\n"

    # Save to file
    with open("ci_summary.txt", "w") as f:
        f.write(summary)

    print(summary)

# ==== Run it ====
trigger_workflow()
time.sleep(10)
run_id = get_latest_run_id()
wait_for_run(run_id)
download_and_extract_logs(run_id)
print_logs()
summarize_run(run_id)
