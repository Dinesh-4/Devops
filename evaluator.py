import subprocess
import sys
import json
import time
from tabulate import tabulate

summary_lines = []  # 📝 Collect summary lines here

def log_summary(line=""):
    summary_lines.append(line)

def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

def inspect_image(image_name):
    print("\n\033[1m🔍 Inspecting Docker Image\033[0m")
    log_summary("## 🔍 Inspecting Docker Image")

    output = run_command(["docker", "inspect", image_name])
    try:
        info = json.loads(output)[0]
        entrypoint = info['Config'].get('Entrypoint')
        cmd = info['Config'].get('Cmd')
        env = info['Config'].get('Env', [])
        ports = info['Config'].get('ExposedPorts')

        print(f"{'Entrypoint:':15} {entrypoint}")
        print(f"{'CMD:':15} {cmd}")
        print(f"{'Env Vars:':15} {len(env)} variables")
        print(f"{'Exposed Ports:':15} {ports}")

        log_summary(f"- Entrypoint: {entrypoint}")
        log_summary(f"- CMD: {cmd}")
        log_summary(f"- Env Vars: {len(env)} variables")
        log_summary(f"- Exposed Ports: {ports}")
    except Exception as e:
        print(f"Failed to parse inspect output: {e}")
        log_summary("❌ Failed to parse inspect output.")

def check_history(image_name):
    print("\n\033[1m📜 Docker Image History\033[0m")
    log_summary("\n## 📜 Docker Image History")

    output = run_command(["docker", "history", "--no-trunc", "--format", "{{.CreatedBy}}\t{{.Size}}", image_name])
    lines = output.splitlines()
    table = [line.split('\t') for line in lines]
    history_table = tabulate(table, headers=["Command", "Size"], tablefmt="github")
    print(history_table)
    log_summary(history_table)

def check_size(image_name):
    print("\n\033[1m📦 Image Size\033[0m")
    log_summary("\n## 📦 Image Size")

    output = run_command(["docker", "image", "inspect", image_name, "--format={{.Size}}"])
    if output.isdigit():
        size_mb = round(int(output) / (1024 ** 2), 2)
        print(f"{'Size:':15} {size_mb} MB")
        log_summary(f"- Size: {size_mb} MB")
    else:
        print(f"{'Size:':15} {output}")
        log_summary(f"- Size: {output}")

def check_health(container_id):
    print("\n\033[1m❤️ Container Health Status\033[0m")
    log_summary("\n## ❤️ Container Health Status")

    output = run_command(["docker", "inspect", "--format={{json .State.Health}}", container_id])
    try:
        health = json.loads(output)
        status = health.get("Status")
        streak = health.get("FailingStreak")
        logs = health.get("Log", [])

        print(f"{'Status:':15} {status}")
        print(f"{'Failing Streak:':15} {streak}")
        log_summary(f"- Status: {status}")
        log_summary(f"- Failing Streak: {streak}")
        log_summary("Log:")
        for entry in logs:
            msg = f"  - [{entry['ExitCode']}] {entry['Output'].strip()}"
            print(msg)
            log_summary(msg)
    except:
        print("No health check defined or container too early to inspect health.")
        log_summary("No health check defined or container too early to inspect health.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python evaluator.py <docker-image-name>")
        sys.exit(1)

    image_name = sys.argv[1]

    print("\n\033[1;36m=== Docker Image Evaluation ===\033[0m")
    log_summary("# 🐳 Docker Image Evaluation")
    log_summary(f"**Image Name:** `{image_name}`\n")

    inspect_image(image_name)
    check_history(image_name)
    check_size(image_name)

    print("\n🚀 Spinning up container to test healthcheck...")
    log_summary("\n## 🚀 Container Healthcheck")
    container_id = run_command(["docker", "run", "-d", image_name]).strip()
    print(f"{'Container ID:':15} {container_id}")
    log_summary(f"- Container ID: `{container_id}`")

    print("⏳ Waiting 5 seconds for healthcheck to initialize...")
    time.sleep(5)

    check_health(container_id)

    print("\n🧹 Cleaning up temporary container...")
    run_command(["docker", "rm", "-f", container_id])
    print("✅ Done.\n")
    log_summary("\n✅ Container cleaned up.\n")

    # Save summary to file
    with open("docker_summary.txt", "w") as f:
        f.write("\n".join(summary_lines))

    print("\033[1;32m📄 Docker summary saved to 'docker_summary.txt'\033[0m")

if __name__ == "__main__":
    main()