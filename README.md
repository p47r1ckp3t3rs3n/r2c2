# r2c
This is a script written in Python that migrates a Redmine issue into a ClickUp ticket.

### Capabilities
The script will create a ClickUp task with name and description of the provided Redmine issue. It will also set the Redmine issue status to "Migrated" and cross-link the Redmine issue and the ClickUp task.

### Installation
You can use Homebrew to install the script:
```
brew tap bajtyngier/homebrew-r2c
brew install r2c
```
### Usage
In order to use the script, simply run the command:
```
r2c
```
##### Parameters
The script will prompt you to provide.
* Redmine issue ID
* ClickUp list ID of where to create a task - you can get it from the URL once you open a ClickUp list in a browser
##### Configuration
The script will also prompty you to provide some configuration. You will have to enter it only once and it will be saved in a JSON file for subsequent use.
* Redmine API Key - everyone has a personal key in "My account" > "API access key"
* ClickUp API Key - everyone has a personal key in "Settings" > "Apps" > "API Token"
* ClickUp Team ID - you can get it from the URL once you open any ClickUp page in a browser