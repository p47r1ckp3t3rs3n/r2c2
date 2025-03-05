import sys
import os
import json

class Config:
	def load(self):
		script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
		config_file = os.path.join(script_dir, "r2c2.json")
		if not os.path.exists(config_file):
			print(f"Config file not found. Creating a new one.")
			config = {}
		else:
			with open(config_file, "r") as f:
				config = json.load(f)
		required_keys = ["redmine_api_key", "clickup_api_key", "clickup_team_id"]
		for key in required_keys:
			if key not in config or not config[key]:
				config[key] = input(f"Enter {key}: ")
		with open(config_file, "w") as f:
			json.dump(config, f, indent=4)
		self.redmine_api_key = config["redmine_api_key"]
		self.clickup_api_key = config["clickup_api_key"]
		self.clickup_team_id = config["clickup_team_id"]