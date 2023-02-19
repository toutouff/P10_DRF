from django.contrib import admin

# Register your models here.
from .models import Project, Issue, Comments, Contributors, User

admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Comments)
admin.site.register(Contributors)
admin.site.register(User)
