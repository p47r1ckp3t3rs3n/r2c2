# r2c
This is a script written in Python that migrates a Redmine issue into a ClickUp ticket.

### Capabilities
The script will create a ClickUp task with name and description of the provided Redmine issue. It will also set the Redmine issue status to "Migrated" and cross-link the Redmine issue and the ClickUp task.

### Installation
You can use Homebrew to install the script:
```
brew tap bajtyngier/r2c
brew install r2c
```
In order to update to latest version:
```
brew update
brew reinstall r2c
```
### Usage
In order to use the script, simply run the command:
```
r2c
```
#### Parameters
The script will prompt you to provide.
* Redmine issue ID
* ClickUp list ID of where to create a task - you can get it from the URL once you open a ClickUp list in a browser

You can also run the command with the above parameters included:
```
r2c --id <redmine_issue_id> --list <clickup_list_id>
```

#### Configuration
The script will also prompty you to provide some configuration. You will have to enter it only once and it will be saved in a JSON file for subsequent use.
* Redmine API Key - everyone has a personal key in "My account" > "API access key"
* ClickUp API Key - everyone has a personal key in "Settings" > "Apps" > "API Token"
* ClickUp Team ID - you can get it from the URL once you open any ClickUp page in a browser

### Troubleshooting

#### `ModuleNotFoundError: No module names 'requests'`
In case you are facing this error, it means you need to install Python's `requests` module. You can install it by running the command:
```
pip3 install requests
```
If the above command triggers an environment related error, you can install `requests` via a virtual environment. Follow the steps below.

1. First, create and activate a virtual environment:
```
python3 -m venv myenv
source myenv/bin/activate
```
2. Then, install `requests`:
```
pip install requests
```
3. Lastly, deactivate the virtual environment:
```
deactivate
```