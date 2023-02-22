import os


VKAPP_TOKEN = os.getenv('PRISCILLA_EF_VKAPP_TOKEN')
TGBOT_TOKEN = os.getenv('PRISCILLA_EF_TGBOT_TOKEN')
TG_API_ID = os.getenv('TG_API_ID')
TG_API_HASH = os.getenv('TG_API_HASH')

TG_CHANNEL_NAME = 'ptestbot777'


VK_GROUP_ID = -208947227  # ID of VK group/channel/wall


VK_API_VERSION = '5.131'


assert VKAPP_TOKEN is not None, 'VK token not found'
assert TGBOT_TOKEN is not None, 'Telegram Bot token not found'
assert TG_API_ID is not None, 'Telegram api_id not found'
assert TG_API_HASH is not None, 'Telegram api_hash not found'
assert VK_GROUP_ID < 0, 'Group ID must be negative'