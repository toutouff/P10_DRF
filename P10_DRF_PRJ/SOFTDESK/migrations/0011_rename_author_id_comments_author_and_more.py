# Generated by Django 4.1.5 on 2023-02-06 15:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SOFTDESK', '0010_rename_issue_comments_issue_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comments',
            old_name='author_id',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='comments',
            old_name='issue_id',
            new_name='issue',
        ),
        migrations.RenameField(
            model_name='contributors',
            old_name='project_id',
            new_name='project',
        ),
        migrations.RenameField(
            model_name='contributors',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='issue',
            old_name='assigned_to_id',
            new_name='assigned_to',
        ),
        migrations.RenameField(
            model_name='issue',
            old_name='author_id',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='issue',
            old_name='project_id',
            new_name='project',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='author_id',
            new_name='author',
        ),
    ]
