# from django.db import transaction
# from django.db.models import Q
from sys import stderr, stdout

from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .helper import ContributorHelper, IssueHelper, CommentHelper
from .models import Project, Contributors
from .serializers import ProjectSerializer, ProjectDetailSerializer, \
    UserCreationSerializer


class AsProjectPermission(BasePermission):
    def has_permission(self, request, view):
        print(f'safe method = {SAFE_METHODS}',file=stderr)
        print(f'actual method = {request.method}',file=stdout)
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user == obj.author:
            print(f'isAuthor: {request.user==obj.author}',file=stderr)
            return True
        elif request.method in SAFE_METHODS:
            print(f'isInSafeMethod : {request.method in SAFE_METHODS}',file=stderr)
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
    user = authenticate(request, username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)

        return Response({'status': 'logged in',
                         'refresh': str(refresh),
                         'access': str(refresh.access_token)})
    return Response({'status': 'authentication failed'})


class ProjectViewSet(ModelViewSet):
    model = Project
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated(),AsProjectPermission()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        author_querry = Project.objects.filter(author=self.request.user)
        contributors_querry = Project.objects.filter(contributors__user=self.request.user)
        author_querry = author_querry.union(contributors_querry)
        idlist = [p.id for p in author_querry]
        queryset = Project.objects.filter(id__in=idlist)
        return queryset

    def get_permissions(self):
        if self.action == 'list':
            return [AsProjectPermission(), IsAuthenticated()]
        elif self.action == 'retrieve':
            return [AsProjectPermission(), IsAuthenticated()]
        elif self.action == 'update' or self.action == 'partial_update':
            return [AsProjectPermission(), IsAuthenticated()]
        elif self.action == 'issue_precise':
            return [AsProjectPermission(),IsAuthenticated()]
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

    ### Contributors View ###
    @action(methods=['post', 'get'], detail=True,
            url_path='user',
            url_name='contributors',
            permission_classes=[AsProjectPermission(),
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
            permission_classes=[AsProjectPermission(),
                                IsAuthenticated()])
    def contributors_delete(self, request, pk=None, contributor_pk=None):
        return ContributorHelper.delete_contributor(self.get_object(), contributor_pk)

    ### Issue View ###
    @action(methods=['post', 'get'], detail=True, url_path='issue', url_name='issue_add-list',
            permission_classes=[AsProjectPermission(), IsAuthenticated()])
    def issue_general(self, request, pk=None):
        project = self.get_object()

        if request.method == 'GET':
            return IssueHelper.get_issues_list(project)
        elif request.method == 'POST':
            return IssueHelper.add_issue(project, request)

    @action(methods=['patch', 'get', 'delete', 'put'], detail=True, url_path='issue/(?P<issue_pk>[^/.]+)',
            url_name='issue_update-delete',
            permission_classes=[AsProjectPermission(), IsAuthenticated()])
    def issue_precise(self, request, pk=None, issue_pk=None):
        project = self.get_object()
        if request.method == 'PATCH' or request.method == 'PUT':
            return IssueHelper.update_issue(request, issue_pk)
        elif request.method == 'GET':
            return IssueHelper.get_issue_detail(issue_pk, project)
        elif request.method == 'DELETE':
            return IssueHelper.delete_issue(request, project, issue_pk)
        return Response(status=404)

    ### Comment View ###
    @action(methods=['post', 'get'], detail=True, url_path='issue/(?P<issue_pk>[^/.]+)/comments',
            url_name='comment_create-&-get',
            permission_classes=[AsProjectPermission(), IsAuthenticated()])
    def comment_general(self, request, pk=None, issue_pk=None):
        project = self.get_object()

        if request.method == 'GET':
            return CommentHelper.get_comments_list(project, issue_pk)
        elif request.method == 'POST':
            return CommentHelper.add_comment(issue_pk, request)

    @action(methods=['get', 'patch', 'delete', 'put'], detail=True, url_path='issue/(?P<issue_pk>[^/.]+)/comments/('
                                                                             '?P<comment_pk>[^/.]+)',
            url_name='comment_detail-&-update-&-delete',
            permission_classes=[AsProjectPermission(), IsAuthenticated()])
    def comment_detail(self, request, pk=None, issue_pk=None, comment_pk=None):
        project = self.get_object()
        if request.method == 'GET':
            return CommentHelper.get_comment_detail(project=project, issue_pk=issue_pk, comment_pk=comment_pk)
        elif request.method == 'PATCH' or request.method == 'PUT':
            return CommentHelper.update_comment(request, project, issue_pk, comment_pk)
        elif request.method == 'DELETE':
            return CommentHelper.delete_comment(request, project, issue_pk, comment_pk)
