from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Prefetch
from django.views.decorators.cache import cache_page
from blog.models import Post, Tag

def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': getattr(tag, 'posts_count', tag.posts.count()),
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

@cache_page(60 * 15)
def index(request):
    most_popular_posts = Post.objects.popular() \
        .prefetch_related(
            Prefetch(
                'tags',
                queryset=Tag.objects.annotate(posts_count=Count('posts'))
            )
        ).fetch_with_comments_count()[:5]

    popular_tags = Tag.objects.annotate(posts_count=Count('posts')).order_by('-posts_count')[:5]

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
        ).prefetch_related(
            Prefetch('tags', queryset=Tag.objects.annotate(posts_count=Count('posts')))
        ).select_related('author'),
        slug=slug
    )

    popular_tags = Tag.objects.annotate(posts_count=Count('posts')).order_by('-posts_count')[:5]
    most_popular_posts = Post.objects.popular()[:5].fetch_with_comments_count()

    context = {
        'post': serialize_post_optimized(post),
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)

def tag_filter(request, tag_slug):
    tag = get_object_or_404(
        Tag.objects.annotate(posts_count=Count('posts')),
        slug=tag_slug
    )

    related_posts = tag.posts.annotate(
        likes_count=Count('likes'),
        comments_count=Count('post_comments')
    ).select_related('author').prefetch_related(
        Prefetch('tags', queryset=Tag.objects.annotate(posts_count=Count('posts')))
    )[:20]

    popular_tags = Tag.objects.annotate(posts_count=Count('posts')).order_by('-posts_count')[:5]
    most_popular_posts = Post.objects.popular()[:5].fetch_with_comments_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        'posts': [serialize_post_optimized(post) for post in related_posts],
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)

def contacts(request):
    return render(request, 'contacts.html', {})