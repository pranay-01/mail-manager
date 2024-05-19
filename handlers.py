import logging
from typing import List, Dict, Any

from db import Email, get_db_engine, get_session, create_tables
from email.utils import parsedate_to_datetime
from rule_manager import apply_rules
from authn import Service
from sqlalchemy import Engine

logger = logging.getLogger(__name__)


def store_emails(message_data: List[Dict[str, Any]], db_engine: Engine):
    """
    function to store emails into the database.

    :param message_data:
    :param db_engine:
    :return:
    """
    logger.info("storing emails into db...")

    create_tables(db_engine)
    session = get_session(db_engine)
    try:
        for msg in message_data:
            msg_headers = {header["name"]: header["value"] for header in msg["payload"]["headers"]}
            email_obj = Email(
                from_addr=msg_headers.get("From"),
                to_addr=msg_headers.get("To"),
                message_id=msg["id"],
                date=parsedate_to_datetime(msg_headers.get("Date")),
                message=msg["snippet"],
                subject=msg_headers.get("Subject", "")
            )
            session.add(email_obj)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.exception(f"error pushing data into db, {e}", exc_info=True)
    finally:
        session.close()


def fetch_emails(engine: Engine):
    """
    function to fetch emails using the gmail api.

    :param engine:
    :return:
    """
    logger.info("fetching emails...")

    result = Service.users().messages().list(userId="me", maxResults=20).execute()
    messages = result.get("messages")
    if not messages:
        logger.info("no emails found, terminating process...")
        return

    message_data = []
    batch = Service.new_batch_http_request()

    def callback(request, response, err):
        if err:
            logger.exception(err, exc_info=True)
        else:
            message_data.append(response)

    for message in messages:
        batch.add(Service.users().messages().get(userId="me", id=message["id"]), callback)
    batch.execute()

    if not message_data:
        logger.info("no emails found, terminating process...")
        return

    store_emails(message_data, engine)


def start_processing():
    """
    initial trigger function to start the process of fetching emails and applying rules on them.

    """
    logger.info("init...")

    db_engine = get_db_engine()

    fetch_emails(db_engine)

    apply_rules("rules.json", db_engine)




