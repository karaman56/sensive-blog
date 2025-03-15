from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch


class PostQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(
            likes_count=Count('likes')
        ).order_by('-likes_count')

    def fetch_with_comments_count(self):
        return self.annotate(
            comments_count=Count('post_comments')
        )


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def popular(self):
        return self.get_queryset().popular()

    def fetch_with_comments_count(self):
        return self.get_queryset().fetch_with_comments_count()


class Post(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='posts/')
    published_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_posts')
    tags = models.ManyToManyField('Tag', related_name='posts')

    objects = PostManager()


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(posts_count=Count('posts')).order_by('-posts_count')


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    objects = TagQuerySet.as_manager()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)