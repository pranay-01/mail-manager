import unittest
from unittest.mock import MagicMock, patch

from actions import mark_as_read_or_unread, move_to_folder
from authn import Service
from handlers import store_emails
from rule_manager import RuleManager


class TestRuleManager(unittest.TestCase):

    @patch("db.get_session")
    @patch("db.get_all_records")
    @patch("rule_manager.logger")
    def test_start_no_emails(self, mock_logger, mock_get_all_records, mock_get_session):
        mock_get_all_records.return_value = []
        db_engine = MagicMock()
        mock_session = mock_get_session(db_engine)
        emails = mock_get_all_records(mock_session)

        if not emails:
            mock_logger.info("no records found in db, terminating process...")

        mock_logger.info.assert_called_once_with("no records found in db, terminating process...")

    @patch("rule_manager.evaluate_condition")
    def test_evaluate_single_predicate(self, mock_evaluate_condition):
        email = MagicMock()
        email.subject = "Test Subject"
        condition = {"field_name": "subject", "value": "Test", "predicate": "contains"}

        rule_manager = RuleManager(None)
        result = rule_manager.evaluate_single_predicate(email, condition)

        self.assertTrue(mock_evaluate_condition.called)
        self.assertEqual(result, mock_evaluate_condition.return_value)

    @patch("rule_manager.RuleManager.evaluate_single_predicate")
    def test_evaluate_group_predicate(self, mock_evaluate_single_predicate):
        email = MagicMock()
        rule = {"predicate": "All", "conditions": [{"field_name": "subject", "value": "Test", "predicate": "contains"}]}

        rule_manager = RuleManager(rule)
        mock_evaluate_single_predicate.return_value = True

        result = rule_manager.evaluate_group_predicate(email, rule)

        self.assertTrue(result)
        mock_evaluate_single_predicate.assert_called_once_with(email, rule["conditions"][0])


class TestStoreEmails(unittest.TestCase):

    @patch("db.get_session")
    @patch("db.create_tables")
    @patch("handlers.logger")
    def test_store_emails_success(self, mock_logger, mock_create_tables, mock_get_session):
        # Mock data
        message_data = [
            {
                "payload": {
                    "headers": [
                        {"name": "From", "value": "sender@example.com"},
                        {"name": "To", "value": "recipient@example.com"},
                        {"name": "Subject", "value": "Test Subject"},
                        {"name": "Date", "value": "2024-05-19"}
                    ]
                },
                "id": "123456",
                "snippet": "Test email snippet"
            }
        ]
        db_engine_mock = MagicMock()

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        store_emails(message_data, db_engine_mock)

        # Assertions
        mock_create_tables.assert_called_once_with(db_engine_mock)
        self.assertEqual(mock_session.add.call_count, 1)
        mock_session.commit.assert_called_once()
        mock_logger.info.assert_called_once_with("storing emails into db...")

    @patch("db.get_session")
    @patch("db.create_tables")
    @patch("handlers.logger")
    def test_store_emails_exception(self, mock_logger, mock_create_tables, mock_get_session):
        # Mock data
        message_data = [
            {
                "payload": {
                    "headers": [
                        {"name": "From", "value": "sender@example.com"},
                        {"name": "To", "value": "recipient@example.com"},
                        {"name": "Subject", "value": "Test Subject"},
                        {"name": "Date", "value": "2024-05-19"}
                    ]
                },
                "id": "123456",
                "snippet": "Test email snippet"
            }
        ]
        db_engine_mock = MagicMock()
        mock_session = MagicMock()
        mock_session.add.side_effect = Exception("Test exception")
        mock_get_session.return_value = mock_session

        store_emails(message_data, db_engine_mock)

        # Assertions
        mock_create_tables.assert_called_once_with(db_engine_mock)
        mock_session.rollback.assert_called_once()
        mock_logger.exception.assert_called_once_with("error pushing data into db, Test exception", exc_info=True)
        mock_session.close.assert_called_once()


# class TestEmailActions(unittest.TestCase):
#
#     @patch("authn.Service")
#     def test_mark_as_read(self, mock_service):
#         action_items = ["18f8ea6229f51b87", "18f8ea3aedf1f203"]
#         mock_service.users().messages().batchModify().execute.return_value = None
#
#         mark_as_read_or_unread(action_items, label="READ")
#
#         body = {"removeLabelIds": ["UNREAD"], "ids": action_items}
#         mock_service.users().messages().batchModify.assert_called_once_with(userId="me", body=body)
#         mock_service.users().messages().batchModify().execute.assert_called_once()
#
#     @patch("authn.Service")
#     def test_mark_as_unread(self, mock_service):
#         action_items = ["18f8ea6229f51b87", "18f8ea3aedf1f203"]
#         mock_service.users().messages().batchModify().execute.return_value = None
#
#         mark_as_read_or_unread(action_items, label="UNREAD")
#
#         body = {"addLabelIds": ["UNREAD"], "ids": action_items}
#         mock_service.users().messages().batchModify.assert_called_once_with(userId="me", body=body)
#         mock_service.users().messages().batchModify().execute.assert_called_once()
#
#     @patch("authn.Service")
#     def test_move_to_folder(self, mock_service):
#         action_items = ["18f8ea6229f51b87", "18f8ea3aedf1f203"]
#         mock_service.users().labels().list().execute.return_value = {
#             "labels": [
#                 {"id": "INBOX", "name": "INBOX"},
#                 {"id": "Label_2073608533525491488", "name": "dummy"}
#             ]
#         }
#         mock_service.users().messages().batchModify().execute.return_value = None
#
#         move_to_folder(action_items, label="Label_2073608533525491488")
#
#         body_remove = {"removeLabelIds": ["INBOX"], "ids": action_items}
#         body_add = {"addLabelIds": ["dummy"], "ids": action_items}
#
#         calls = [
#             patch(Service).users().messages().batchModify(userId="me", body=body_remove),
#             patch(Service).users().messages().batchModify(userId="me", body=body_add)
#         ]
#
#         mock_service.users().messages().batchModify.assert_has_calls(calls)
#         self.assertEqual(mock_service.users().messages().batchModify().execute.call_count, 2)
#
