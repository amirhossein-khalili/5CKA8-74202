from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class SignUpViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")  # adjust namespace if needed

    def test_signup_success(self):
        data = {"username": "newuser", "password": "ComplexPass123!"}
        resp = self.client.post(self.url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Should contain all four keys
        for key in ("access", "refresh", "token_type", "expires_in"):
            self.assertIn(key, resp.data)
        # User was created
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_missing_fields(self):
        resp = self.client.post(self.url, {"username": "u"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", resp.data)

    def test_signup_password_validation(self):
        # Too short / too common password
        data = {"username": "user2", "password": "123"}
        resp = self.client.post(self.url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", resp.data)


class SignInViewTests(APITestCase):
    def setUp(self):
        self.signup_url = reverse("accounts:signup")
        self.login_url = reverse("accounts:signin")
        # create a user to authenticate against
        self.user = User.objects.create_user(
            username="existing", password="MySecretPass!23"
        )

    def test_signin_success(self):
        data = {"username": self.user.username, "password": "MySecretPass!23"}
        resp = self.client.post(self.login_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Should contain JWT tokens
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_signin_invalid_credentials(self):
        data = {"username": "existing", "password": "WrongPass"}
        resp = self.client.post(self.login_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        # Error should mention authorization
        self.assertTrue("authorization" in str(resp.data).lower())
