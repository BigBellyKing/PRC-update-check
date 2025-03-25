# prcboard-checker.py
import os
import hashlib
import requests
from github import Github

# Configuration
URL = "https://www.prcboard.com/room-assignments-april-2025-electronics-engineer-licensure-exam-ece-electronics-technician-licensure-exam-ect"
GIST_ID = os.environ['GIST_ID']  # GitHub secret
DISCORD_WEBHOOK = os.environ['DISCORD_WEBHOOK']  # GitHub secret
GH_TOKEN = os.environ['GH_TOKEN']  # GitHub secret

def get_current_hash():
    response = requests.get(URL)
    response.raise_for_status()
    return hashlib.sha256(response.content).hexdigest()

def update_gist(new_hash):
    g = Github(GH_TOKEN)
    gist = g.get_gist(GIST_ID)
    gist.edit(
        description="PRC Board Update Checker",
        files={list(gist.files.keys())[0]: github.InputFileContent(new_hash)}
    )

def get_previous_hash():
    g = Github(GH_TOKEN)
    gist = g.get_gist(GIST_ID)
    return list(gist.files.values())[0].content.strip()

def send_discord_notification():
    payload = {
        "content": f"📢 Update detected on PRC Board website!\n{URL}"
    }
    requests.post(DISCORD_WEBHOOK, json=payload)

def main():
    current_hash = get_current_hash()
    try:
        previous_hash = get_previous_hash()
    except Exception as e:
        print(f"Error getting previous hash: {e}")
        previous_hash = ""
    
    if current_hash != previous_hash:
        print("Change detected!")
        send_discord_notification()
        update_gist(current_hash)
    else:
        print("No changes detected")

if __name__ == "__main__":
    main()