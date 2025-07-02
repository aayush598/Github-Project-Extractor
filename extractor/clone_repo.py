# extractor/clone_repo.py

import os
import subprocess

def clone_repo(repo_url, destination="cloned_repos"):
    if not os.path.exists(destination):
        os.makedirs(destination)

    repo_name = repo_url.rstrip("/").split("/")[-1]
    local_path = os.path.join(destination, repo_name)

    if os.path.exists(local_path):
        print(f"[INFO] Repo already cloned at {local_path}")
        return local_path

    try:
        subprocess.run(["git", "clone", repo_url, local_path], check=True)
        print(f"[SUCCESS] Cloned repo to {local_path}")
        return local_path
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Cloning failed: {e}")
        return None
