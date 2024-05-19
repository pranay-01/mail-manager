import json
import logging
from functools import singledispatch
from datetime import timedelta, datetime
from typing import Dict, Union, List

from sqlalchemy import Engine

from actions import run_actions
from db import get_session, get_all_records, Email

logger = logging.getLogger(__name__)


@singledispatch
def evaluate_condition(payload_value, field_value, predicate) -> bool:
    """
    a single dispatch function to apply the appropriate rule depending on the value type.

    :param payload_value:
    :param field_value:
    :param predicate:
    :return:
    """
    raise NotImplementedError(f"predicates not implemented for this payload")


@evaluate_condition.register
def _(payload_value: str, field_value: str, predicate: str) -> bool:
    if predicate == "contains":
        return payload_value.lower() in field_value.lower()
    elif predicate == "not contains":
        return payload_value.lower() not in field_value.lower()
    elif predicate == "equals":
        return payload_value.lower() == field_value.lower()
    elif predicate == "not equals":
        return payload_value.lower() != field_value.lower()
    else:
        raise Exception("invalid predicate")


@evaluate_condition.register
def _(payload_value: int, field_value: datetime, predicate: str) -> bool:
    delta = timedelta(payload_value)
    now_ = datetime.now()
    if predicate == "less than":
        return now_ - delta < field_value
    elif predicate == "greater than":
        return now_ - delta > field_value
    else:
        raise Exception("invalid predicate")


def apply_rules(rule_file, db_engine: Engine):
    """
    function to load the rules from json file and initiate the rule manager.

    :param rule_file:
    :param db_engine:
    :return:
    """
    logger.info("loading rules from filesystem...")

    with open(rule_file) as f1:
        rules = json.load(f1)

        if not rules:
            logger.info("no rules to apply, terminating process...")
            return

        for rule in rules:
            rule_mgr = RuleManager(rule)
            rule_mgr.start(db_engine=db_engine)


class RuleManager:
    """
    Manager class for handling the processing of rule on emails, filter them out and run actions on them
    """

    def __init__(self, rule):
        self.action_items = []
        self.rule = rule

    def start(self, db_engine: Engine):
        """
        entrypoint function to start the rule processing.

        :param db_engine:
        :return:
        """
        logger.info("applying rule(s)...")

        session = get_session(db_engine)
        emails = get_all_records(session)

        if not emails:
            logger.info("no records found in db, terminating process...")

        self.process_rule(emails)

    def evaluate_group_predicate(self, email: Email, rule: Dict[str, Union[str, Dict]]) -> bool:
        """
        function to evaluate the overall predicate.

        :param email:
        :param rule:
        :return:
        """
        if rule["predicate"] == "All":
            return all(self.evaluate_single_predicate(email, condition) for condition in rule["conditions"])
        elif rule["predicate"] == "Any":
            return any(self.evaluate_single_predicate(email, condition) for condition in rule["conditions"])
        else:
            raise Exception("invalid group predicate")

    def evaluate_single_predicate(self, email: Email, condition: Dict[str, Union[str, int]]) -> bool:
        """
        function to evaluate individual predicate condition.
        :param email:
        :param condition:
        :return:
        """
        field = getattr(email, condition["field_name"].lower(), "")
        return evaluate_condition(condition["value"], field, condition["predicate"])

    def process_rule(self, emails: List[Email]):
        """
        function to apply a rule on emails from db.
        :param emails:
        :return:
        """
        for email in emails:
            if not self.evaluate_group_predicate(email, self.rule):
                continue
            self.action_items.append(email.message_id)

        if self.action_items:
            run_actions(self.rule["actions"], self.action_items)
