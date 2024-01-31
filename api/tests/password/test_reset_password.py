from api.conftest import user_not_logged_in_session_fixture
from api.support.user_account_support import UserAccountSupport
from api.api_library.password import Password
from api.api_library.user_account import UserAccount
import requests
import string
import random
import allure
import pytest

class TestResetPassword:

    @allure.feature('Reset password (3nd step in the process, final)')
    @allure.description('Reset password (positive)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_reset_password_positive(self, user_not_logged_in_session_fixture):
        # set up of preconditions:
        # 1) create a user account
        user_account_support = UserAccountSupport()
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        # 2) get reset token needed for the test itself
        not_authorized_session = user_not_logged_in_session_fixture
        password_api = Password(not_authorized_session)
        request_recovery = password_api.request_password_recovery_by_email_or_username(email)
        status = request_recovery[1]
        assert status == 200
        reset_token = email_and_password_generator.get_token_for_password_reset()
        assert reset_token is not None

        # creating a new password by replacing the last symbol in the current password with "1"
        new_password = password[:-1] + "1"

        # test itself
        request_reset_password = password_api.reset_password(new_password, reset_token)
        response_body, status = request_reset_password
        expected_response_body = {'message': 'Your new password has been successfully saved'}
        assert status == 200
        assert response_body == expected_response_body

        # now verify that the user is able to log in with a new password after change
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, new_password)
        response_body, status = request_log_in
        assert status == 200

        # if password was changed successfully (we are able to log in with it, so the endpoint works),
        # then we change password back to the old one through the same process as before
        if status == 200:
            request_recovery = password_api.request_password_recovery_by_email_or_username(email)
            status = request_recovery[1]
            assert status == 200
            reset_token = email_and_password_generator.get_token_for_password_reset()
            assert reset_token is not None

            request_reset_password = password_api.reset_password(password, reset_token)
            status = request_reset_password[1]
            assert status == 200


        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Reset password (3nd step in the process, final)')
    @allure.description('Reset password with invalid token (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_reset_password_invalid_reset_token_negative(self):
        # set up of preconditions:
        # 1) create a user account
        user_account_support = UserAccountSupport()
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        # 2) get reset token needed for the test itself
        not_authorized_session = user_not_logged_in_session_fixture
        password_api = Password(not_authorized_session)
        request_recovery = password_api.request_password_recovery_by_email_or_username(email)
        status = request_recovery[1]
        assert status == 200
        reset_token = email_and_password_generator.get_token_for_password_reset()
        assert reset_token is not None
        print(f"Token: {reset_token}")

        # 3) modify reset token to make it invalid (by replacing the last 5 symbols with some other letters and digits)
        symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
        five_random_symbols = ''.join(random.choice(symbols) for i in range(5))
        invalid_reset_token = reset_token[:-5] + five_random_symbols
        print(f"Invalid token: {invalid_reset_token}")

        # creating a new password by replacing the last symbol in the current password with "1"
        new_password = password[:-1] + "1"

        # test itself
        request_reset_password = password_api.reset_password(new_password, invalid_reset_token)
        response_body, status = request_reset_password
        print(request_reset_password)
        expected_response_body = {
          "code": "not_found_error",
          "message": "User was not found"
        }
        assert status == 404
        assert response_body == expected_response_body

        # now verify that the user is able to log in with the old password (so no changes were made)
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, password)
        response_body, status = request_log_in
        assert status == 200

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Reset password (3nd step in the process, final)')
    @allure.description('Reset password with loo long new password, 33-symbols (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_reset_password_too_long_new_password_negative(self, user_not_logged_in_session_fixture):
        # set up of preconditions:
        # 1) create a user account
        user_account_support = UserAccountSupport()
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        # 2) get reset token needed for the test itself
        not_authorized_session = user_not_logged_in_session_fixture
        password_api = Password(not_authorized_session)
        request_recovery = password_api.request_password_recovery_by_email_or_username(email)
        status = request_recovery[1]
        assert status == 200
        reset_token = email_and_password_generator.get_token_for_password_reset()
        assert reset_token is not None

        # create a new password that is 33-symbols long (from the old password by adding symbols in the end)
        how_many_symbols_to_add = 33 - len(password)
        # so we add as many "1" symbols as needed to create a 33-symbols long password (from current)
        new_password_too_long = password + "1" * how_many_symbols_to_add

        # test itself
        request_reset_password = password_api.reset_password(new_password_too_long, reset_token)
        response_body, status = request_reset_password
        expected_response_body = {
            'detail': [{'loc': ['body', 'newPassword2'],
                        'msg': 'Password must contain between 8 and 32 symbols (numbers and/or letters and/or special characters)',
                        'type': 'value_error'}
                       ]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with the old password (so no changes were made)
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, password)
        response_body, status = request_log_in
        assert status == 200

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Reset password (3nd step in the process, final)')
    @allure.description('Reset password with loo short new password, 7-symbols (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_reset_password_too_short_new_password(self, user_not_logged_in_session_fixture):
        # set up of preconditions:
        # 1) create a user account
        user_account_support = UserAccountSupport()
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        # 2) get reset token needed for the test itself
        not_authorized_session = user_not_logged_in_session_fixture
        password_api = Password(not_authorized_session)
        request_recovery = password_api.request_password_recovery_by_email_or_username(email)
        status = request_recovery[1]
        assert status == 200
        reset_token = email_and_password_generator.get_token_for_password_reset()
        assert reset_token is not None

        # create  password that is 7-symbols short (from the old password by getting all symbols up to the 8th)
        new_password_too_short = password[:7]

        # test itself
        request_reset_password = password_api.reset_password(new_password_too_short, reset_token)
        response_body, status = request_reset_password
        expected_response_body = {
            'detail': [{'loc': ['body', 'newPassword2'],
                        'msg': 'Password must contain between 8 and 32 symbols (numbers and/or letters and/or special characters)',
                        'type': 'value_error'}
                       ]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with the old password (so no changes were made)
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, password)
        response_body, status = request_log_in
        assert status == 200

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Reset password (3nd step in the process, final)')
    @allure.description('Reset password with no new password one provided (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_reset_password_no_new_password_one_provided_negative(self, user_not_logged_in_session_fixture):
        # set up of preconditions:
        # 1) create a user account
        user_account_support = UserAccountSupport()
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        # 2) get reset token needed for the test itself
        not_authorized_session = user_not_logged_in_session_fixture
        password_api = Password(not_authorized_session)
        request_recovery = password_api.request_password_recovery_by_email_or_username(email)
        status = request_recovery[1]
        assert status == 200
        reset_token = email_and_password_generator.get_token_for_password_reset()
        assert reset_token is not None

        # creating a new password by replacing the last symbol in the current password with "1"
        new_password = password[:-1] + "1"

        # test itself
        request_body = {
            "newPassword2": new_password,
            "resetToken": reset_token
        }
        request_reset_password = password_api.reset_password_custom_body(request_body)
        response_body, status = request_reset_password
        expected_response_body = {
            'detail':
                [{'loc': ['body', 'newPassword1'],
                  'msg': 'field required',
                  'type': 'value_error.missing'}]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with the old password (so no changes were made)
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, password)
        response_body, status = request_log_in
        assert status == 200

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Reset password (3nd step in the process, final)')
    @allure.description('Reset password with no new password two provided (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_reset_password_no_new_password_two_provided_negative(self, user_not_logged_in_session_fixture):
        # set up of preconditions:
        # 1) create a user account
        user_account_support = UserAccountSupport()
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        # 2) get reset token needed for the test itself
        not_authorized_session = user_not_logged_in_session_fixture
        password_api = Password(not_authorized_session)
        request_recovery = password_api.request_password_recovery_by_email_or_username(email)
        status = request_recovery[1]
        assert status == 200
        reset_token = email_and_password_generator.get_token_for_password_reset()
        assert reset_token is not None

        # creating a new password by replacing the last symbol in the current password with "1"
        new_password = password[:-1] + "1"

        # test itself
        request_body = {
            "newPassword1": new_password,
            "resetToken": reset_token
        }
        request_reset_password = password_api.reset_password_custom_body(request_body)
        response_body, status = request_reset_password
        expected_response_body = {
            'detail':
                [{'loc': ['body', 'newPassword2'],
                  'msg': 'field required',
                  'type': 'value_error.missing'}]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with the old password (so no changes were made)
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, password)
        response_body, status = request_log_in
        assert status == 200

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Reset password (3nd step in the process, final)')
    @allure.description('Reset password with empty request body (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_reset_password_empty_request_body_negative(self, user_not_logged_in_session_fixture):
        # set up of preconditions:
        # 1) create a user account
        user_account_support = UserAccountSupport()
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        # 2) get reset token needed for the test itself
        not_authorized_session = user_not_logged_in_session_fixture
        password_api = Password(not_authorized_session)
        request_recovery = password_api.request_password_recovery_by_email_or_username(email)
        status = request_recovery[1]
        assert status == 200
        reset_token = email_and_password_generator.get_token_for_password_reset()
        assert reset_token is not None

        # test itself
        request_body = {}
        request_reset_password = password_api.reset_password_custom_body(request_body)
        response_body, status = request_reset_password
        expected_response_body = {
            'detail': [{'loc': ['body', 'newPassword1'],
                        'msg': 'field required',
                        'type': 'value_error.missing'},
                       {'loc': ['body', 'newPassword2'],
                        'msg': 'field required', 'type': 'value_error.missing'},
                       {'loc': ['body', 'resetToken'],
                        'msg': 'field required',
                        'type': 'value_error.missing'}]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with the old password (so no changes were made)
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, password)
        response_body, status = request_log_in
        assert status == 200

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()




