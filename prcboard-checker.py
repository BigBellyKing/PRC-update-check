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

def check_for_update():
    response = requests.get(URL)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    target_element = soup.find('li', string='Metro Manila')
    
    if not target_element:
        raise Exception("Metro Manila list item not found in the page")
    
    # Check if the element has a hyperlink
    has_link = bool(target_element.find('a'))
    link = target_element.find('a')['href'] if has_link else None
    
    return has_link, link

def update_gist(new_state):
    g = Github(GH_TOKEN)
    gist = g.get_gist(GIST_ID)
    gist.edit(
        description="PRC Board Update Checker",
        files={list(gist.files.keys())[0]: InputFileContent(new_state)}
    )

def get_previous_state():
    g = Github(GH_TOKEN)
    gist = g.get_gist(GIST_ID)
    return list(gist.files.values())[0].content.strip()

def send_discord_notification(link):
    payload = {
        "content": f"🚨 Room assignments updated! \nDownload link: {link}"
    }
    requests.post(DISCORD_WEBHOOK, json=payload)

def main():
    try:
        current_has_link, current_link = check_for_update()
        current_state = f"{current_has_link}|{current_link or ''}"
        
        previous_state = get_previous_state()
        prev_has_link, prev_link = previous_state.split('|', 1)
        
        # Check if link state changed from no-link to has-link
        if current_has_link and not eval(prev_has_link):
            print("Update detected with link!")
            send_discord_notification(current_link)
            update_gist(current_state)
        else:
            print("No relevant changes detected")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        if "Metro Manila list item not found" in str(e):
            send_discord_notification("⚠️ Website structure changed! Manual check required")

if __name__ == "__main__":
    main()