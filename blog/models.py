from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch


class TagQuerySet(models.QuerySet):
    def with_posts_count(self):
        """Аннотация количества постов для тегов"""
        return self.annotate(posts_count=Count('posts'))

    def popular(self):
        """Сортировка тегов по популярности"""
        return self.with_posts_count().order_by('-posts_count')


class PostQuerySet(models.QuerySet):
    def popular(self):
        """Сортировка постов по количеству лайков"""
        return self.annotate(likes_count=Count('likes')).order_by('-likes_count')

    def with_comments_count(self):
        """Аннотация количества комментариев"""
        return self.annotate(comments_count=Count('post_comments'))

    def with_prefetched_tags(self):
        """Префетч тегов с аннотацией количества постов"""
        return self.prefetch_related(
            Prefetch('tags', queryset=Tag.objects.with_posts_count())
        )


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    objects = TagQuerySet.as_manager()


class Post(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='posts/')
    published_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_posts')
    tags = models.ManyToManyField(Tag, related_name='posts')

    objects = PostQuerySet.as_manager()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)

