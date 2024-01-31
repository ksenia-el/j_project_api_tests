
import pytest
from api.api_library.password import Password
from api.api_library.user_account import UserAccount
from api.conftest import user_not_logged_in_session_fixture
from api.conftest import user_logged_in_session_fixture
import allure
import api.conftest


class TestChangePasswordInProfile:

    @allure.feature('Change password in profile')
    @allure.description('Change password in profile (positive)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_change_password_in_profile_positive(self, user_logged_in_session_fixture, user_not_logged_in_session_fixture):
        authorized_session = user_logged_in_session_fixture[0]
        email = user_logged_in_session_fixture[1]
        old_password = user_logged_in_session_fixture[2]

        # creating a new password by replacing the last symbol in the current password with "1"
        new_password = old_password[:-1] + "1"

        password_api = Password(authorized_session)
        # and run request to change password from current to new
        request_change_password = password_api.change_password_in_profile(old_password, new_password)
        response_body = request_change_password[0]
        status = request_change_password[1]
        expected_response_body = {'message': 'Your new password has been successfully saved'}

        assert status == 200
        assert response_body == expected_response_body

        # now verify that the user is able to log in with a new password after change
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, new_password)
        response_body = request_log_in[0]
        status = request_log_in[1]
        assert status == 200

        # if password was changed successfully (we are able to log in with it, so the endpoint works),
        # then we change password back to the old one
        if status == 200:
            # update token for authorized session
            access_token = response_body.get("access_token")
            authorized_session.headers.update({"Authorization": f"Bearer {access_token}"})  # by that we update session, so now the user is logged in
            # change password back
            request_password_change = password_api.change_password_in_profile(new_password, old_password)
            status = request_password_change[1]
            assert status == 200

    @allure.feature('Change password in profile')
    @allure.description('Change password in profile, incorrect old password provided (negative)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_change_password_in_profile_incorrect_old_password_negative(self, user_not_logged_in_session_fixture, user_logged_in_session_fixture):
        authorized_session = user_logged_in_session_fixture[0]
        email = user_logged_in_session_fixture[1]
        correct_password = user_logged_in_session_fixture[2]

        # creating a new password by replacing the last symbol in the current password with "1"
        new_password = correct_password[:-1] + "1"
        # modify current (old) password to make it incorrect by changing the last symbol in it
        incorrect_old_password = correct_password[:-1] + "3"

        password_api = Password(authorized_session)
        # and run request to try changing password
        request_change_password = password_api.change_password_in_profile(incorrect_old_password, new_password)
        response_body = request_change_password[0]
        status = request_change_password[1]
        expected_response_body = {
          "code": "bad_request",
          "message": "Wrong old password"
        }

        assert status == 400
        assert response_body == expected_response_body

        # now verify that the user is able to log in with old correct password (=no changes were made)
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, correct_password)
        status = request_log_in[1]
        assert status == 200

    @allure.feature('Change password in profile')
    @allure.description('Change password in profile, too long new password provided (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_change_password_in_profile_too_long_new_password_negative(self, user_logged_in_session_fixture, user_not_logged_in_session_fixture):
        authorized_session = user_logged_in_session_fixture[0]
        email = user_logged_in_session_fixture[1]
        old_password = user_logged_in_session_fixture[2]

        # create a new password that is 33-symbols long (from the old password by adding symbols in the end)
        how_many_symbols_to_add = 33-len(old_password)
        # so we add as many "1" symbols as needed to create a 33-symbols long password (from current)
        new_password_too_long = old_password + "1" * how_many_symbols_to_add

        password_api = Password(authorized_session)
        request_password_change = password_api.change_password_in_profile(old_password, new_password_too_long)
        response_body, status = request_password_change
        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "newPassword2"
              ],
              "msg": "Password must contain between 8 and 32 symbols (numbers and/or letters and/or special characters)",
              "type": "value_error"
            }
          ]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with old correct password (=no changes were made)
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, old_password)
        status = request_log_in[1]
        assert status == 200

    @allure.feature('Change password in profile')
    @allure.description('Change password in profile, too short new password provided (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_change_password_in_profile_too_short_new_password_negative(self,
                                                                        user_logged_in_session_fixture,
                                                                        user_not_logged_in_session_fixture):
        authorized_session = user_logged_in_session_fixture[0]
        email = user_logged_in_session_fixture[1]
        old_password = user_logged_in_session_fixture[2]

        # create  password that is 7-symbols short (from the old password by getting all symbols up to the 8th)
        new_password_too_short = old_password[:7]

        password_api = Password(authorized_session)
        request_password_change = password_api.change_password_in_profile(old_password, new_password_too_short)
        response_body, status = request_password_change
        expected_response_body = {
            "detail": [
                {
                    "loc": [
                        "body",
                        "newPassword2"
                    ],
                    "msg": "Password must contain between 8 and 32 symbols "
                           "(numbers and/or letters and/or special characters)",
                    "type": "value_error"
                }
            ]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with old correct password (=no changes were made)
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, old_password)
        response_body, status = request_log_in
        print(response_body)
        assert status == 200

    @allure.feature('Change password in profile')
    @allure.description('Change password in profile, not matching new passwords provided (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_change_password_in_profile_not_matching_new_passwords_negative(self,
                                                                        user_logged_in_session_fixture,
                                                                        user_not_logged_in_session_fixture):
        authorized_session = user_logged_in_session_fixture[0]
        email = user_logged_in_session_fixture[1]
        old_password = user_logged_in_session_fixture[2]

        # creating two different versions of new password
        # (by replacing the last symbol in the current password with "1" or "2")
        new_password1 = old_password[:-1] + "1"
        new_password2 = old_password[:-1] + "2"

        request_body = {
            "newPassword1": new_password1,
            "newPassword2": new_password2,
            "oldPassword": old_password
        }

        password_api = Password(authorized_session)
        request_password_change = password_api.change_password_in_profile_custom_body(request_body)
        response_body, status = request_password_change
        expected_response_body = {
            "code": "bad_request",
            "message": "Passwords do not match"
        }
        assert status == 400
        assert response_body == expected_response_body

        # now verify that the user is able to log in with old correct password (=no changes were made)
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, old_password)
        status = request_log_in[1]
        assert status == 200

    @allure.feature('Change password in profile')
    @allure.description('Change password in profile, no new password one provided (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_change_password_in_profile_no_new_password_one_provided_negative(self,
                                                                        user_logged_in_session_fixture,
                                                                        user_not_logged_in_session_fixture):
        authorized_session = user_logged_in_session_fixture[0]
        email = user_logged_in_session_fixture[1]
        old_password = user_logged_in_session_fixture[2]

        # creating a new password by replacing the last symbol in the current (old) password with "1"
        new_password = old_password[:-1] + "1"

        request_body = {
            "newPassword2": new_password,
            "oldPassword": old_password
        }

        password_api = Password(authorized_session)
        request_password_change = password_api.change_password_in_profile_custom_body(request_body)
        response_body, status = request_password_change
        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "newPassword1"
              ],
              "msg": "field required",
              "type": "value_error.missing"
            }
          ]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with old correct password (=no changes were made)
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, old_password)
        status = request_log_in[1]
        assert status == 200

    @allure.feature('Change password in profile')
    @allure.description('Change password in profile, no new password two provided (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_change_password_in_profile_no_new_password_two_provided_negative(self,
                                                                        user_logged_in_session_fixture,
                                                                        user_not_logged_in_session_fixture):
        authorized_session = user_logged_in_session_fixture[0]
        email = user_logged_in_session_fixture[1]
        old_password = user_logged_in_session_fixture[2]

        # creating a new password by replacing the last symbol in the current (old) password with "1"
        new_password = old_password[:-1] + "1"

        request_body = {
            "newPassword1": new_password,
            "oldPassword": old_password
        }

        password_api = Password(authorized_session)
        request_password_change = password_api.change_password_in_profile_custom_body(request_body)
        response_body, status = request_password_change
        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "newPassword2"
              ],
              "msg": "field required",
              "type": "value_error.missing"
            }
          ]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with old correct password (=no changes were made)
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, old_password)
        status = request_log_in[1]
        assert status == 200

    @allure.feature('Change password in profile')
    @allure.description('Change password in profile, no old password provided (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_change_password_in_profile_no_old_password_provided_negative(self,
                                                                              user_logged_in_session_fixture,
                                                                              user_not_logged_in_session_fixture):
        authorized_session = user_logged_in_session_fixture[0]
        email = user_logged_in_session_fixture[1]
        old_password = user_logged_in_session_fixture[2]

        # creating a new password by replacing the last symbol in the current (old) password with "1"
        new_password = old_password[:-1] + "1"

        request_body = {
            "newPassword1": new_password,
            "newPassword2": new_password
        }

        password_api = Password(authorized_session)
        request_password_change = password_api.change_password_in_profile_custom_body(request_body)
        response_body, status = request_password_change
        expected_response_body = {
            "detail": [
                {
                    "loc": [
                        "body",
                        "oldPassword"
                    ],
                    "msg": "field required",
                    "type": "value_error.missing"
                }
            ]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with old correct password (=no changes were made)
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, old_password)
        status = request_log_in[1]
        assert status == 200

    @allure.feature('Change password in profile')
    @allure.description('Change password in profile, empty request body (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_change_password_in_profile_empty_request_body_negative(self,
                                                                              user_logged_in_session_fixture,
                                                                              user_not_logged_in_session_fixture):
        authorized_session = user_logged_in_session_fixture[0]
        email = user_logged_in_session_fixture[1]
        old_password = user_logged_in_session_fixture[2]

        request_body = {}

        password_api = Password(authorized_session)
        request_password_change = password_api.change_password_in_profile_custom_body(request_body)
        response_body, status = request_password_change
        expected_response_body = {
          "detail": [
              {"loc":
                  ["body",
                    "newPassword1"],
                    "msg": "field required",
                    "type": "value_error.missing"},
              {"loc":
                   ["body",
                    "newPassword2"],
                    "msg": "field required",
                    "type": "value_error.missing"},
              {"loc":
                 ["body",
                  "oldPassword"],
               "msg": "field required",
              "type": "value_error.missing"}
          ]
        }
        assert status == 422
        assert response_body == expected_response_body

        # now verify that the user is able to log in with old correct password (=no changes were made)
        not_authorized_session = user_not_logged_in_session_fixture
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, old_password)
        status = request_log_in[1]
        assert status == 200

    @allure.feature('Change password in profile')
    @allure.description('Change password in profile, user not authenticated (negative)')
    @allure.severity('Critical')
    @pytest.mark.regression
    def test_change_password_in_profile_not_authenticated_negative(self, user_not_logged_in_session_fixture, user_logged_in_session_fixture):
        not_authorized_session = user_not_logged_in_session_fixture

        email = user_logged_in_session_fixture[1]
        old_password = user_logged_in_session_fixture[2]

        # creating a new password by replacing the last symbol in the current password with "1"
        new_password = old_password[:-1] + "1"

        # to make a call in non-authorized session
        password_api = Password(not_authorized_session)
        # and run request to try changing password
        request_change_password = password_api.change_password_in_profile(old_password, new_password)
        response_body = request_change_password[0]
        status = request_change_password[1]
        expected_response_body = {
          "detail": "Not authenticated"
        }

        assert status == 401
        assert response_body == expected_response_body

        # now verify that the user is able to log in with old correct password (=no changes were made)
        user_account_api = UserAccount(not_authorized_session)
        request_log_in = user_account_api.log_in_with_email_or_username(email, old_password)
        status = request_log_in[1]
        assert status == 200

