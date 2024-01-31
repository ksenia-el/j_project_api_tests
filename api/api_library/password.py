import requests
import allure
import os

class Password:

    def __init__(self, session):
        self.base_url = os.environ.get("BASIC_URL")
        self.session = session

    @allure.step('Send request to change password in profile')
    # change password while being authorized and being in the user profile
    def change_password_in_profile(self, old_password, new_password):
        request_body = {
            "newPassword1": new_password,
            "newPassword2": new_password,
            "oldPassword": old_password
        }

        response = self.session.post(
            self.base_url + "/api/password/change_password_in_profile",
            json=request_body  # !use this form for each request in JSON format, no "json.dumps()" needed
        )
        status = response.status_code
        return response.json(), status

    @allure.step('Send request to request password recovery by email or username (1st step in the whole process)')
    # the next 3 methods are used for 3-steps process to reset a new password instead of the old that was forgotten
    def request_password_recovery_by_email_or_username(self, email_or_username):
        request_body = {
            "recoveryField": email_or_username
        }

        response = requests.post(
            self.base_url + "/api/password/request_password_recovery",
            json=request_body
        )
        status = response.status_code
        return response.json(), status

    @allure.step('Send request to confirm password recovery (2nd step in the whole process)')
    def confirm_password_recovery(self, reset_token):
        response = requests.get(
            self.base_url + f"/api/password/reset_password?reset_token={reset_token}"
        )
        status = response.status_code
        return response.text, status

    @allure.step('Send request to reset password recovery (3rd step in the whole process)')
    def reset_password(self, new_password, reset_token):
        request_body = {
            "newPassword1": new_password,
            "newPassword2": new_password,
            "resetToken": reset_token
        }
        response = requests.post(
            self.base_url + "/api/password/reset_password",
            json=request_body
        )
        status = response.status_code
        return response.json(), status


    #  ------ NEXT METHODS ARE USED IN NEGATIVE TESTS (to run API-calls with custom request body if needed)

    @allure.step('Send request to change password in profile, but with custom request body)')
    # change password while being authorized and being in the user profile
    def change_password_in_profile_custom_body(self, request_body):
        response = self.session.post(
            self.base_url + "/api/password/change_password_in_profile",
            json=request_body  # !use this form for each request in JSON format, no "json.dumps()" needed
        )
        status = response.status_code
        return response.json(), status

    @allure.step('Send request to request password recovery, but with custom request body')
    def request_password_recovery_custom_body(self, request_body):
        response = requests.post(
            self.base_url + "/api/password/request_password_recovery",
            json=request_body
        )
        status = response.status_code
        return response.json(), status

    @allure.step('Send request to reset password, but with custom request body')
    def reset_password_custom_body(self, request_body):
        response = requests.post(
            self.base_url + "/api/password/reset_password",
            json=request_body
        )
        status = response.status_code
        return response.json(), status
