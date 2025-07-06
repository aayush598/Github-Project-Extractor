import os
import subprocess

def clone_repo(repo_url, destination="cloned_repos", clone_type="readme"):
    """
    Clones a Git repository.

    Args:
        repo_url (str): The URL of the Git repository.
        destination (str): The directory where the repository will be cloned.
                           Defaults to "cloned_repos".
        clone_type (str): Specifies what to clone. 
                          - "readme": Clones only the readme.md file (default).
                          - "full": Clones the complete repository.
    Returns:
        str or None: The path to the cloned repository or None if cloning fails.
    """
    if not os.path.exists(destination):
        os.makedirs(destination)

    repo_name = repo_url.rstrip("/").split("/")[-1]
    local_path = os.path.join(destination, repo_name)

    if os.path.exists(local_path):
        print(f"[INFO] Repo already cloned at {local_path}")
        return local_path

    try:
        if clone_type == "readme":
            print(f"[INFO] Cloning only readme.md from {repo_url} to {local_path}")
            # Initialize an empty repository
            subprocess.run(["git", "init", local_path], check=True)
            # Add the remote
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=local_path, check=True)
            # Enable sparse-checkout
            subprocess.run(["git", "config", "core.sparseCheckout", "true"], cwd=local_path, check=True)
            # Define what to checkout
            sparse_checkout_path = os.path.join(local_path, ".git", "info", "sparse-checkout")
            with open(sparse_checkout_path, "w") as f:
                f.write("readme.md\n")
            # Pull only the specified file
            subprocess.run(["git", "pull", "--depth=1", "origin", "main" if "github.com" in repo_url else "master"], cwd=local_path, check=True)
            print(f"[SUCCESS] Cloned readme.md to {local_path}")
        elif clone_type == "full":
            print(f"[INFO] Cloning full repo from {repo_url} to {local_path}")
            subprocess.run(["git", "clone", repo_url, local_path], check=True)
            print(f"[SUCCESS] Cloned full repo to {local_path}")
        else:
            print(f"[ERROR] Invalid clone_type '{clone_type}'. Use 'readme' or 'full'.")
            return None
        return local_path
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Cloning failed: {e}")
        return None