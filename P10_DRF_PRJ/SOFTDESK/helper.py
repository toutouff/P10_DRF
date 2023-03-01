from rest_framework.response import Response

from SOFTDESK.models import Contributors, Issue, Comments
from SOFTDESK.serializers import ContributorsSerializer, IssueSerializer, IssueCreationSerializer, CommentsSerializer


class ContributorHelper:
    @staticmethod
    def get_contributor(project):
        contributor_list = Contributors.objects.filter(project=project)
        return Response(ContributorsSerializer(instance=contributor_list, many=True).data)

    @staticmethod
    def add_contributor(project, request):
        """
        call add_contributor(project,data)
        """
        serializer = ContributorsSerializer(data=request.data)
        if serializer.is_valid():
            contributor = serializer.save(project=project)
            return Response(ContributorsSerializer(instance=contributor).data, status=201)
        return Response(serializer.errors)

    @staticmethod
    def delete_contributor(request, contributor_pk):
        if Contributors.objects.filter(id=contributor_pk).exists():
            msg = ContributorsSerializer(instance=Contributors.objects.get(id=contributor_pk)).data
            contributor = Contributors.objects.get(id=contributor_pk)
            contributor.delete()
            return Response(msg, status=204)
        return Response({'status': 'contributor not found'}, status=404)


class IssueHelper:
    @staticmethod
    def get_issues_list(project):
        issue_list = Issue.objects.filter(project=project)
        return Response(IssueSerializer(instance=issue_list, many=True).data)

    @staticmethod
    def get_issue_detail(issue_pk):
        if Issue.objects.filter(id=issue_pk).exists():
            issue = Issue.objects.get(id=issue_pk)
            return Response(IssueSerializer(instance=issue).data)
        return Response({'status': 'issue not found'}, status=404)

    @staticmethod
    def add_issue(project, request):
        serializer = IssueCreationSerializer(data=request.data)
        if serializer.is_valid():
            issue = serializer.save(project=project, author=request.user)
            return Response(IssueSerializer(instance=issue).data, status=201)
        return Response(serializer.errors)

    @staticmethod
    def update_issue(request, issue_pk):
        if Issue.objects.filter(id=issue_pk).exists():
            issue = Issue.objects.get(id=issue_pk)
            serializer = IssueCreationSerializer(instance=issue, data=request.data)
            if serializer.is_valid():
                issue = serializer.save()
                return Response(IssueSerializer(instance=issue).data, status=201)
            return Response(serializer.errors)
        return Response({'status': 'issue not found'}, status=404)

    @staticmethod
    def delete_issue(request, issue_pk):
        if Issue.objects.filter(id=issue_pk).exists():
            issue = Issue.objects.get(id=issue_pk)
            issue.delete()
            return Response(status=204)
        return Response({'status': 'issue not found'}, status=404)


class CommentHelper:
    @staticmethod
    def get_comments_list(issue_pk):
        if Issue.objects.filter(id=issue_pk).exists():
            issue = Issue.objects.get(id=issue_pk)
            comment_list = Comments.objects.filter(issue=issue)
            return Response(CommentsSerializer(instance=comment_list, many=True).data)
        return Response({'status': 'issue not found'}, status=404)

    @staticmethod
    def get_comment_detail(comment_pk):
        if Comments.objects.filter(id=comment_pk).exists():
            comment = Comments.objects.get(id=comment_pk)
            return Response(CommentsSerializer(instance=comment).data)
        return Response({'status': 'comment not found'}, status=404)

    @staticmethod
    def add_comment(issue_pk, request):
        if Issue.objects.filter(id=issue_pk).exists():
            issue = Issue.objects.get(id=issue_pk)
            serializer = CommentsSerializer(data=request.data)
            if serializer.is_valid():
                comment = serializer.save(issue=issue, author=request.user)
                return Response(CommentsSerializer(instance=comment).data, status=201)
            return Response(serializer.errors)
        return Response({'status': 'issue not found'})

    @staticmethod
    def update_comment(request, comment_pk):
        if Comments.objects.filter(id=comment_pk).exists():
            comment = Comments.objects.get(id=comment_pk)
            serializer = CommentsSerializer(instance=comment, data=request.data)
            if serializer.is_valid():
                comment = serializer.save()
                return Response(CommentsSerializer(instance=comment).data, status=201)
            return Response(serializer.errors)
        return Response({'status': 'comment not found'}, status=404)

    @staticmethod
    def delete_comment(request, comment_pk):
        if Comments.objects.filter(id=comment_pk).exists():
            comment = Comments.objects.get(id=comment_pk)
            msg = CommentsSerializer(instance=comment).data
            comment.delete()
            return Response(msg, status=204)
        return Response({'status': 'comment not found'}, status=404)
