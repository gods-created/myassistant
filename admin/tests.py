from django.test import TestCase
from unittest.mock import patch
from .models import Admin

class Tests(TestCase):
    @patch('admin.models.Admin.objects.validate_admin')
    def test_validate_admin_method(self, mock_object):
        mock_object.return_value = True
        email, password = 'test@example.com', 'test123456789'
        response = Admin.objects.validate_admin(email, password)
        mock_object.assert_called_once_with(email, password)

        self.assertTrue(response)