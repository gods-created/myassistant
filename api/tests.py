from django.test import TestCase
from json import dumps
from oauth2_provider.models import Application
from admin.models import Admin


class Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.access_token = None
        
        cls.user = Admin.objects.create(
            email='test@gmail.com',
            password='test123456789',
            is_staff=True,
            is_active=True
        )
        
        cls.app = Application.objects.create(
            user=cls.user,
            authorization_grant_type='client-credentials',
            client_type='confidential',
        )
        
        cls.data = {
            'data': [
                {'choosen': 20}, {'choosen': 25}, {'choosen': 100}, {'choosen': 1000}, {'choosen': 4000}, {'choosen': 10}
            ],
            'n_clusters': 3
        }

    def get_access_token(self):
        data = {
            'client_id': self.app.client_id,
            'client_secret': self.app.client_secret
        }
        
        response = self.client.post(
            path='/api/auth/',
            data=dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        access_token = response_data.get('access_token')
        self.assertIsNotNone(access_token, 'Access token not received')
        return access_token

    def test_1_auth(self):
        access_token = self.get_access_token()
        Tests.access_token = access_token 
    
    def test_2_clustering(self):
        if not self.access_token:
            self.access_token = self.get_access_token() 
        
        data = self.data
        
        response = self.client.post(
            path='/api/clustering/',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
            data=dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        print(response_data)
        
        clusters = any([item.get('cluster', None) for item in response_data.get('data', [])])
        self.assertTrue(clusters, 'Clusters not found in response')

    @classmethod
    def tearDownClass(cls):
        cls.app.delete()
        cls.user.delete()
        super().tearDownClass()
