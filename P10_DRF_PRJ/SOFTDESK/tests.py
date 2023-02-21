from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from SOFTDESK.models import User, Project, Contributors


class SoftDeskTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='user1')
        self.user2 = User.objects.create_user(username='user2', password='user2')
        self.project2 = Project.objects.create(title='project2', description='project2', author=self.user1)

    @staticmethod
    def get_token(response):
        token = response.data['access']
        return f'Bearer {token}'


class TestUser(SoftDeskTestCase):
    # check if user can register
    def test_user_can_register(self):
        user_data = {'username': 'user1', 'password': 'user1'}
        response = self.client.post('/register/', user_data)
        self.assertEqual(response.status_code, 200, response.data)

    # check if login return JWT access & refresh token
    def test_user_can_login(self):
        user_data = {'username': 'user1', 'password': 'user1'}
        response = self.client.post('/login/', user_data)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class TestProject(SoftDeskTestCase):
    # test if user can get project list
    def test_user_can_get_project_list(self):
        url = reverse_lazy('projects-list')
        login_response = self.client.post('/login/', {'username': 'user1', 'password': 'user1'})
        token = self.get_token(login_response)
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)

    # test if user can create project
    def test_user_can_create_project(self):
        url = reverse_lazy('projects-list')
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_token(self.client.post('/login/', {'username': 'user1', 'password': 'user1'})))
        data = {'title': 'test', 'description': 'test'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data, {'id': 2, 'title': 'test', 'description': 'test'})

    # test if user can get project detail
    def test_user_can_get_project_detail(self):
        url = reverse_lazy('projects-detail', kwargs={'pk': self.project2.id})
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_token(self.client.post('/login/', {'username': 'user1', 'password': 'user1'})))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('title', response.data)

    # test if user can update project
    def test_user_can_update_project(self):
        url = reverse_lazy('projects-detail', kwargs={'pk': self.project2.id})
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_token(self.client.post('/login/', {'username': 'user1', 'password': 'user1'})))
        data = {'title': 'test', 'description': 'test_edit'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('test_edit', response.data['description'])

    def test_user_can_delete_project(self):
        # todo: check if project deletion also deletes related issues and comments
        url = reverse_lazy('projects-detail', kwargs={'pk': self.project2.id})
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_token(self.client.post('/login/', {'username': 'user1', 'password': 'user1'})))
        initial_count = Project.objects.count()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)
        self.assertEqual(Project.objects.count(), initial_count - 1)

    # test if user can add contributor to project
    def test_user_can_add_contributor_to_project(self):
        url = reverse_lazy('projects-contributors', kwargs={'pk': self.project2.id})
        contributors_count = self.project2.contributors.count()

        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_token(self.client.post('/login/', {'username': 'user1', 'password': 'user1'})))
        data = {'user_id': 2}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201, response.status_code)
        self.assertEqual(self.project2.contributors.count(), contributors_count + 1)
        # print(response.data)

    # test if author can get contributor's list from project
    def test_author_can_get_user_as_contributor(self):
        url = reverse_lazy('projects-contributors', kwargs={'pk': self.project2.id})
        self.contributor = Contributors.objects.create(permission='Read and Edit', role='test_role',
                                                       user_id=self.user2.id, project_id=self.project2.id)
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_token(self.client.post('/login/', {'username': 'user1', 'password': 'user1'})))
        response = self.client.get(url)
        print(response.data)
