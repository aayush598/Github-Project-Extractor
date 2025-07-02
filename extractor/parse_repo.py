# extractor/parse_repo.py

import os

# Define file types you care about
TEXT_EXTENSIONS = [".md", ".py", ".js", ".ts", ".html", ".css", ".json", ".txt"]

def is_text_file(filename):
    return any(filename.endswith(ext) for ext in TEXT_EXTENSIONS)

def parse_repo(repo_path):
    repo_data = {
        "repo_path": repo_path,
        "readme": "",
        "files": []  # List of dicts: { "path": ..., "content": ... }
    }

    for root, _, files in os.walk(repo_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, repo_path)

            # Readme extraction
            if file.lower() == "readme.md":
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        repo_data["readme"] = f.read()
                except Exception as e:
                    print(f"[ERROR] Reading README: {e}")

            # Text/code file extraction
            elif is_text_file(file):
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        repo_data["files"].append({
                            "path": rel_path,
                            "content": content
                        })
                except Exception as e:
                    print(f"[ERROR] Reading file {rel_path}: {e}")

    return repo_data
