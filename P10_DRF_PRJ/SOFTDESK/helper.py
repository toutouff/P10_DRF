from sys import stderr

from rest_framework.response import Response

from SOFTDESK.models import Contributors, Issue, Comments
from SOFTDESK.serializers import ContributorsSerializer, IssueSerializer, IssueCreationSerializer, CommentsSerializer


class ContributorHelper:
    # fixme : start from project instance for relation
    @staticmethod
    def get_contributor(project):
        contributor_list = project.contributors.all()
        return Response(ContributorsSerializer(instance=contributor_list, many=True).data)

    @staticmethod
    def add_contributor(project, request):
        """
        call add_contributor(project,data)
        """
        serializer = ContributorsSerializer(data=request.data)
        print(f' new contributor = {request.data["user"]}, user = {request.user.id} ,author = {project.author.id}',file=stderr)
        if int(project.author.id) == int(request.data['user']):
            return Response({"error : Can't add author as contributor"}, status=400)
        if not serializer.is_valid() :
            return Response(serializer.errors, status=400)
        for c in project.contributors.all():
            if c.user == serializer.validated_data['user'] :
                return Response(serializer.data,status=400)
        contributor = serializer.save(project=project)
        return Response(ContributorsSerializer(instance=contributor).data, status=201)



    @staticmethod
    def delete_contributor(project, contributor_pk):
        if project.contributors.filter(id=contributor_pk).exists():
            msg = ContributorsSerializer(instance=project.contributors.get(id=contributor_pk)).data
            contributor = project.contributors.get(id=contributor_pk)
            contributor.delete()
            return Response(msg, status=204)
        return Response({'status': 'contributor not found'}, status=404)


class IssueHelper:
    # fixme : start from project instance for relation
    @staticmethod
    def get_issues_list(project):
        issue_list = project.issues.all()
        return Response(IssueSerializer(instance=issue_list, many=True).data)

    @staticmethod
    def get_issue_detail(issue_pk,project):
        if project.issues.filter(id=issue_pk).exists():
            issue = project.issues.get(id= issue_pk)
            return Response(IssueSerializer(instance=issue).data)
        return Response({'status': 'issue not found'}, status=404)

    @staticmethod
    def add_issue(project, request):
        serializer = IssueCreationSerializer(data=request.data,partial=True)
        if serializer.is_valid():
            issue = serializer.save(project=project, author=request.user)
            return Response(IssueSerializer(instance=issue).data, status=201)
        return Response(serializer.errors,status=400 )

    @staticmethod
    def update_issue(request, issue_pk):
        if Issue.objects.filter(id=issue_pk).exists():
            issue = Issue.objects.get(id=issue_pk)
            serializer = IssueCreationSerializer(instance=issue, data=request.data,partial=True)
            if serializer.is_valid():
                issue = serializer.save()
                return Response(IssueSerializer(instance=issue).data, status=201)
            return Response(serializer.errors)
        return Response({'status': 'issue not found'}, status=404)

    @staticmethod
    def delete_issue(request,project, issue_pk):
        if project.issues.filter(id=issue_pk).exists():
            issue = project.issues.get(id= issue_pk)
            msg = IssueSerializer(instance=issue).data
            issue.delete()
            return Response(msg,status=204)
        else : return Response({'status': 'issue not found'},status= 404)


class CommentHelper:
    # fixme : start from project instance for relation
    @staticmethod
    def get_comments_list(project,issue_pk):
        if project.issues.filter(id=issue_pk).exists():
            issue = project.issues.get(id=issue_pk)
            comment_list = issue.comments.all()
            return Response(CommentsSerializer(instance=comment_list, many=True).data)
        return Response({'status': 'issue not found'}, status=404)

    @staticmethod
    def add_comment(issue_pk, request):
        if Issue.objects.filter(id=issue_pk).exists():
            issue = Issue.objects.get(id=issue_pk)
            serializer = CommentsSerializer(data=request.data)
            if serializer.is_valid():
                comment = serializer.save(issue=issue, author=request.user)
                return Response(CommentsSerializer(instance=comment).data, status=201)
            return Response(serializer.errors,status=400)
        return Response({'status': 'issue not found'},status=404)

    @staticmethod
    def get_comment_detail(project,issue_pk,comment_pk):
        if project.issues.filter(id=issue_pk).exists():
            issue = project.issues.get(id=issue_pk)
            if issue.comments.filter(id=comment_pk).exists():
                comment = issue.comments.get(id=comment_pk)
                return Response(CommentsSerializer(instance=comment).data)
            return Response({'status': 'comment not found'}, status=404)
        return Response({'status':'issue not found'},status=404)

    @staticmethod
    def update_comment(request,project,issue_pk, comment_pk):
        if project.issues.filter(id=issue_pk).exists():
            issue = project.issues.get(id=issue_pk)
        else: return Response({'status':'issue not found'},status=404)
        if issue.comments.filter(id=comment_pk).exists():
            comment = issue.comments.get(id=comment_pk)
            serializer = CommentsSerializer(instance=comment, data=request.data)
            if serializer.is_valid():
                comment = serializer.save()
                return Response(CommentsSerializer(instance=comment).data, status=201)
            return Response(serializer.errors,status=400)
        return Response({'status': 'comment not found'}, status=404)

    @staticmethod
    def delete_comment(request,project,issue_pk,comment_pk):
        if project.issues.filter(id=issue_pk).exists():
            issue=project.issues.get(id=issue_pk)
        else: return Response({'status':'issue not found'})
        if issue.comments.filter(id=comment_pk).exists():
            comment = issue.comments.get(id=comment_pk)
            msg = CommentsSerializer(instance=comment).data
            comment.delete()
            return Response(msg, status=204)
        return Response({'status': 'comment not found'}, status=404)
