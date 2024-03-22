import json
import os

whitelist_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'whitelist.json')
help_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'help.json')

def is_user_allowed(user_id):
    with open(whitelist_path, "r", encoding='utf-8') as f:
        whitelist = json.load(f)
    allowed_users = whitelist.get("allowed_users", [])
    return user_id in allowed_users

def get_help_text(user_id):
    with open(help_path, "r", encoding='utf-8') as f:
        help_data = json.load(f)
    if is_user_allowed(user_id):
        return '\n'.join(help_data.get("helpWhitelist", []))
    else:
        return '\n'.join(help_data.get("helpRegular", []))

def show_help_cmd(bot, message):
    user_id = message.from_user.id
    help_text = get_help_text(user_id)
    bot.send_message(message.chat.id, help_text)