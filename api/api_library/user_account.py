import requests
import allure
import os

class UserAccount:

    def __init__(self, session):
        self.base_url = os.environ.get("BASIC_URL")
        self.session = session

    @allure.step('Send request to register user')
    def user_registration(self, username, email, password):
        request_body = {
            "username": username,
            "email": email,
            "password": password
        }

        response = self.session.post(
            self.base_url + "/api/registration",
            json=request_body  # !use this form for each request in JSON format, no "json.dumps()" needed
        )
        status = response.status_code
        return response.json(), status

    @allure.step('Send request to confirm email with token')
    def confirm_email(self, token):
        response = self.session.get(
            self.base_url + f"/api/email/confirm_email/{token}"
        )
        return response.json(), response.status_code

    @allure.step('Send request to log in with email or username')
    def log_in_with_email_or_username(self, email_or_username, password):
        request_body = {
            "username": email_or_username,
            "password": password
        }
        response = self.session.post(
            self.base_url + "/api/login/oauth",
            data=request_body  # !use this form for each request in x-www-form-urlencoded format
        )
        status = response.status_code
        # by "response_data.get()" we can later obtain values from such fields: "user_profile_id",
        # "user_role", "user_status", "access_token"
        return response.json(), status


    @allure.step('Send request to log out')
    def user_logout(self):
        response = self.session.post(
            self.base_url + "/api/logout"
        )
        return response.json(), response.status_code

    @allure.step('Send request to request delete user (start)')
    def request_delete_user(self):
        response = self.session.post(
            self.base_url + "/api/delete/request_delete"
        )
        return response.json(), response.status_code

    @allure.step('Send request to delete user (finish)')
    def delete_user(self, code):
        response = self.session.delete(
            self.base_url + f"/api/delete/user/{code}"
        )
        return response.json(), response.status_code


    @allure.step('Send request to request email verify (start)')
    def request_email_verify(self, email):
        request_body = {"email": email}
        response = self.session.post(
            self.base_url + "/api/email/request_email_verify",
            json=request_body
        )
        return response.json(), response.status_code

    @allure.step('Send request to check username')
    def username_check(self, username):
        request_body = {"username": username}
        response = self.session.post(
            self.base_url + "/api/registration/username_check",
            json=request_body
        )
        return response, response.status_code

    @allure.step('Send request to register user with a custom request body')
    def user_registration_custom_body(self, request_body):
        response = self.session.post(
            self.base_url + "/api/registration",
            json=request_body
        )
        status = response.status_code
        return response.json(), status

    @allure.step('Send request to log in with email but with custom request body')
    def log_in_with_email_custom_body(self, request_body):
        response = self.session.post(
            self.base_url + "/api/login/oauth",
            data=request_body  # !use this form for each request in x-www-form-urlencoded format
        )
        status = response.status_code
        return response.json(), status

    @allure.step('Send request to check username but with custom request body')
    def username_check_custom_body(self, request_body):
        response = self.session.post(
            self.base_url + "/api/registration/username_check",
            json=request_body
        )
        return response, response.status_code
