from clickup.clickup_api import ClickUpAPI

class ClickUp:

	def __init__(self):
		self.api = ClickUpAPI()

	def create_task(self, list_id, redmine, api_key, team_id):
		print(f"Creating a ClickUp task")
		issue = redmine.issue
		title = issue.get("subject")
		description = issue.get("description")
		description = f"Migrated from a Redmine ticket\nhttps://tickets.vivino.com/issues/{issue.get("id")}\n\n" +  description
		payload = {
			"name": title,
			"description": description,
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
			1: 1012, #bug -> bug
			2: 0, #feature -> task
			5: 0, #automation -> task
			6: 1014, #operation -> operation
			7: 0, #ideas -> task
			8: 1016, #incident -> incident
		}
		return trackers.get(value, 0)

	def set_resource(self, task, redmine, api_key, team_id):
		print(f"Setting the resource based on repository")
		value = redmine.get_custom_field_value(41)[0]
		if not value:
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
			"Web": ["ruby-lib-api","ruby-merchant-admin","ruby-merchants","ruby-order-admin","ruby-user-admin","ruby-web","ruby-wine-admin","js-react-common-ui","js-web","js-web-common"],
			"Backend": ["go-api","go-common","go-content","go-oauth","go-premium-services","go-promotions-api","go-ranks","go-recommender-api","go-retail","go-sendout","go-wine-matching","go-tools"]
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
