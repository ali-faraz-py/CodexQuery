from github import Github
import os
import json

# Repos to pull from, in your chronological order
REPOS = [
    "ali-faraz-py/Python-CurrencyConverter",
    "ali-faraz-py/python-weather-app",
    "ali-faraz-py/PersonalFinanceTracker",
    "ali-faraz-py/AetherQuant",
    "ali-faraz-py/DiabetesDetector",
    "ali-faraz-py/deepfake-detector",
    "ali-faraz-py/Picassify",
    "ali-faraz-py/NeuralLens",
    "ali-faraz-py/SentimentSense",
]

# File types worth embedding — code and documentation, not binaries/configs
INCLUDE_EXTENSIONS = {".py", ".md", ".txt"}

# Folders to skip entirely — dependencies, build artifacts, version control internals
SKIP_DIRS = {"venv", "node_modules", ".git", "__pycache__", ".next"}

def should_include(path):
    if any(skip in path.split("/") for skip in SKIP_DIRS):
        return False
    return any(path.endswith(ext) for ext in INCLUDE_EXTENSIONS)

def fetch_repo_files(gh, repo_name):
    repo = gh.get_repo(repo_name)
    contents = repo.get_contents("")
    files = []

    while contents:
        item = contents.pop(0)
        if item.type == "dir":
            contents.extend(repo.get_contents(item.path))
        elif should_include(item.path):
            try:
                text = item.decoded_content.decode("utf-8")
                files.append({
                    "repo": repo_name.split("/")[-1],
                    "path": item.path,
                    "content": text
                })
            except Exception as e:
                print(f"Skipped {item.path}: {e}")

    return files

def main():
    gh = Github()
    all_files = []

    for repo_name in REPOS:
        print(f"Fetching {repo_name}...")
        files = fetch_repo_files(gh, repo_name)
        print(f"  → {len(files)} files")
        all_files.extend(files)

    os.makedirs("data", exist_ok=True)
    with open("data/repo_files.json", "w", encoding="utf-8") as f:
        json.dump(all_files, f, indent=2)

    print(f"\nTotal files pulled: {len(all_files)}")
    print("Saved to data/repo_files.json")

if __name__ == "__main__":
    main()