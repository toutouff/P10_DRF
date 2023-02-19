from rest_framework.test import APITestCase

from SOFTDESK import models


class SOFTDESKTestCase(APITestCase):
    user = None
    project = None
    contributors = None
    issue = None

    @classmethod
    def setUp(cls):
        cls.user = models.User.objects.create_user(first_name='john',
                                                   last_name='doe',
                                                   username='john_doe',
                                                   password='test_password')
        cls.project = models.Project.objects.create(title='test_project',
                                                    description='test_description',
                                                    type='test_type',
                                                    author=cls.user)
        cls.contributors = models.Contributors.objects.create(permision='R',
                                                              role='test_role',
                                                              user=cls.user,
                                                              project=cls.project)
        cls.issue = models.Issue.objects.create(title='test_issue',
                                                description='test_description',
                                                tag='test_tag',
                                                priority='test_priority',
                                                project=cls.project,
                                                status='test_status',
                                                author=cls.user,
                                                assigned_to=cls.contributors)


class TestUser(SOFTDESKTestCase):
    def test_register(self):
        response = self.client.post('/register/', {'username': 'test_user',
                                                   'password': 'test_password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'registered')
        logged = self.client.login(username='test_user',
                                   password='test_password')
        self.assertTrue(logged)

    def test_login(self):
        response = self.client.post('/login/', {'username': 'john_doe',
                                                'password': 'test_password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('logged in', response.data['status'])


class TestProject(SOFTDESKTestCase):
    def test_project_list(self):
        self.client.login(username='john_doe', password='test_password')
        response = self.client.get('/api/project/')
        self.assertEqual(response.status_code, 200)

    def test_project_detail(self):
        self.client.login(username='john_doe', password='test_password')
        response = self.client.get('/api/project/1/')
        self.assertEqual(response.status_code, 200)


class TestContributors(SOFTDESKTestCase):
    def test_contributors_creation(self):
        self.assertEqual(self.contributors.permision, 'R')
        self.assertEqual(self.contributors.role, 'test_role')
        self.assertEqual(self.contributors.user, self.user)
        self.assertEqual(self.contributors.project, self.project)


class TestIssue(SOFTDESKTestCase):
    def test_issue_creation(self):
        self.assertEqual(self.issue.title, 'test_issue')
        self.assertEqual(self.issue.description, 'test_description')
        self.assertEqual(self.issue.tag, 'test_tag')
        self.assertEqual(self.issue.priority, 'test_priority')
        self.assertEqual(self.issue.project, self.project)
        self.assertEqual(self.issue.status, 'test_status')
        self.assertEqual(self.issue.author, self.user)
        self.assertEqual(self.issue.assigned_to, self.contributors)
