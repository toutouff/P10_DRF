# Generated by Django 4.1.5 on 2023-01-25 15:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SOFTDESK', '0003_alter_project_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributors',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='SOFTDESK.project'),
        ),
    ]
