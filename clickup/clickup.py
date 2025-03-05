import re
from clickup.clickup_api import ClickUpAPI

def convert_redmine_to_clickup(text):
    """Convert Redmine Textile formatting to ClickUp Markdown while ensuring correct spacing and removing templates."""
    if not text:
        return ""

    # **Remove excessive blank lines to keep things tight**
    text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with a single newline

    # **Remove Redmine template sections (exact match)**
    text = re.sub(r'(?m)^h3\. Testing Notes\n_Mention the impacted.*?_?\n\n?', '', text, flags=re.DOTALL)
    text = re.sub(r'(?m)^h3\. Accessibility IDs\nThese are the locators.*?\n\n?', '', text, flags=re.DOTALL)
    text = re.sub(r'(?m)^h2\. Pull Requests\n\* https://github.com/Vivino/\n\n?', '', text, flags=re.DOTALL)
    text = re.sub(r'(?m)^h2\. Release Checks\n<!-- MENTION ANY SPECIAL.*?-->\n\n?', '', text, flags=re.DOTALL)
    text = re.sub(r'(?m)^h3\. Stack Trace\n<pre>\n<!-- TRACE -->\n</pre>\n\n?', '', text, flags=re.DOTALL)
    text = re.sub(r'(?m)^h3\. Analysis\n<!-- INFORMATION ON WHAT CAUSED THE BUG -->\n\n?', '', text, flags=re.DOTALL)

    # **Convert Headers (h1. → #, h2. → ##, etc.)**
    text = re.sub(r'(?m)^h1\.\s*(.*)', r'# \1', text)
    text = re.sub(r'(?m)^h2\.\s*(.*)', r'## \1', text)
    text = re.sub(r'(?m)^h3\.\s*(.*)', r'### \1', text)
    text = re.sub(r'(?m)^h4\.\s*(.*)', r'#### \1', text)

    # **Ensure text follows headers immediately (no blank lines between headers and content)**
    text = re.sub(r'(?m)(#+ .*)\n+', r'\1\n', text)

    # **Convert Bold (**bold**) but avoid list formatting**
    text = re.sub(r'(?<!\*)\*([^\*\n]+)\*(?!\*)', r'**\1**', text)

    # **Convert Italics `_text_` → `*text*`, but avoid breaking `_table_name_`**
    text = re.sub(r'(?<!\w)_(?!_)([^_\n]+)_(?!_)(?!\w)', r'*\1*', text)

    # **Fix Bullet Lists (`*` → `-`)**
    text = re.sub(r'(?m)^\*\s+', '- ', text)  # Single `*` becomes `-`
    text = re.sub(r'(?m)^\*\*\s+', '  - ', text)  # Double `**` becomes indented bullet

    # **Fix Numbered Lists (`# Step → 1. Step`)**
    text = re.sub(r'(?m)^\#\s+', '1. ', text)

    # **Fix Nested Numbered Lists (`#*` → `  1.` for proper ClickUp rendering)**
    text = re.sub(r'(?m)^\#\*\s+', '  1. ', text)

    # **Ensure multiple numbered list items stay correctly formatted**
    text = re.sub(r'(?m)^(\d+)\.\s*\n+(\d+)\.', r'\1.\n\2.', text)

    # **Convert Blockquotes (`bq. Quote` → `> Quote`)**
    text = re.sub(r'(?m)^bq\.\s*(.*)', r'> \1', text)

    # **Convert Code Blocks (`<pre><code>` → ` ``` `)**
    text = re.sub(r'<pre><code[^>]*>', '```', text)  # Open code block
    text = re.sub(r'</code></pre>', '```', text)  # Close code block

    # **Convert Inline Code (`@code@` → ``code``)**
    text = re.sub(r'@([^@]+)@', r'`\1`', text)

    # **Convert Tables (`|| Header ||` → `| Header |`)**
    text = re.sub(r'(?m)^\|\| (.*?) \|\|$', r'| \1 |', text)
    text = re.sub(r'(?m)^\| (.*?) \|$', r'| \1 |', text, flags=re.MULTILINE)

    # **Convert Links (`"Text":URL` → `[Text](URL)`)**
    text = re.sub(r'"([^"]+)":(https?://[^\s]+)', r'[\1](\2)', text)

    # **Convert Collapsible Sections (`{{collapse(...)}}` → `> **Title**`)**
    text = re.sub(r'(?m){{collapse\((.*?)\)\s*', r'> **\1**\n', text)
    text = text.replace("}}", "\n")  # Close collapsible block

    # **Ensure "Suggested Solution" is properly formatted**
    text = re.sub(r'(?m)^### Suggested Solution\n\s*<!-- DESCRIPTION OF THE FIXES MADE -->\n?', '### Suggested Solution\n', text)

    # **Remove final trailing newlines**
    return text.strip()

