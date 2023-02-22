# from django.db import transaction
# from django.db.models import query

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Project, User, Contributors, Issue, Comments
from .serializers import ProjectSerializer, ProjectDetailSerializer, \
    ContributorsSerializer, IssueSerializer, CommentsSerializer, UserCreationSerializer, IssueCreationSerializer


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsContributor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if Contributors.objects.filter(user=request.user,
                                       project=obj).exists():
            return Contributors.objects.filter(user=request.user,
                                               project=obj).first().permision != 'R'
        return False


@api_view(['POST'])
def register(request):
    username, password = request.POST['username'], request.POST['password']
    user = User.objects.create_user(username=username, password=password)
    if user is not None:
        return Response({'status': 'registered'})
    return Response({'status': 'registration failed'})


@api_view(['POST'])
def register_2(request):
    serializer = UserCreationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
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


class ContributorHelper:
    @staticmethod
    def get_contributor(project):
        contributor_list = Contributors.objects.filter(project=project)
        return ContributorsSerializer(instance=contributor_list, many=True)

    @staticmethod
    def add_contributor(project, request, *args):
        """
        call add_contributor(project,data)
        """
        serializer = ContributorsSerializer(data=request.data)
        if serializer.is_valid():
            contributor = serializer.save(project=project)
            return Response(ContributorsSerializer(instance=contributor).data)
        return Response(serializer.errors)


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        elif self.action == 'retrieve':
            return [IsAuthor() or IsContributor(), IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Project.objects.filter(author=self.request.user)

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
    def contributors(self, request, contributor_pk=None, pk=None):
        project = self.get_object()
        if request.method == 'GET':
            data = ContributorsSerializer(
                Contributors.objects.filter(project=project), many=True).data
            return Response(data=data)
        elif request.method == 'POST':
            user_id = request.POST['user_id']
            if User.objects.filter(id=user_id).exists():
                contributor = Contributors.objects.create(project=project,
                                                          user_id=user_id)
                return Response(ContributorsSerializer(contributor).data, status=201)
            return Response('error : user does not exist')
        return Response(status=405)

    @action(methods=['delete'], detail=True,
            url_path='user/(?P<contributor_pk>[^/.]+)',
            url_name='contributors-delete',
            permission_classes=[(IsAuthor() or IsContributor()) and
                                IsAuthenticated()])
    def contributors_delete(self, request, pk=None, contributor_pk=None):
        if Contributors.objects.filter(id=contributor_pk).exists():
            contributor = Contributors.objects.get(id=contributor_pk)
            msg = f'contributor {contributor.user.username} ( id : {contributor.id} ) has been deleted'
            contributor.delete()
            return Response(msg, status=204)
        return Response(f'error : contributor (id : {contributor_pk}) does not exist')

    @action(methods=['post', 'get'], detail=True, url_path='issue', url_name='issue_add-list',
            permission_classes=[(IsAuthor() or IsContributor()) and IsAuthenticated()])
    def issue_general(self, request, pk=None):
        def issue_create():
            project = self.get_object()
            data = request.data
            serializer = IssueCreationSerializer(data=data)
            if serializer.is_valid():
                issue = serializer.save(project=project, author=request.user)
                return Response(serializer.data, status=201)
            return Response(serializer.errors)

        def issue_list():
            project = self.get_object()
            issue_list = Issue.objects.filter(project=project)
            issue_serializer = IssueSerializer(instance=issue_list, many=True)
            return Response(issue_serializer.data)

        if request.method == 'GET':
            return issue_list()
        elif request.method == 'POST':
            return issue_create()

    @action(methods=['patch', 'get', 'delete'], detail=True, url_path='issue/(?P<issue_pk>[^/.]+)',
            url_name='issue_update-delete',
            permission_classes=[(IsAuthor() or IsContributor()) and IsAuthenticated()])
    def issue_precise(self, request, pk=None, issue_pk=None):
        def issue_detail():
            queryset = Issue.objects.filter(id=issue_pk)
            if len(queryset):
                issue = queryset.first()
                serializer = IssueSerializer(instance=issue)
                return Response(serializer.data)

        def issue_update():
            queryset = Issue.objects.filter(id=issue_pk)
            if len(queryset):
                issue = queryset.first()
                serializer = IssueSerializer(instance=issue, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors)

        def issue_delete():
            queryset = Issue.objects.filter(id=issue_pk)
            if len(queryset):
                issue = queryset.first()
                msg = f'issue({issue.id} has been deleted'
                issue.delete()
                return Response(msg)
            return Response('error issue not found')

        if request.method == 'PATCH':
            return issue_update()
        elif request.method == 'GET':
            return issue_detail()
        elif request.method == 'DELETE':
            return issue_delete()
        return Response(status=404)

    @action(methods=['post', 'get'], detail=True, url_path='issue/(?P<issue_pk>[^/.]+)/comments',
            url_name='comment_create-&-get',
            permission_classes=[(IsAuthor() or IsContributor()) and IsAuthenticated()])
    def comment_general(self, request, pk=None, issue_pk=None):
        def list_comment():
            issue_set = Issue.objects.filter(id=issue_pk)
            if issue_set:
                issue = issue_set.first()
                comment_list = issue.comments
                serializer = CommentsSerializer(instance=comment_list, many=True)
                return Response(serializer.data)
            return Response('issue not found')

        def create_comment():
            issue_set = Issue.objects.filter(id=issue_pk)
            if len(issue_set):
                serializer = CommentsSerializer(data=request.data)
                if serializer.is_valid():
                    comment = serializer.save(author=request.user, issue=issue_set.first())
                    return Response(CommentsSerializer(instance=comment).data)
                return Response(serializer.errors)

        if request.method == 'GET':
            return list_comment()
        elif request.method == 'POST':
            return create_comment()

    @action(methods=['get', 'patch', 'delete'], detail=True, url_path='issue/(?P<issue_pk>[^/.]+)/comments/('
                                                                      '?P<comment_pk>[^/.]+)',
            url_name='comment_detail-&-update-&-delete',
            permission_classes=[(IsAuthor() or IsContributor()) and IsAuthenticated()])
    def comment_detail(self, request, pk=None, issue_pk=None, comment_pk=None):
        def detail_comment():
            if comment_tester():
                comment = Comments.objects.get(id=comment_pk)
                serializer = CommentsSerializer(instance=comment)
                return Response(serializer.data)
            return 'comment not found'

        def update_comment():
            if comment_tester():
                comment = Comments.objects.get(id=comment_pk)
                serializer = CommentsSerializer(instance=comment, data=request.data, partial=True)
                if serializer.is_valid():
                    comment = serializer.save()
                    return Response(CommentsSerializer(instance=comment).data)
                return Response(serializer.errors)
            return Response('comment not found')

        def delete_comment():
            if comment_tester():
                comment = Comments.objects.get(id=comment_pk)
                msg = f'comment({comment.id}) has been deleted'
                comment.delete()
                return Response(msg)
            return Response('comment not found')

        def issue_tester():
            return len(Issue.objects.filter(id=issue_pk)) >= 1

        def comment_tester():
            if issue_tester():
                return len(Comments.objects.filter(id=comment_pk)) >= 1
            return Response('issue not found')

        if request.method == 'GET':
            return detail_comment()
        elif request.method == 'PATCH':
            return update_comment()
        elif request.method == 'DELETE':
            return delete_comment()
