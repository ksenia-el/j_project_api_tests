import pytest
from api.api_library.user_account import UserAccount
from api.conftest import user_not_logged_in_session_fixture
from api.support.temporary_email_generator import EmailAndPasswordGenerator
import string
import random
from api.support.user_account_support import UserAccountSupport
import time
from api.test_data.test_data_user_account import TestData
import allure

class TestRequestEmailVerify:

    @allure.feature('Request email verification (used to complete user registration; '
                    'run in case no email with token was received before)')
    @allure.description('Request email verification (positive)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_request_email_verify_positive(self, user_not_logged_in_session_fixture):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)

        request_user_registration = user_account_api.user_registration(username, email, password)
        status = request_user_registration[1]
        assert status == 201

        # we retrieve the first token automatically send when starting registration - so we won't confuse it
        # with the second token that should be sent in the test itself
        first_token_received = email_and_password_generator.get_token_from_confirmation_link_for_registration()

        # the test itself
        request_email_verify = user_account_api.request_email_verify(email)
        response_body, status = request_email_verify

        assert status == 200
        expected_response_body = {
          "message": "Verification message has been sent for your email"
        }
        assert response_body == expected_response_body

        second_token_received = None

        for i in range(0, 10):  # make 10 attempts max to detect new token received in email
            last_token_received = email_and_password_generator.get_token_from_confirmation_link_for_registration()
            if last_token_received != first_token_received:
                second_token_received = last_token_received
                break

        assert second_token_received is not None, "No new token detected in email"

        # also, trying to register user account with this token to verify that it's valid
        request_confirm_email = user_account_api.confirm_email(second_token_received)
        status = request_confirm_email[1]
        assert status == 200
        # and log in with it to complete verification
        request_log_in = user_account_api.log_in_with_email_or_username(email, password)
        status = request_log_in[1]
        assert status == 200

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support = UserAccountSupport()
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Request email verification (used to complete user registration; '
                    'run in case no email with token was received before)')
    @allure.description('Request email verification, second attempt (positive)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    # the next test verifies that the endpoint can be used as many times as needed (more than once),
    # and each time a new token received
    def test_request_email_verify_second_attempt_positive(self, user_not_logged_in_session_fixture):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)

        request_user_registration = user_account_api.user_registration(username, email, password)
        status = request_user_registration[1]
        assert status == 201

        # we retrieve the first token automatically sent when starting registration - so we won't confuse it
        # with the second token that should be sent in the test itself
        first_token_received = email_and_password_generator.get_token_from_confirmation_link_for_registration()

        # the test itself

        # first attempt
        request_email_verify_first_attempt = user_account_api.request_email_verify(email)
        status = request_email_verify_first_attempt[1]
        assert status == 200
        second_token_received = None
        for i in range(0, 10):  # make 10 attempts max to detect new token received in email
            last_token_received = email_and_password_generator.get_token_from_confirmation_link_for_registration()
            if last_token_received != first_token_received:
                second_token_received = last_token_received
                break
        assert second_token_received is not None, "No new token (first attempt) detected in email"

        # second attempt
        request_email_verify_second_attempt = user_account_api.request_email_verify(email)
        status = request_email_verify_second_attempt[1]
        assert status == 200
        third_token_received = None
        for i in range(0, 10):  # make 10 attempts max to detect a new token received in email
            last_token_received = email_and_password_generator.get_token_from_confirmation_link_for_registration()
            if last_token_received != second_token_received:
                third_token_received = last_token_received
                break
        assert second_token_received is not None, "No new token (second attempt) detected in email"

        # delete email address created before - tear down
        email_and_password_generator.delete_email_generated()

    @allure.feature('Request email verification (used to complete user registration; '
                    'run in case no email with token was received before)')
    @allure.description('Request email verification, registration process has not been started yet (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_request_email_verify_registration_was_not_started_negative(self, user_not_logged_in_session_fixture):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)

        request_email_verify = user_account_api.request_email_verify(email)
        response_body, status = request_email_verify

        assert status != 200

        # also verify that no email with token was sent
        token = email_and_password_generator.get_token_from_confirmation_link_for_registration()
        assert token is None

        # delete email address created before - tear down
        email_and_password_generator.delete_email_generated()

    @allure.feature('Request email verification (used to complete user registration; '
                    'run in case no email with token was received before)')
    @allure.description('Request email verification, email address is already registered (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_request_email_verify_with_address_already_registered_negative(self, user_not_logged_in_session_fixture):
        user_account_support = UserAccountSupport()
        # create a user account first
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)

        # test itself
        request_email_verify = user_account_api.request_email_verify(email)
        response_body, status = request_email_verify

        print(request_email_verify)
        assert status != 200

        # also verify that no email with token was sent
        token = email_and_password_generator.get_token_from_confirmation_link_for_registration()
        assert token is None

        # and user is able to log in as usual, no changes were made
        request_log_in = user_account_api.log_in_with_email_or_username(email, password)
        status = request_log_in[1]
        assert status == 200

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support = UserAccountSupport()
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Request email verification (used to complete user registration; '
                    'run in case no email with token was received before)')
    @allure.description('Request email verification, invalid email address provided (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    @pytest.mark.parametrize('invalid_email', TestData.invalid_emails)
    def test_request_email_verify_invalid_email_address_negative(self, invalid_email, user_not_logged_in_session_fixture):
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)

        request_email_verify = user_account_api.request_email_verify(invalid_email)
        response_body, status =  request_email_verify

        assert status == 422, f'Invalid email ({invalid_email}) was accepted'
        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "email"
              ],
              "msg": "value is not a valid email address",
              "type": "value_error.email"
            }
          ]
        }
        assert response_body == expected_response_body






