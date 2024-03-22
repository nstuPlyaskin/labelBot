import os
import json

whitelist_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'whitelist.json')

def is_user_allowed(user_id):
    with open(whitelist_path, "r") as f:
        whitelist = json.load(f)
    allowed_users = whitelist.get("allowed_users", [])
    return user_id in allowed_users
