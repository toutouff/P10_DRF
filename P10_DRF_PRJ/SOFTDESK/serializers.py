from rest_framework.serializers import ModelSerializer

from .models import Project, Issue, Comments, Contributors, User


# TODO: add issue and comment to detail of serializer that need it
class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description']


class ContributorsSerializer(ModelSerializer):
    """user = SerializerMethodField()

    def get_user(self, obj):
        queryset = User.objects.filter(contributors=obj)
        return UserSerializer(queryset, many=True).data"""

    class Meta:
        model = Contributors
        fields = ['id', 'permission', 'role', 'user']


class ProjectDetailSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'author',
                  'contributors']


class IssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'


class IssueCreationSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'status', 'assigned_to']


class CommentsSerializer(ModelSerializer):
    class Meta:
        model = Comments
        fields = ['id', 'description']


class UserCreationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'projects',
                  'issues', 'comments']


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