class ClickUp:

    def __init__(self):
        self.api = ClickUpAPI()

    def create_task(self, list_id, redmine, api_key, team_id):
        print(f"Creating a ClickUp task")
        issue = redmine.issue
        title = issue.get("subject")
        markdown_description = convert_redmine_to_clickup(issue.get("description"))

        # Ensure proper inline formatting for migrated message
        markdown_description = (
            f"_Migrated from a Redmine ticket -_ "
            f"[https://tickets.vivino.com/issues/{issue.get('id')}]"
            f"(https://tickets.vivino.com/issues/{issue.get('id')})\n\n"
            + markdown_description
        )

        payload = {
            "name": title,
            "markdown_description": markdown_description,  # Using markdown_description instead of description
            "custom_item_id": self.get_task_type(issue)
        }

        task = self.api.create_task(list_id, team_id, api_key, payload)
        if task:
            self.task_id = task.get("id")
            self.set_resource(task, redmine, api_key, team_id)
            self.set_automation(task, redmine, api_key, team_id)

    def get_task_type(self, issue):
        print(f"Getting the task type based on issue tracker")
        value = issue.get("tracker").get("id")
        if value is None:
            print(f" * Failed to get the issue tracker")
            return None
        trackers = {
            1: 1012,  # bug -> bug
            2: 0,     # feature -> task
            5: 0,     # automation -> task
            6: 1014,  # operation -> operation
            7: 0,     # ideas -> task
            8: 1016,  # incident -> incident
        }
        return trackers.get(value, 0)

    def set_resource(self, task, redmine, api_key, team_id):
        print(f"Setting the resource based on repository")
        field_value = redmine.get_custom_field_value(41)
        if not field_value:
            print(f" * Failed to get the repository")
            return None
        value = field_value[0]
        if value is None:
            print(f" * Failed to get the repository")
            return None
        field_id = "b5db13c7-2e07-4f52-b2a7-941abcd8dee0"
        resources = {
            "iOS": "4a49dd8c-4e4d-4827-965e-d5801386e493",
            "Android": "c9359502-a2f9-4d8b-994e-f4d1ee5f5146",
            "Web": "006d4929-177b-4edd-97f1-88c7149ef6ca",
            "Backend": "d12a5f55-1364-4d8e-a458-95afdca8b6b6"
        }
        repositories_map = {
            "iOS": ["iOS"],
            "Android": ["Android"],
            "Web": ["ruby-lib-api", "ruby-merchant-admin", "ruby-merchants", "ruby-order-admin", "ruby-user-admin", "ruby-web", "ruby-wine-admin", "js-react-common-ui", "js-web", "js-web-common"],
            "Backend": ["go-api", "go-common", "go-content", "go-oauth", "go-premium-services", "go-promotions-api", "go-ranks", "go-recommender-api", "go-retail", "go-sendout", "go-wine-matching", "go-tools"]
        }
        resource_key = None
        for key, repositories in repositories_map.items():
            if value in repositories:
                resource_key = key
                break
        payload = {
            "value": resources.get(key),
        }
        self.api.update_task(self.task_id, field_id, team_id, api_key, payload)

    def set_automation(self, task, redmine, api_key, team_id):
        print(f"Setting the blocks automation flag if available")
        value = redmine.get_custom_field_value(16)
        if value is None:
            print(f" * Failed to get the flag value")
            return None
        if value != "1":
            print(f" > Ignored for values other than 'Yes'")
            return None
        field_id = "e6bd7f7e-3b86-4d7d-91a0-f4c9f4654584"
        payload = {
            "value": True,
        }
        self.api.update_task(self.task_id, field_id, team_id, api_key, payload)
