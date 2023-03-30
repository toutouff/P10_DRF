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

    def create(self, validated_data):
        proj = validated_data.get('project')
        return proj.issue.create(**validated_data)


class IssueCreationSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'status']


class CommentsSerializer(ModelSerializer):
    class Meta:
        model = Comments
        fields = ['id', 'description']


class UserCreationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        return User.objects.create_user(username=validated_data.get('username'),
                                        password=validated_data.get('password'))


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'projects',
                  'issues', 'comments']


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
