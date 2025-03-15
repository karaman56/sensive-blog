from django.contrib import admin
from blog.models import Post, Tag, Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'published_at']
    list_select_related = ['author', 'post']
    raw_id_fields = ['author', 'post']
    search_fields = ['text']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_at']
    raw_id_fields = ['author', 'tags']
    list_filter = ['published_at']
    search_fields = ['title', 'text']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    search_fields = ['title']
