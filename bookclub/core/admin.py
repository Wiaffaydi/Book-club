from django.contrib import admin
from .models import *

admin.site.register(Book)
admin.site.register(Discussion)
admin.site.register(Comment)
admin.site.register(DiscussionComment)
admin.site.register(BookView)
