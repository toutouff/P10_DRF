from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from SOFTDESK.models import User, Project, Contributors, Issue, Comments


class SoftDeskTestCase(APITestCase):
    def setUp(self):
        self.userinfo = {'username': 'user1', 'password': 'user1'}
        self.user1 = User.objects.create_user(username='user1', password='user1')
        self.user2 = User.objects.create_user(username='user2', password='user2')
        self.project2 = Project.objects.create(title='project2', description='project2', author=self.user1)
        self.contributor = Contributors.objects.create(permission='Read and Edit', role='test_role',
                                                       user_id=self.user2.id, project_id=self.project2.id)
        self.issue = Issue.objects.create(title='issue1', description='issue1', author=self.user1,
                                          project=self.project2, status='open', assigned_to=self.contributor)
        self.comment = Comments.objects.create(description='comment1', author=self.user1, issue=self.issue)

    @staticmethod
    def get_token(response):
        token = response.data['access']
        return f'Bearer {token}'

    @staticmethod
    def log_user(client, user_info):
        response = client.post('/login/', {'username': user_info['username'], 'password': user_info['password']})
        token = SoftDeskTestCase.get_token(response)
        client.credentials(HTTP_AUTHORIZATION=token)
        return client


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
        data = {'permission': 'RE', 'role': 'test_role', 'user': self.user2.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(self.project2.contributors.count(), contributors_count + 1)

    # test if author can get contributor's list from project
    def test_author_can_get_user_as_contributor(self):
        url = reverse_lazy('projects-contributors', kwargs={'pk': self.project2.id})
        self.client.credentials(
            HTTP_AUTHORIZATION=self.get_token(self.client.post('/login/', {'username': 'user1', 'password': 'user1'})))
        self.client.get(url)

    def test_author_can_delete_project(self):
        url = reverse_lazy('projects-contributors-delete', kwargs={'pk': self.project2.id, 'contributor_pk':
            self.contributor.id})
        self.client.credentials(HTTP_AUTHORIZATION=self.get_token(self.client.post('/login/', {'username': 'user1',
                                                                                               'password': 'user1'})))
        count = Contributors.objects.all().count()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(count - 1, self.project2.contributors.count())

    def test_user_can_get_issues(self):
        url = reverse_lazy('projects-issue_add-list', kwargs={'pk': self.project2.id})
        self.client.credentials(HTTP_AUTHORIZATION=self.get_token(self.client.post('/login/', {'username': 'user1',
                                                                                               'password': 'user1'})))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('title', response.data[0])

    def test_user_can_create_issue(self):
        url = reverse_lazy('projects-issue_add-list', kwargs={'pk': self.project2.id})
        count = self.project2.issues.count()
        self.client.credentials(HTTP_AUTHORIZATION=self.get_token(self.client.post('/login/', {'username': 'user1',
                                                                                               'password': 'user1'})))
        data = {'title': 'test', 'description': 'test', 'status': 'open', 'assigned_to': self.contributor.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(self.project2.issues.count(), count + 1)

    def test_user_can_update_issue(self):
        url = reverse_lazy('projects-issue_update-delete', kwargs={'pk': self.project2.id, 'issue_pk': self.issue.id})
        client = self.log_user(self.client, self.userinfo)
        data = {'title': 'test', 'description': 'test_edit', 'status': 'open', 'assigned_to': self.contributor.id}
        response = client.put(url, data)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn('test_edit', response.data['description'])

    def test_user_can_delete_issue(self):
        url = reverse_lazy('projects-issue_update-delete', kwargs={'pk': self.project2.id, 'issue_pk': self.issue.id})
        client = self.log_user(self.client, self.userinfo)
        count = self.project2.issues.count()
        response = client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)
        self.assertEqual(self.project2.issues.count(), count - 1)

    def test_user_can_create_comment(self):
        url = reverse_lazy('projects-comment_create-&-get', kwargs={'pk': self.project2.id, 'issue_pk': self.issue.id})
        count = self.issue.comments.count()
        client = self.log_user(self.client, self.userinfo)
        data = {'description': 'test'}
        response = client.post(url, data)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(self.issue.comments.count(), count + 1)

    def test_user_can_get_comments(self):
        url = reverse_lazy('projects-comment_create-&-get', kwargs={'pk': self.project2.id, 'issue_pk': self.issue.id})
        client = self.log_user(self.client, self.userinfo)
        response = client.get(url)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('comment1', response.data[0]['description'])

    def test_user_can_update_coment(self):
        url = reverse_lazy('projects-comment_detail-&-update-&-delete', kwargs={'pk': self.project2.id, 'issue_pk':
            self.issue.id, 'comment_pk': self.comment.id})
        client = self.log_user(self.client, self.userinfo)
        data = {'description': 'test_edit'}
        response = client.put(url, data)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn('test_edit', response.data['description'])

    def test_user_can_delete_comment(self):
        url = reverse_lazy('projects-comment_detail-&-update-&-delete',
                           kwargs={'pk': self.project2.id, 'issue_pk': self.issue.id,
                                   'comment_pk': self.comment.id})
        client = self.log_user(self.client, self.userinfo)
        count = self.issue.comments.count()
        response = client.delete(url)
        self.assertEqual(response.status_code, 204, response.data)
        self.assertEqual(self.issue.comments.count(), count - 1)


