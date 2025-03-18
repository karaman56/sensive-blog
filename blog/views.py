from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from blog.models import Post, Tag

def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }

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


def get_popular_tags():
    cache_key = 'popular_tags_serialized'
    serialized_tags = cache.get(cache_key)

    if not serialized_tags:
        tags = Tag.objects.popular()[:5]
        serialized_tags = [serialize_tag(tag) for tag in tags]
        cache.set(cache_key, serialized_tags, 60 * 15)

    return serialized_tags


def get_most_popular_posts():
    cache_key = 'most_popular_posts_serialized'
    serialized_posts = cache.get(cache_key)

    if not serialized_posts:
        posts = Post.objects.popular() \
                    .with_comments_count() \
                    .with_prefetched_tags() \
                    .select_related('author')[:5]

        serialized_posts = [serialize_post(post) for post in posts]
        cache.set(cache_key, serialized_posts, 60 * 15)

    return serialized_posts


@cache_page(60 * 15)
def index(request):
    context = {
        'most_popular_posts': get_most_popular_posts(),
        'popular_tags': get_popular_tags(),
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects
        .with_comments_count()
        .with_prefetched_tags()
        .select_related('author'),
        slug=slug
    )

    context = {
        'post': serialize_post(post),
        'popular_tags': get_popular_tags(),
        'most_popular_posts': get_most_popular_posts(),
    }
    return render(request, 'post-details.html', context)

def tag_filter(request, tag_slug):
    tag = get_object_or_404(Tag.objects.popular(), slug=tag_slug)

    related_posts = Post.objects.filter(tags=tag) \
        .with_comments_count() \
        .with_prefetched_tags() \
        .select_related('author') \
        .distinct()[:20]

    context = {
        'tag': tag.title,
        'popular_tags': get_popular_tags(),
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': get_most_popular_posts(),
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})

