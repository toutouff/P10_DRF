from django.contrib.auth.models import AbstractUser as A_USER
from django.db import models


# Create your models here.


class User(A_USER):
    pass


class Project(models.Model):
    title = models.CharField(max_length=80, )
    description = models.TextField(max_length=250)
    type = models.CharField(max_length=80)
    author = models.ForeignKey('User', on_delete=models.CASCADE,
                               related_name='projects')


class Issue(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField(max_length=250)
    tag = models.CharField(max_length=80, blank=True)
    priority = models.CharField(max_length=80, blank=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE,
                                related_name='issues', )
    status = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey('User', on_delete=models.CASCADE,
                               related_name='issues', blank=False)
    assigned_to = models.ForeignKey('Contributors',
                                    on_delete=models.CASCADE,
                                    related_name='issues')


class Comments(models.Model):
    description = models.TextField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey('User', on_delete=models.CASCADE,
                               related_name='comments')
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE,
                              related_name='comments')


class Contributors(models.Model):
    readOnly = 'R'
    readEdit = 'RE'
    readEditDelete = 'RED'
    permision_choice = [
        (readOnly, 'ReadOnly'),
        (readEdit, 'Read and Edit'),
        (readEditDelete, 'Read,Edit and Delete')]
    permission = models.CharField(max_length=3,
                                  choices=permision_choice,
                                  default=readOnly, )
    role = models.CharField(max_length=25, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='contributors', blank=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name='contributors', blank=False)
