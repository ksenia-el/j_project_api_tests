from api.api_library.password import Password
from api.api_library.user_account import UserAccount
from api.conftest import user_not_logged_in_session_fixture
from api.support.user_account_support import UserAccountSupport
from api.support.temporary_email_generator import EmailAndPasswordGenerator
import allure
import pytest

class TestRequestPasswordRecovery:

    @allure.feature('Request password recovery by email or username (1st step in the process)')
    @allure.description('Request password recovery by email (positive)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_request_password_recovery_by_email_positive(self, user_not_logged_in_session_fixture):
        # set up of preconditions: create a user account
        user_account_support = UserAccountSupport()
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        # test itself
        not_authorized_session = user_not_logged_in_session_fixture
        password_api = Password(not_authorized_session)
        request_recovery = password_api.request_password_recovery_by_email_or_username(email)
        response_body, status = request_recovery

        assert status == 200
        expected_response_body = None
        assert response_body == expected_response_body

        # we should also verify that the email for recovery was sent to email
        reset_token = email_and_password_generator.get_token_for_password_reset()
        assert reset_token is not None

        # and also verify that after all actions (incomplete password recovery) we are still able to log in with current password
        user_account_api = UserAccount(not_authorized_session)
        request_user_log_in = user_account_api.log_in_with_email_or_username(email, password)
        response_body, status = request_user_log_in
        assert status == 200

        # ----- now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Request password recovery by email or username (1st step in the process)')
    @allure.description('Request password recovery by username (positive)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_request_password_recovery_by_username_positive(self, user_not_logged_in_session_fixture):
        # set up of preconditions: create a user account
        user_account_support = UserAccountSupport()
        email_and_password_generator, username, email, password = user_account_support.create_user_account()

        # test itself
        not_authorized_session = user_not_logged_in_session_fixture
        password_api = Password(not_authorized_session)
        request_recovery = password_api.request_password_recovery_by_email_or_username(username)

        response_body, status = request_recovery
        assert status == 200
        expected_response_body = None
        assert response_body == expected_response_body

        # we should also verify that the email for recovery was sent to email
        reset_token = email_and_password_generator.get_token_for_password_reset()
        assert reset_token is not None

        # and also verify that after all actions (incomplete password recovery) we are still able to log in with current password
        user_account_api = UserAccount(not_authorized_session)
        request_user_log_in = user_account_api.log_in_with_email_or_username(email, password)
        response_body, status = request_user_log_in
        assert status == 200

        # ----- now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        user_account_support.delete_user_account(email_and_password_generator)

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Request password recovery by email (1st step in the process)')
    @allure.description('Request password recovery, but with empty request body (negative)')
    @allure.severity('Normal')
    @pytest.mark.regression
    def test_request_password_recovery_empty_body_negative(self, user_not_logged_in_session_fixture):
        not_authorized_session = user_not_logged_in_session_fixture

        password_api = Password(not_authorized_session)
        request_body = {}
        request_recovery = password_api.request_password_recovery_custom_body(request_body)

        response_body, status = request_recovery
        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "recoveryField"
              ],
              "msg": "field required",
              "type": "value_error.missing"
            }
          ]
        }
        assert status == 422
        assert response_body == expected_response_body

    @allure.feature('Request password recovery by email (1st step in the process)')
    @allure.description('Request password recovery, but with empty value in recovery field (negative)')
    @allure.severity('Normal')
    @pytest.mark.regression
    def test_request_password_recovery_empty_string_in_recovery_field_negative(self, user_not_logged_in_session_fixture):
        not_authenticated_session = user_not_logged_in_session_fixture

        password_api = Password(not_authenticated_session)
        request_body = {"recoveryField": ""}
        request_recovery = password_api.request_password_recovery_custom_body(request_body)

        response_body, status = request_recovery
        assert status == 422

    @allure.feature('Request password recovery by email (1st step in the process)')
    @allure.description('Request password recovery by email not registered (negative)')
    @allure.severity('Normal')
    @pytest.mark.regression
    def test_request_password_recovery_no_user_with_such_email_exist_negative(self, user_not_logged_in_session_fixture):
        not_authenticated_session = user_not_logged_in_session_fixture
        email_and_password_generator = EmailAndPasswordGenerator()
        email = email_and_password_generator.generate_username_and_email_and_password()[1]

        password_api = Password(not_authenticated_session)
        request_body = {"recoveryField": email}
        request_recovery = password_api.request_password_recovery_custom_body(request_body)

        response_body, status = request_recovery
        assert status != 200
        print(request_recovery)

        # also verify that no reset token was sent via email provided
        reset_token_from_email = email_and_password_generator.get_token_for_password_reset()
        assert reset_token_from_email is None

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

