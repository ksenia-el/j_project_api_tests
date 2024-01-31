import pytest
from api.api_library.user_account import UserAccount
from api.conftest import user_not_logged_in_session_fixture
from api.conftest import user_logged_in_session_fixture
import allure
from api.support.temporary_email_generator import EmailAndPasswordGenerator


class TestRequestDeleteUser:

    @allure.feature('Request delete user (1st step in two-steps process)')
    @allure.description('Request user delete for existing account (positive)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_request_delete_user_positive(self, user_not_logged_in_session_fixture):
        # ----- precondition: create a user account first
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        session = user_not_logged_in_session_fixture
        api = UserAccount(session)
        request_user_registration = api.user_registration(username, email, password)
        status = request_user_registration[1]
        assert status == 201

        confirmation_token_from_email = email_and_password_generator.get_token_from_confirmation_link_for_registration()
        request_confirm_email = api.confirm_email(confirmation_token_from_email)
        status = request_confirm_email[1]
        assert status == 200

        request_log_in_with_email = api.log_in_with_email_or_username(email, password)
        response, status = request_log_in_with_email
        assert status == 200

        access_token = response.get("access_token")
        session.headers.update(
            {"Authorization": f"Bearer {access_token}"})  # by that we update session, so now the user is logged in


        # --- now the test itself
        api = UserAccount(session)
        response_body, status = api.request_delete_user()
        message = response_body.get("message")
        expected_message = "Message has been sent for your email"
        assert status == 200
        assert message == expected_message

        # also check that the confirmation code was received via email
        code_from_email_to_confirm = email_and_password_generator.get_confirmation_code_for_delete_user()
        assert code_from_email_to_confirm is not None

        # and check that the user is not deleted yet (since this is only 1 step in deleting user process)
        session = user_not_logged_in_session_fixture # using a session of not authorized user
        api = UserAccount(session)
        status = api.log_in_with_email_or_username(email, password)[1]
        assert status == 200

        # ----- now we just delete everything created in the test before - tear-down
        # 1) delete user account created before
        request_confirm_delete_user = api.delete_user(code_from_email_to_confirm)
        status = request_confirm_delete_user[1]
        assert status == 200

        # 2) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('Request delete user (1st step in two-steps process)')
    @allure.description('Request user delete in not authorized session (negative)')
    @allure.severity('Normal')
    @pytest.mark.regression
    def test_request_delete_user_for_not_authenticated_positive(self, user_not_logged_in_session_fixture):
        api = UserAccount(user_not_logged_in_session_fixture)
        response, status = api.request_delete_user()
        expected_response_body = {"detail": "Not authenticated"}
        assert status == 401
        assert response == expected_response_body

