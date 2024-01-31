import pytest
from api.api_library.user_account import UserAccount
from api.conftest import user_not_logged_in_session_fixture
from api.support.temporary_email_generator import EmailAndPasswordGenerator
import string
import random
from api.support.user_account_support import UserAccountSupport
import allure


class TestCheckUsername:

    @allure.feature('Username check')
    @allure.description('Check username for registration, not used before (positive)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_check_username_positive(self, user_not_logged_in_session_fixture):
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(user_not_logged_in_session_fixture)

        username = None

        for i in range(0, 3):  # making three attempts to find username
            # that is not already registered in system (according to the result of check)

            # 1) firstly create a 32-symbols long username that contains all allowed types of symbols:
            # letters (lower and upper case), numbers and '.'
            alphanumeric_symbols_allowed = string.ascii_lowercase + string.ascii_uppercase + string.digits
            username_candidate = '.' + ''.join(random.choice(alphanumeric_symbols_allowed) for i in range(30)) + '.'

            request_username_check = user_account_api.username_check(username_candidate)
            response, status = request_username_check

            # 2) check that it's not used yet
            if status == 204:  # and if username is not already used, then we select it to the test itself
                username = username_candidate
                break

        assert username is not None, "Unable to find an available username for test after three attempts"

        #  verify that it's not used in system yet - by registering a new account with it
        email_and_password_generator = EmailAndPasswordGenerator()
        username_do_not_use, email, password = email_and_password_generator.generate_username_and_email_and_password()

        request_user_registration = user_account_api.user_registration(username, email, password)
        status = request_user_registration[1]
        assert status == 201

        confirmation_token_from_email = email_and_password_generator.get_token_from_confirmation_link_for_registration()
        request_confirm_email = user_account_api.confirm_email(confirmation_token_from_email)
        status = request_confirm_email[1]
        assert status == 200

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support = UserAccountSupport()
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Username check')
    @allure.description('Check username for registration, already used (negative)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_check_username_already_used_negative(self, user_not_logged_in_session_fixture):
        # set up of preconditions:
        # create a user account (with a specific username used)
        user_account_support = UserAccountSupport()
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        # test itself
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_username_check = user_account_api.username_check(username)
        response, status = request_username_check

        assert status == 400
        assert response.json() == {
          "code": "already_exist",
          "message": "User with this username is already exist"
        }

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Username check')
    @allure.description('Check username for registration, too short, 2 symbols long (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_check_username_too_short_negative(self, user_not_logged_in_session_fixture):
        # firstly create a 2-symbols long username from alphanumeric symbols
        alphanumeric_symbols_allowed = string.ascii_lowercase + string.ascii_uppercase + string.digits
        username = ''.join(random.choice(alphanumeric_symbols_allowed) for i in range(2))

        # test itself
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_username_check = user_account_api.username_check(username)
        response, status = request_username_check

        assert status == 422

        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "username"
              ],
              "msg": "Username must contain from 3 to 32 symbols (numbers, letters or '.' are allowed)",
              "type": "value_error"
            }
          ]
        }
        assert response.json() == expected_response_body

    @allure.feature('Username check')
    @allure.description('Check username for registration, too long, 33 symbols long (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_check_username_too_long_negative(self, user_not_logged_in_session_fixture):
        # firstly create a 33-symbols long username that contains all allowed types of symbols:
        # letters (lower and upper case), numbers and '.'
        alphanumeric_symbols_allowed = string.ascii_lowercase + string.ascii_uppercase + string.digits
        username = '.' + ''.join(random.choice(alphanumeric_symbols_allowed) for i in range(31)) + '.'

        # test itself
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_username_check = user_account_api.username_check(username)
        response, status = request_username_check

        assert status == 422

        expected_response_body = {
            "detail": [
                {
                    "loc": [
                        "body",
                        "username"
                    ],
                    "msg": "Username must contain from 3 to 32 symbols (numbers, letters or '.' are allowed)",
                    "type": "value_error"
                }
            ]
        }
        assert response.json() == expected_response_body

    @allure.feature('Username check')
    @allure.description('Check username for registration, contains not allowed symbols (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_check_username_contains_not_allowed_symbols_negative(self, user_not_logged_in_session_fixture):
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)

        symbols_allowed = string.ascii_lowercase + string.ascii_uppercase + string.digits + '.'
        not_allowed_symbols = string.punctuation.replace('.', '')  # get all punctuation symbols except allowed '.'

        for symbol_to_check in not_allowed_symbols:
            # generate a username 4-symbols long, that contains: 1 not-allowed symbol and 3 other - allowed
            username_generated = symbol_to_check + ''.join(random.choice(symbols_allowed) for i in range(3))
            request_username_check = user_account_api.username_check(username_generated)
            response, status = request_username_check

            assert status == 422

            expected_response_body = {
                "detail": [
                    {
                        "loc": [
                            "body",
                            "username"
                        ],
                        "msg": "Username must contain from 3 to 32 symbols (numbers, letters or '.' are allowed)",
                        "type": "value_error"
                    }
                ]
            }
            assert response.json() == expected_response_body

    @allure.feature('Username check')
    @allure.description('Check username for registration, empty value (negative)')
    @allure.severity('Normal')
    @pytest.mark.regression
    def test_check_username_empty_string_negative(self, user_not_logged_in_session_fixture):
        empty_username = ''

        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_username_check = user_account_api.username_check(empty_username)
        response, status = request_username_check

        assert status == 422

        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "username"
              ],
              "msg": "Name cannot be empty",
              "type": "value_error"
            }
          ]
        }
        assert response.json() == expected_response_body

    @allure.feature('Username check')
    @allure.description('Check username for registration, spaces only (negative)')
    @allure.severity('Normal')
    @pytest.mark.regression
    def test_check_username_spaces_only_negative(self, user_not_logged_in_session_fixture):
        # username with three spaces - allowed length, but not allowed symbols
        username_spaces_only = ' ' * 3

        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_username_check = user_account_api.username_check(username_spaces_only)
        response, status = request_username_check

        assert status == 422

        expected_response_body = {
            "detail": [
                {
                    "loc": [
                        "body",
                        "username"
                    ],
                    "msg": "Username must contain from 3 to 32 symbols (numbers, letters or '.' are allowed)",
                    "type": "value_error"
                }
            ]
        }
        assert response.json() == expected_response_body

    @allure.feature('Username check')
    @allure.description('Check username for registration, empty request body (negative)')
    @allure.severity('Normal')
    @pytest.mark.regression
    def test_check_username_empty_request_body(self, user_not_logged_in_session_fixture):
        empty_request_body = {}

        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_username_check = user_account_api.username_check_custom_body(empty_request_body)
        response, status = request_username_check

        assert status == 422

        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "username"
              ],
              "msg": "field required",
              "type": "value_error.missing"
            }
          ]
        }
        assert response.json() == expected_response_body
