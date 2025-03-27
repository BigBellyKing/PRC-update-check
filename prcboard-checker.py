# prcboard-checker.py
import os
import requests
from bs4 import BeautifulSoup
from github import Github, InputFileContent

# Configuration
URL = "https://www.prcboard.com/room-assignments-april-2025-electronics-engineer-licensure-exam-ece-electronics-technician-licensure-exam-ect"
GIST_ID = os.environ['GIST_ID']
DISCORD_WEBHOOK = os.environ['DISCORD_WEBHOOK']
GH_TOKEN = os.environ['GH_TOKEN']

def check_for_metro_manila_link():
    response = requests.get(URL)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    metro_manila_item = soup.find('li', string='Metro Manila')
    
    if not metro_manila_item:
        raise ValueError("Metro Manila list item not found on the page")
    
    link = metro_manila_item.find('a')
    return link['href'] if link else None

def update_gist_state(new_state):
    g = Github(GH_TOKEN)
    gist = g.get_gist(GIST_ID)
    gist.edit(
        description="PRC Board Update Checker",
        files={list(gist.files.keys())[0]: InputFileContent(new_state)}
    )

def get_previous_state():
    g = Github(GH_TOKEN)
    gist = g.get_gist(GIST_ID)
    content = list(gist.files.values())[0].content.strip()
    return content.split('|', 1) if content else ['', '']

def send_discord_notification(link):
    payload = {
        "content": f"?? Metro Manila Room Assignments Available!\nDownload link: {link}"
    }
    requests.post(DISCORD_WEBHOOK, json=payload)

def main():
    try:
        current_link = check_for_metro_manila_link()
        current_state = f"{bool(current_link)}|{current_link or ''}"
        
        previous_has_link, previous_link = get_previous_state()
        
        # Only notify if link appears for the first time
        if current_link and not previous_has_link.lower() == 'true':
            print("New Metro Manila link detected!")
            send_discord_notification(current_link)
            update_gist_state(current_state)
        else:
            print("No new links detected")
            
    except ValueError as e:
        print(f"Error: {str(e)}")
        send_discord_notification("?? Website structure changed! Could not find Metro Manila item")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()