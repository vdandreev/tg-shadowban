# License: GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html
# Do whatever you want with this, take this code as is, no guarantees of any kind whatsoever

from pyrogram import Client
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


def init_tg(config):
    app = Client("client", api_id=config['app_id'], api_hash=config['app_hash'])

    #TODO: add full authz routine to handle predefined sessions, to enable this thing to dockerize
    app.start()

    return app


def run_routine(client, config):
    dialogs = client.get_dialogs(pinned_only=True)
    dialog_chunk = client.get_dialogs()
    while len(dialog_chunk) > 0:
        dialogs.extend(dialog_chunk)
        dialog_chunk = client.get_dialogs(offset_date=dialogs[-1].top_message.date)

    chat_objects = [d.chat for d in dialogs]

    #TODO:  for sopme massive housekeeping, this stuff should be reworked as async multiprocessing actions
    while True:
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


if __name__ == "__main__":
    config = configure()
    client = init_tg(config)
    run_routine(client, config)
