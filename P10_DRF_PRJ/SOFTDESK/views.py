# from django.db import transaction
# from django.db.models import query
from sys import stderr

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .helper import ContributorHelper, IssueHelper, CommentHelper
from .models import Project, Contributors
from .serializers import ProjectSerializer, ProjectDetailSerializer, \
    UserCreationSerializer


class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if obj.author == request.user:
            return True
        return False


class IsContributor(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        for contributor in obj.contributors:
            if contributor.user.id == request.user.id:
                return True
        return False


@api_view(['POST'])
def sign_up(request):
    serializer = UserCreationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['POST'])
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        return Response({'status': 'logged in', })
    return Response({'status': 'authentication failed'})


class ProjectViewSet(ModelViewSet):
    model = Project
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        authorset = Project.objects.filter(author = user)
        return authorset

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthor()or IsContributor(),IsAuthenticated()]
        elif self.action == 'retrieve':
            return [IsAuthor() or IsContributor(), IsAuthenticated()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ProjectDetailSerializer
        elif self.action == 'contributors':
            return ProjectDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'get'], detail=True,
            url_path='user',
            url_name='contributors',
            permission_classes=[(IsAuthor() or IsContributor()) and
                                IsAuthenticated()])
    def contributors(self, request, pk=None):
        project = self.get_object()
        if request.method == 'GET':
            return ContributorHelper.get_contributor(project)
        elif request.method == 'POST':
            return ContributorHelper.add_contributor(project, request)

    @action(methods=['delete'], detail=True,
            url_path='user/(?P<contributor_pk>[^/.]+)',
            url_name='contributors-delete',
            permission_classes=[(IsAuthor() or IsContributor()) and
                                IsAuthenticated()])
    def contributors_delete(self, request, pk=None, contributor_pk=None):
        return ContributorHelper.delete_contributor(request, contributor_pk)

    @action(methods=['post', 'get'], detail=True, url_path='issue', url_name='issue_add-list',
            permission_classes=[(IsAuthor() or IsContributor()) and IsAuthenticated()])
    def issue_general(self, request, pk=None):
        project = self.get_object()

        if request.method == 'GET':
            return IssueHelper.get_issues_list(project)
        elif request.method == 'POST':
            return IssueHelper.add_issue(project, request)

    @action(methods=['patch', 'get', 'delete', 'put'], detail=True, url_path='issue/(?P<issue_pk>[^/.]+)',
            url_name='issue_update-delete',
            permission_classes=[(IsAuthor() or IsContributor()) and IsAuthenticated()])
    def issue_precise(self, request, pk=None, issue_pk=None):

        if request.method == 'PATCH' or request.method == 'PUT':
            return IssueHelper.update_issue(request, issue_pk)
        elif request.method == 'GET':
            return IssueHelper.get_issue_detail(issue_pk)
        elif request.method == 'DELETE':
            return IssueHelper.delete_issue(request, issue_pk)
        return Response(status=404)

    @action(methods=['post', 'get'], detail=True, url_path='issue/(?P<issue_pk>[^/.]+)/comments',
            url_name='comment_create-&-get',
            permission_classes=[(IsAuthor() or IsContributor()) and IsAuthenticated()])
    def comment_general(self, request, pk=None, issue_pk=None):

        if request.method == 'GET':
            return CommentHelper.get_comments_list(issue_pk)
        elif request.method == 'POST':
            return CommentHelper.add_comment(issue_pk, request)

    @action(methods=['get', 'patch', 'delete', 'put'], detail=True, url_path='issue/(?P<issue_pk>[^/.]+)/comments/('
                                                                             '?P<comment_pk>[^/.]+)',
            url_name='comment_detail-&-update-&-delete',
            permission_classes=[(IsAuthor() or IsContributor()) and IsAuthenticated()])
    def comment_detail(self, request, pk=None, issue_pk=None, comment_pk=None):

        if request.method == 'GET':
            return CommentHelper.get_comment_detail(comment_pk)
        elif request.method == 'PATCH' or request.method == 'PUT':
            return CommentHelper.update_comment(request, comment_pk)
        elif request.method == 'DELETE':
            return CommentHelper.delete_comment(request, comment_pk)
