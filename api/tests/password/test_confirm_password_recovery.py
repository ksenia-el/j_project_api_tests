from api.api_library.password import Password
from api.api_library.user_account import UserAccount
from api.conftest import user_not_logged_in_session_fixture
from api.support.user_account_support import UserAccountSupport
import string
import random
import allure
import pytest


class TestConfirmPasswordRecovery:

    @allure.feature('Confirm password recovery (2nd step in the process)')
    @allure.description('Confirm password recovery (positive)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_confirm_password_recovery_positive(self, user_not_logged_in_session_fixture):
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
        request_confirm_password_recovery = password_api.confirm_password_recovery(reset_token)
        response_text, status = request_confirm_password_recovery
        expected_response_text = "Password reset"
        assert status == 200
        assert response_text == expected_response_text

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Confirm password recovery (2nd step in the process)')
    @allure.description('Confirm password recovery with invalid token (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_confirm_password_recovery_incorrect_token_provided_negative(self, user_not_logged_in_session_fixture):
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

        # 3) modify reset token to make it incorrect (by replacing the last 5 symbols with some other letters and digits)
        symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
        five_random_symbols = ''.join(random.choice(symbols) for i in range(5))
        incorrect_reset_token = reset_token[:-5] + five_random_symbols

        # test itself
        request_confirm_password_recovery = password_api.confirm_password_recovery(incorrect_reset_token)
        response_text, status = request_confirm_password_recovery
        assert status != 200

        # now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()




