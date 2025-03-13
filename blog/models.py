from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count


class PostQuerySet(models.QuerySet):
    def popular(self):
        """Сортировка по популярности (количеству лайков)"""
        return self.annotate(
            likes_count=Count('likes')
        ).order_by('-likes_count')

    def fetch_with_comments_count(self):
        """Добавляет количество комментариев к постам"""
        posts_ids = [post.id for post in self]
        posts_with_comments = Post.objects.filter(
            id__in=posts_ids
        ).annotate(
            comments_count=Count('post_comments')
        )

        # Создаем словарь {id поста: количество комментариев}
        ids_and_comments = {
            post.id: post.comments_count
            for post in posts_with_comments
        }

        # Добавляем количество комментариев к каждому посту
        for post in self:
            post.comments_count = ids_and_comments.get(post.id, 0)
        return self


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def popular(self):
        """Популярные посты"""
        return self.get_queryset().popular()

    def fetch_with_comments_count(self):
        """Посты с количеством комментариев"""
        return self.get_queryset().fetch_with_comments_count()

    def year(self, year):
        """Фильтрация постов по году публикации"""
        return self.filter(published_at__year=year)


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации', db_index=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    # Используем кастомный менеджер
    objects = PostManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'
        indexes = [
            models.Index(fields=['-published_at', 'title']),
            models.Index(fields=['slug']),
        ]


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(posts_count=Count('posts')).order_by('-posts_count')


class TagManager(models.Manager):
    def get_queryset(self):
        return TagQuerySet(self.model, using=self._db)

    def popular(self):
        return self.get_queryset().popular()


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True, db_index=True)
    slug = models.SlugField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    objects = TagManager()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='Пост, к которому написан',
        related_name='post_comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')
    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'