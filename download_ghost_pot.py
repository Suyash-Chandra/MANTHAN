from huggingface_hub import snapshot_download
import os

repo_id = "PINGEcosystem/sss-crab-pot-detection-ds"
local_dir = os.path.abspath(os.path.join("data", "raw", "ghost_pot"))
hf_token = os.environ.get("HF_TOKEN", "")

print(f"Downloading dataset {repo_id} to {local_dir}...")
try:
    snapshot_download(
        repo_id=repo_id,
        repo_type="dataset",
        local_dir=local_dir,
        token=hf_token
    )
    print("Download completed successfully.")
except Exception as e:
    print(f"Error downloading dataset: {e}")
