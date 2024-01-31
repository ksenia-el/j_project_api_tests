from api.api_library.user_account import UserAccount
from api.conftest import new_user_logged_in_session_fixture
from api.conftest import user_not_logged_in_session_fixture
import allure
import pytest


class TestUserLogOut:


    @allure.feature('User log out')
    @allure.description('User logs out (positive)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_user_log_out_positive(self, new_user_logged_in_session_fixture):
        session, email, password, user_profile_id, user_role, user_status, username = new_user_logged_in_session_fixture
        api = UserAccount(session)  # create an Endpoints instance using a session of authorized user
        response_body, status = api.user_logout()
        message = response_body.get("message")
        assert status == 200
        assert message == "You have been logout"

    @allure.feature('User log out')
    @allure.description('User logs out, not authorized session (negative)')
    @allure.severity('Normal')
    @pytest.mark.regression
    def test_user_log_out_for_not_authenticated_negative(self, user_not_logged_in_session_fixture):
        api = UserAccount(user_not_logged_in_session_fixture)
        response, status = api.user_logout()
        assert status == 401
        expected_response_body = {'detail': 'Not authenticated'}
        assert response == expected_response_body

