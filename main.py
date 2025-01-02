#!/usr/bin/env python3

import argparse

from config import Config
from redmine.redmine import Redmine
from clickup.clickup import ClickUp

config = Config()

def migrate_issue(issue_id, list_id):
	print(f":::::::::: Start migration of Redmine issue {issue_id} ::::::::::")
	redmine = Redmine(issue_id)
	redmine.get_issue(config.redmine_api_key)
	if not redmine.issue:
	    return
	clickup = ClickUp()
	clickup.create_task(list_id, redmine, config.clickup_api_key, config.clickup_team_id)
	if clickup.task_id:
	    redmine.close_issue(clickup.task_id, config.redmine_api_key)

def main():
	# Load configuration with essential api keys and ids
	config.load()
	# Parse command parameters
	parser = argparse.ArgumentParser()
	parser.add_argument("--id", type=int)
	parser.add_argument("--list", type=int)
	args = parser.parse_args()
	issue_id = args.id
	list_id = args.list
	# Request missing parameters
	if not issue_id:
		issue_id = int(input("Enter a Redmine issue ID: "))
	if not list_id:
		list_id = int(input("Enter a ClickUp list ID: "))
	# Trigger migration
	migrate_issue(issue_id, list_id)

if __name__ == "__main__":
	main()