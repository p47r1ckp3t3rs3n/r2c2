import os
import json
import requests
import argparse

REDMINE_BASE_URL = "https://tickets.vivino.com"
CLICKUP_BASE_URL = "https://api.clickup.com/api/v2"
CONFIG_FILE = "r2c.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file not found. Creating a new one.")
        config = {}
    else:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

    required_keys = ["redmine_api_key", "clickup_api_key"]
    for key in required_keys:
        if key not in config or not config[key]:
            config[key] = input(f"Enter {key}: ")

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    return config

def get_issue_from_redmine(issue_id, api_key):
    print(f"Retrieving the Redmine issue...")
    url = f"{REDMINE_BASE_URL}/issues/{issue_id}.json"
    headers = {
        "X-Redmine-API-Key": api_key
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"Success!")
        return response.json()["issue"]
    else:
        print(f"Failed to retrieve the Redmine issue: {response.status_code}, {response.text}")
        return None

def close_issue_in_redmine(issue_id, task_id, api_key):
    print(f"Closing the Redmine issue...")
    url = f"{REDMINE_BASE_URL}/issues/{issue_id}.json"
    headers = {
        "content-type": f"application/json",
        "X-Redmine-API-Key": api_key
    }
    payload = {
        "issue": {
            "status_id": 20,
            "notes": f"Migrated to a ClickUp task https://app.clickup.com/t/{task_id}"
        }
    }
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code in (200, 204):
        print(f"Success! {REDMINE_BASE_URL}/issues/{issue_id}")
    else:
        print(f"Failed to close the Redmine issue ({response.status_code}) {REDMINE_BASE_URL}/issues/{issue_id}")

def create_task_in_clickup(list_id, issue, api_key, team_id):
    print(f"Creating a ClickUp task...")
    url = f"{CLICKUP_BASE_URL}/list/{list_id}/task?team_id={team_id}"
    headers = {
        "Authorization": f"{api_key}",
        "accept": f"application/json",
        "content-type": f"application/json"
    }
    title = issue.get("subject")
    description = issue.get("description")
    description = f"Migrated from a Redmine ticket\nhttps://tickets.vivino.com/issues/{issue.get("id")}\n\n" +  description
    payload = {
        "name": title,
        "description": description
    }
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    if response.status_code in (200, 201):
        task_id = response_data.get("id")
        print(f"Success! https://app.clickup.com/t/{task_id}")
    else:
        print(f"Failed to create a ClickUp task ({response.status_code})")

def transfer_task(issue_id, list_id):
    config = load_config()
    redmine_api_key = config["redmine_api_key"]
    clickup_api_key = config["clickup_api_key"]
    clickup_team_id = config["clickup_team_id"]
    issue = get_issue_from_redmine(issue_id, redmine_api_key)
    if not issue:
        return
    
    task_id = create_task_in_clickup(list_id, issue, clickup_api_key, clickup_team_id)
    close_issue_in_redmine(issue_id, task_id, redmine_api_key)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int)
    parser.add_argument("--list", type=int)
    args = parser.parse_args()
    
    issue_id = args.id
    list_id = args.list
    if not issue_id:
        issue_id = int(input("Enter a Redmine issue ID: "))
    if not list_id:
        list_id = int(input("Enter a ClickUp list ID: "))
    transfer_task(issue_id, list_id)

if __name__ == "__main__":
    main()