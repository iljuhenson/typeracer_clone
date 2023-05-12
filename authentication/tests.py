from rest_framework.test import APITestCase


class UserAuthenticationTestCase(APITestCase):
    def setUp(self):
        self.username = 'TestUser1'
        self.password = 'TestPass.123'
        self.email = 'testuser@tester.com'
        self.first_name = 'John'
        self.last_name = 'Smith'

    def test_signup_api_view(self):
        response = self.client.post('/api/signup/', {'username' : self.username, 'password' : self.password, 'password2' : self.password, 'email' : self.email, 'first_name' : self.first_name, 'last_name' : self.last_name})
        self.assertEqual(response.status_code, 201)

    def test_signup_api_view_wrong_second_password(self):
        response = self.client.post('/api/signup/', {'username' : self.username, 'password' : self.password, 'password2' : 'WrongPassword', 'email' : self.email, 'first_name' : self.first_name, 'last_name' : self.last_name})
        self.assertEqual(response.status_code, 400)

    def test_logout_api_view(self):
        self.client.post('/api/signup/', {'username' : self.username, 'password' : self.password, 'password2' : self.password, 'email' : self.email, 'first_name' : self.first_name, 'last_name' : self.last_name})
        response = self.client.post('/api/login/', {'username' : self.username, 'password' : self.password})
        
        access_token = response.data['access']
        refresh_token = response.data['refresh']

        headers = {'Authorization': f"Bearer {access_token}"}
        logout_response = self.client.post('/api/logout/', {'refresh' : refresh_token}, headers=headers)
        self.assertEqual(logout_response.status_code, 205)
        refresh_token_action_response = self.client.post('/api/login/refresh/', {'refresh' : refresh_token})
        self.assertEqual(refresh_token_action_response.status_code, 401)