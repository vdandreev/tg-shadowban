# License: GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html
# Do whatever you want with this, take this code as is, no guarantees of any kind whatsoever

from pyrogram import Client, idle
from pyrogram.handlers import MessageHandler
import argparse
import yaml
import logging
import time

logging.basicConfig(
        level="INFO",
        datefmt="%d-%b-%Y %H:%M:%S",
        format="%(asctime)s:%(levelname)s %(message)s",
    )
LOGGER = logging.getLogger(__name__)


def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="local/config.yaml")
    args = parser.parse_args()
    with open(args.config, "r") as f:
        config_vars = yaml.load(f,  Loader=yaml.FullLoader)

    #TODO: merge it with env vars, add ability to configure from cmdline etc
    # ^ if it is really necessary though
    return config_vars


def init_tg(config):
    app = Client("client", api_id=config['app_id'], api_hash=config['app_hash'])

    #TODO: add full authz routine to handle predefined sessions, to enable this thing to dockerize
    app.start()
    app.add_handler(get_handler(config['shadowban_users'], config['watch_groups']))

    return app


def clean_history(client, config):
    dialogs = client.get_dialogs(pinned_only=True)
    dialog_chunk = client.get_dialogs()
    while len(dialog_chunk) > 0:
        dialogs.extend(dialog_chunk)
        dialog_chunk = client.get_dialogs(offset_date=dialogs[-1].top_message.date)

    chat_objects = [d.chat for d in dialogs]

    #TODO:  for sopme massive housekeeping, this stuff should be reworked as async multiprocessing actions
    for chat in chat_objects:
        if chat.title not in config['watch_groups']:
            continue
        LOGGER.info(f"Deleteing historical messages from {config['shadowban_users']} in chat {chat['title']}")
        msg_span = []
        for msg in client.search_messages(chat.id, offset=0, limit=int(config['offset_messages'])):
            if filter_user(msg.from_user, config['shadowban_users']):
                msg_span.append(msg.message_id)

        LOGGER.info(f"Found {len(msg_span)} unwanted messages in {chat.title}, deleting")
        client.delete_messages(chat_id=chat.id, message_ids=msg_span)


def get_handler(users, groups):
    def msg_handler(client, msg):
        chat = msg.chat
        user = msg.from_user

        if chat.title not in groups:
            return

        if filter_user(msg.from_user, users):
            client.delete_messages(chat_id=chat.id, message_ids=[msg.message_id])
            LOGGER.info(f"Deleted message from '{user.first_name} {user.last_name}': {msg.text}")

    return MessageHandler(msg_handler)


def filter_user(msg_user, users):
    if msg_user.first_name in users \
            or msg_user.last_name in users \
            or msg_user.username in users:
        return True
    else:
        return False


if __name__ == "__main__":
    config = configure()
    client = init_tg(config)
    clean_history(client, config)
    idle()
