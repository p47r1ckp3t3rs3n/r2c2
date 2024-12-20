import json
import requests

class ClickUpAPI:

	def __init__(self):
		self.base_url= "https://api.clickup.com/api/v2"

	def create_task(self, list_id, team_id, api_key, payload):
		url = f"{self.base_url}/list/{list_id}/task?team_id={team_id}"
		response = requests.post(url, headers=self.build_headers(api_key), json=payload)
		if response.status_code in (200, 201):
			print(" > Success!")
			return response.json()
		else:
			print(" * Failed to create a task")
			return None

	def update_task(self, task_id,field_id, team_id, api_key, payload):
		url = f"{self.base_url}/task/{task_id}/field/{field_id}?team_id={team_id}"
		response = requests.post(url, headers=self.build_headers(api_key), json=payload)
		if response.status_code in (200, 201):
			print(" > Success!")
		else:
			print(" * Failed to update the task")

	def build_headers(self, api_key):
		return {
			"Authorization": f"{api_key}",
			"accept": f"application/json",
			"content-type": f"application/json"
		}