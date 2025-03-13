from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.first().title if post.tags.exists() else None,
    }


def serialize_post_optimized(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.first().title if post.tags.exists() else None,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count if hasattr(tag, 'posts_count') else 0,
    }


@cache_page(60 * 15)
def index(request):
    most_popular_posts = Post.objects.annotate(  # Добавляем аннотации
        likes_count=Count('likes'),
        comments_count=Count('post_comments')
    ).prefetch_related(
        Prefetch('tags', queryset=Tag.objects.annotate(posts_count=Count('posts')))
    ).filter(tags__isnull=False).distinct()[:5]

    popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.annotate(
            likes_count=Count('likes'),
            comments_count=Count('post_comments')
        )
        .prefetch_related(
            Prefetch('tags', queryset=Tag.objects.annotate(posts_count=Count('posts')))
        ),
        slug=slug
    )

    popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = Post.objects.annotate(
        likes_count=Count('likes'),
        comments_count=Count('post_comments')
    ).order_by('-likes_count')[:5]

    context = {
        'post': serialize_post(post),
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_slug):
    tag = get_object_or_404(
        Tag.objects.annotate(posts_count=Count('posts')),
        slug=tag_slug
    )

    related_posts = tag.posts.annotate(  # Добавляем аннотации
        likes_count=Count('likes'),
        comments_count=Count('post_comments')
    ).select_related('author')[:20]

    popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = Post.objects.annotate(
        likes_count=Count('likes'),
        comments_count=Count('post_comments')
    ).order_by('-likes_count')[:5]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})