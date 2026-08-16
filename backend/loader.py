import requests
import zipfile
import io
import os
import json

REPOS = [
    "Python-CurrencyConverter",
    "python-weather-app",
    "PersonalFinanceTracker",
    "AetherQuant",
    "DiabetesDetector",
    "deepfake-detector",
    "Picassify",
    "NeuralLens",
    "SentimentSense",
]

GITHUB_USER = "ali-faraz-py"

INCLUDE_EXTENSIONS = {".py", ".md", ".txt"}
SKIP_DIRS = {"venv", "node_modules", ".git", "__pycache__", ".next"}

def should_include(path):
    if any(skip in path.split("/") for skip in SKIP_DIRS):
        return False
    return any(path.endswith(ext) for ext in INCLUDE_EXTENSIONS)

def fetch_repo_zip(repo_name):
    """Try 'main' branch first, fall back to 'master' if that 404s."""
    for branch in ["main", "master"]:
        url = f"https://github.com/{GITHUB_USER}/{repo_name}/archive/refs/heads/{branch}.zip"
        response = requests.get(url)
        if response.status_code == 200:
            return response.content, branch
    return None, None

def extract_files(zip_bytes, repo_name):
    files = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for name in z.namelist():
            relative_path = "/".join(name.split("/")[1:])
            if not relative_path or not should_include(relative_path):
                continue
            try:
                content = z.read(name).decode("utf-8")
                files.append({
                    "repo": repo_name,
                    "path": relative_path,
                    "content": content
                })
            except Exception as e:
                print(f"  Skipped {relative_path}: {e}")
    return files

def main():
    all_files = []

    for repo_name in REPOS:
        print(f"Fetching {repo_name}...")
        zip_bytes, branch = fetch_repo_zip(repo_name)
        if zip_bytes is None:
            print(f"  ✗ Could not download (checked main and master branches)")
            continue
        files = extract_files(zip_bytes, repo_name)
        print(f"  → {len(files)} files (branch: {branch})")
        all_files.extend(files)

    os.makedirs("data", exist_ok=True)
    with open("data/repo_files.json", "w", encoding="utf-8") as f:
        json.dump(all_files, f, indent=2)

    print(f"\nTotal files pulled: {len(all_files)}")
    print("Saved to data/repo_files.json")

if __name__ == "__main__":
    main()