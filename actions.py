import logging

from typing import List
from utils import RegexDict
from authn import Service

logger = logging.getLogger(__name__)


def mark_as_read_or_unread(action_items: List[str], **kwargs):
    """
    function to apply (read/unread)action on emails using gmail api

    :param action_items:
    :param kwargs:
    :return:
    """
    if kwargs["label"] == "READ":
        body = {"removeLabelIds": ["UNREAD"]}
    elif kwargs["label"] == "UNREAD":
        body = {"addLabelIds": ["UNREAD"]}
    else:
        raise Exception("invalid action to apply")
    body["ids"] = action_items

    Service.users().messages().batchModify(userId="me", body=body).execute()


def move_to_folder(action_items: List[str], **kwargs):
    """
    function to apply move emails action using gmail api

    :param action_items:
    :param kwargs:
    :return:
    """
    labels = Service.users().labels().list(userId="me").execute()["labels"]
    label_dict = {label_dict["id"]: label_dict["name"].lower() for label_dict in labels}
    if not kwargs["label"].lower() in label_dict.values():
        raise Exception("cannot move to the folder", kwargs["label"])

    label = [key for key, value in label_dict.items() if value == kwargs["label"].lower()]
    Service.users().messages().batchModify(userId="me", body={"removeLabelIds": ["INBOX"], "ids": action_items}).execute()
    Service.users().messages().batchModify(userId="me", body={"addLabelIds": label[0], "ids": action_items}).execute()


ACTION_DISPATCHER = RegexDict({
    "MARK_AS_READ": mark_as_read_or_unread,
    "MARK_AS_UNREAD": mark_as_read_or_unread,
    r"^MOVE_TO_FOLDER_.*": move_to_folder
})


def run_actions(actions: List[str], action_items: List[str]):
    """
    dispatcher function to decide on the appropriate action to run on emails
    :param actions:
    :param action_items:
    :return:
    """
    logger.info("performing actions...")
    for action in actions:
        try:
            kwargs = {"label": action.split("_")[-1]}
            ACTION_DISPATCHER[action](action_items, **kwargs)
        except KeyError:
            raise Exception("action not implemented/recognized")

    logger.info("process complete.")
