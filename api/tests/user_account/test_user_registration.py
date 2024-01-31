import pytest
import allure
from api.api_library.user_account import UserAccount
import requests
from api.support.temporary_email_generator import EmailAndPasswordGenerator
from api.conftest import user_not_logged_in_session_fixture
from api.conftest import new_user_logged_in_session_fixture
import random
import string
from api.support.user_account_support import UserAccountSupport


class TestUserRegistration:

    @allure.feature('User registration')
    @allure.description('Register user with valid credentials (positive)')
    @allure.severity('Blocker')
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_user_registration_positive(self, user_not_logged_in_session_fixture):
        # generate email and password needed for user registration
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        # create session (empty, no user authorized yet)
        user_not_authorized_session = user_not_logged_in_session_fixture
        #  next API calls will be done using not-authorized session
        api = UserAccount(user_not_authorized_session)

        # start user registration process by using one endpoint
        request_user_registration = api.user_registration(username, email, password)
        response_body, status = request_user_registration

        assert status == 201

        expected_response_body = {
          "message": "successful"
        }
        assert response_body == expected_response_body

        # complete user registration process by using another endpoint (to confirm email)
        confirmation_token_from_email = email_and_password_generator.get_token_from_confirmation_link_for_registration()
        request_confirm_email = api.confirm_email(confirmation_token_from_email)
        status = request_confirm_email[1]
        assert status == 200

        # now we just delete everything created in the test before (tear-down):

        # 1) log into the system
        request_log_in = api.log_in_with_email_or_username(email, password)
        response_body, status = request_log_in
        assert status == 200
        access_token = response_body.get("access_token")
        session_of_user_being_logged_in = requests.Session()
        session_of_user_being_logged_in.headers.update({"Authorization": f"Bearer {access_token}"})  # by that we update session, so now the user is logged in
        api = UserAccount(session_of_user_being_logged_in)

        # 2) delete user account created before
        request_delete_user = api.request_delete_user()
        status = request_delete_user[1]
        assert status == 200
        code_from_email_to_confirm = email_and_password_generator.get_confirmation_code_for_delete_user()
        assert code_from_email_to_confirm is not None
        request_confirm_delete_user = api.delete_user(code_from_email_to_confirm)
        status = request_confirm_delete_user[1]
        assert status == 200

        # 3) delete email address created before
        email_and_password_generator.delete_email_generated()

    @allure.feature('User registration')
    @allure.description('Register user with valid credentials, second attempt (negative)')
    @allure.severity('Normal')
    @pytest.mark.regression
    def test_user_registration_second_attempt_negative(self, user_not_logged_in_session_fixture):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        api = UserAccount(user_not_logged_in_session_fixture)

        # first request to register user
        request_user_registration = api.user_registration(username, email, password)
        response_body, status = request_user_registration
        assert status == 201

        # second request to register user with the same credentials
        second_request_user_registration = api.user_registration(username, email, password)
        response_body, status = second_request_user_registration
        assert status == 400
        expected_response_body = {
            "code": "already_exist",
            "message": "User with this email is already exist"
        }
        assert response_body == expected_response_body

    @allure.feature('User registration')
    @allure.description('Register user with empty request body (negative)')
    @allure.severity('Minor')
    @pytest.mark.regression
    def test_user_registration_empty_request_negative(self, user_not_logged_in_session_fixture):
        api = UserAccount(user_not_logged_in_session_fixture)

        empty_request_body = {}  # custom type of request body, without "email" and "password" inside
        request_user_registration_custom_body = api.user_registration_custom_body(empty_request_body)
        response_body, status = request_user_registration_custom_body

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
            },
            {
              "loc": [
                "body",
                "email"
              ],
              "msg": "field required",
              "type": "value_error.missing"
            },
            {
              "loc": [
                "body",
                "password"
              ],
              "msg": "field required",
              "type": "value_error.missing"
            }
          ]
        }
        assert response_body == expected_response_body

    @allure.feature('User registration')
    @allure.description('Register user with no email provided (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_user_registration_no_email_provided_negative(self, user_not_logged_in_session_fixture):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        api = UserAccount(user_not_logged_in_session_fixture)

        request_body = {
            "username": username,
            "password": password
        }  # custom type of request body, without "email" inside
        request_user_registration_custom_body = api.user_registration_custom_body(request_body)
        response_body, status = request_user_registration_custom_body

        assert status == 422
        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "email"
              ],
              "msg": "field required",
              "type": "value_error.missing"
            }
          ]
        }
        assert response_body == expected_response_body

        # delete username, email (not used) and password generated for the test before
        email_and_password_generator.delete_email_generated()

    @allure.feature('User registration')
    @allure.description('Register user with no password provided (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_user_registration_no_password_provided_negative(self, user_not_logged_in_session_fixture):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        api = UserAccount(user_not_logged_in_session_fixture)

        request_body = {
            "username": username,
            "email": email
        }  # custom type of request body, without "password" inside
        request_user_registration_custom_body = api.user_registration_custom_body(request_body)
        response_body, status = request_user_registration_custom_body

        assert status == 422
        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "password"
              ],
              "msg": "field required",
              "type": "value_error.missing"
            }
          ]
        }
        assert response_body == expected_response_body

        # delete username, email and password (not used) generated for the test before
        email_and_password_generator.delete_email_generated()

    @allure.feature('User registration')
    @allure.description('Register user with empty email value (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_user_registration_empty_email_negative(self, user_not_logged_in_session_fixture):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        api = UserAccount(user_not_logged_in_session_fixture)

        request_body = {
            "username": username,
            "email": "",
            "password": password
        }  # custom type of request body, with empty string for "email" inside
        request_user_registration_custom_body = api.user_registration_custom_body(request_body)
        response_body, status = request_user_registration_custom_body

        assert status == 422
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

        # delete username, email (not used) and password generated for the test before
        email_and_password_generator.delete_email_generated()

    @allure.feature('User registration')
    @allure.description('Register user with empty password value (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_user_registration_empty_password_negative(self, user_not_logged_in_session_fixture):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        api = UserAccount(user_not_logged_in_session_fixture)

        request_body = {
            "username": username,
            "email": email,
            "password": ""
        }  # custom type of request body, with empty string for "password" inside
        request_user_registration_custom_body = api.user_registration_custom_body(request_body)
        response_body, status = request_user_registration_custom_body

        assert status == 422
        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "password"
              ],
              "msg": "Password must contain between 8 and 32 symbols (numbers and/or letters and/or special characters)",
              "type": "value_error"
            }
          ]
        }
        assert response_body == expected_response_body

        # delete username, email and password (not used) generated for the test before
        email_and_password_generator.delete_email_generated()

    @allure.feature('User registration')
    @allure.description('Register user with too short password, 7-symbols long (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_user_registration_too_short_password_negative(self, user_not_logged_in_session_fixture):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        # since password generated is 8-symbols_long
        seven_symbols_password = password[:-1] # we remove the last symbol to make it shorter

        api = UserAccount(user_not_logged_in_session_fixture)

        request_body = {
            "username": username,
            "email": email,
            "password": seven_symbols_password
        }
        request_user_registration_custom_body = api.user_registration_custom_body(request_body)
        response_body, status = request_user_registration_custom_body

        assert status == 422
        expected_response_body = {
          "detail": [
            {
              "loc": [
                "body",
                "password"
              ],
              "msg": "Password must contain between 8 and 32 symbols (numbers and/or letters and/or special characters)",
              "type": "value_error"
            }
          ]
        }

        assert response_body == expected_response_body

        # delete username, email and password generated for the test before
        email_and_password_generator.delete_email_generated()

    @allure.feature('User registration')
    @allure.description('Register user with too long password, 33-symbols long (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_user_registration_too_long_password_negative(self, user_not_logged_in_session_fixture):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        # since the password generated is 8-symbols_long,
        # we need to create another one instead, 33-symbols long
        password_symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
        long_password = ''.join(random.choice(password_symbols) for i in range(33))

        api = UserAccount(user_not_logged_in_session_fixture)

        request_body = {
            "username": username,
            "email": email,
            "password": long_password
        }
        request_user_registration_custom_body = api.user_registration_custom_body(request_body)
        response_body, status = request_user_registration_custom_body

        assert status == 422
        expected_response_body = {
            "detail": [
                {
                    "loc": [
                        "body",
                        "password"
                    ],
                    "msg": "Password must contain between 8 and 32 symbols (numbers and/or letters and/or special characters)",
                    "type": "value_error"
                }
            ]
        }

        assert response_body == expected_response_body

        # delete username, email and password generated for the test before
        email_and_password_generator.delete_email_generated()


    @allure.feature('User registration')
    @allure.description('Register user with email already used (negative)')
    @allure.severity('Blocker')
    @pytest.mark.regression
    def test_user_registration_email_already_used_negative(self, new_user_logged_in_session_fixture, user_not_logged_in_session_fixture):
        # precondition: to have a user account already created
        username = new_user_logged_in_session_fixture[6]
        email = new_user_logged_in_session_fixture[1]
        password = new_user_logged_in_session_fixture[2]

        # create session (empty, no user authorized yet)
        user_not_authorized_session = user_not_logged_in_session_fixture
        #  next API calls will be done using not-authorized session
        api = UserAccount(user_not_authorized_session)

        # try to register user with the credentials of user that already exists in the system
        request_user_registration = api.user_registration(username, email, password)
        response_body, status = request_user_registration

        assert status == 400
        expected_response_body = {
            "code": "already_exist",
            "message": "User with this email is already exist"
        }
        assert response_body == expected_response_body

        # now the user account and the email created before will be
        # automatically deleted by the new_user_logged_in_session_fixture

