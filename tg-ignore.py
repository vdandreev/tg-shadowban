# License: GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html
# Do whatever you want with this, take this code as is, no guarantees of any kind whatsoever

from pyrogram import Client, idle
from pyrogram.handlers import MessageHandler
import argparse
import yaml
import logging

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

def clear_history(client, config):
    dialogs = client.get_dialogs(pinned_only=True)
    dialog_chunk = client.get_dialogs()
    while len(dialog_chunk) > 0:
        dialogs.extend(dialog_chunk)
        dialog_chunk = client.get_dialogs(offset_date=dialogs[-1].top_message.date)

    chat_objects = [d.chat for d in dialogs]
    for chat in chat_objects:
        if chat.title not in config['watch_groups']:
            continue
        LOGGER.info(f"Deleteing all messages from {config['shadowban_users']} in chat {chat['title']}")

        msg_span = []
        for msg in client.search_messages(chat.id, offset=0, limit=int(config['offset_messages'])):
            user = msg.from_user
            if user.first_name in config['shadowban_users'] \
                    or user.last_name in config['shadowban_users'] \
                    or user.username in config['shadowban_users']:
                msg_span.append(msg.message_id)

        LOGGER.info(f"Found {len(msg_span)} unwanted messages in {chat.title}, deleting")
        client.delete_messages(chat_id=chat.id, message_ids=msg_span)


def make_handler(config):
    grouplist = config['watch_groups']
    banlist = config['shadowban_users']
    def handler(client, msg):
        chat = msg.chat
        user = msg.from_user

        if chat.title not in grouplist:
            return

        if user.first_name in banlist \
                or user.last_name in banlist \
                or user.username in banlist:
            client.delete_messages(chat_id = chat.id, message_ids=[msg.message_id])
            LOGGER.info(f"deleted message from '{user.first_name} {user.last_name}': {msg.text}")
    return MessageHandler(handler)

def main():
    config = configure()
    app = Client("client", api_id=config['app_id'], api_hash=config['app_hash'])
    app.add_handler(make_handler(config))

    app.start()
    clear_history(app, config)
    idle()
    app.stop()

if __name__ == '__main__':
    main()
