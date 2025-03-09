from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count


def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,  # Теперь использует select_related
        'comments_amount': post.comments_count,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],  # Использует prefetch_related
        'first_tag_title': post.tags.first().title if post.tags.exists() else None,
    }

def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }

def index(request):
    most_popular_posts = Post.objects.annotate(
        likes_count=Count('likes'),
        comments_count=Count('comment')
    ).select_related('author').prefetch_related('tags').order_by('-likes_count')[:5]

    most_fresh_posts = Post.objects.select_related('author').prefetch_related('tags').order_by('-published_at')[:5]

    popular_tags = Tag.objects.annotate(
        posts_count=Count('posts', distinct=True)
    ).order_by('-posts_count')[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.annotate(
        likes_count=Count('likes')
    ).select_related('author').prefetch_related('tags').get(slug=slug)
    most_popular_posts = Post.objects.annotate(
        likes_count=Count('likes'),
        comments_count=Count('comment')
    ).order_by('-likes_count')[:5]

    context = {
        'post': serialize_post(post),
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in
            Post.objects.annotate(likes_count=Count('likes'))
            .order_by('-likes_count')[:5]
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)
    popular_tags = Tag.objects.annotate(
        posts_count=Count('posts')
    ).order_by('-posts_count')[:5]
    related_posts = tag.posts.annotate(
        likes_count=Count('likes'),
        comments_count=Count('comment')
    ).select_related('author')[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in
            Post.objects.annotate(likes_count=Count('likes'))
            .order_by('-likes_count')[:5]
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
