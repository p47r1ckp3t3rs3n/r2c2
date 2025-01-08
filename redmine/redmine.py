from redmine.redmine_api import RedmineAPI

class Redmine:

	def __init__(self, issue_id):
		self.api = RedmineAPI()
		self.issue_id = issue_id

	def get_issue(self, api_key):
		print(f"Retrieving the Redmine issue")
		self.issue = self.api.get_issue(self.issue_id, api_key)

	def get_custom_field_value(self, field_id):
		custom_fields = self.issue.get("custom_fields")
		field = next((field for field in custom_fields if field.get('id') == field_id), None)
		if field is None:
			return None
		return field.get("value")

	def close_issue(self, task_id, api_key):
		print(f"Closing the Redmine issue")
		task_url = f" https://app.clickup.com/t/{task_id}" if task_id else ""
		payload = {
			"issue": {
				"status_id": 20,
				"notes": f"Migrated to a ClickUp task{task_url}"
			}
		}
		self.api.update_issue(self.issue_id, api_key, payload)
		print(f"✅ Migrated to ClickUp task{task_url}")