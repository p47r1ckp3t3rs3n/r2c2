import json
import requests

class RedmineAPI:

	def __init__(self):
		self.base_url= "https://tickets.vivino.com"

	def get_issue(self, issue_id, api_key):
		response = requests.get(self.build_url(issue_id), headers=self.build_headers(api_key))
		if response.status_code == 200:
			print(" > Success!")
			return response.json().get("issue")
		else:
			print(" * Failed to get the issue")
			return None

	def update_issue(self, issue_id, api_key, payload):
		response = requests.put(self.build_url(issue_id), headers=self.build_headers(api_key), json=payload)
		if response.status_code in (200, 204):
			print(" > Success!")
		else:
			print(" * Failed to update the issue")

	def build_url(self, issue_id):
		return f"{self.base_url}/issues/{issue_id}.json"

	def build_headers(self, api_key):
		return {
			"X-Redmine-API-Key": api_key
		}