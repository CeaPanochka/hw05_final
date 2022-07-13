from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

NUMBER_OF_RECORDS = 10


# Главная страница
@cache_page(60 * 20)
def index(request):
    posts = Post.objects.order_by('-pub_date')
    page_obj = paginator_func(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


# Страница с информацией о группе
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.order_by('-pub_date')
    page_obj = paginator_func(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator_func(request, posts)
    if request.user.username != username and request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = None
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.select_related(
        'author',
    )
    form = CommentForm(
        request.POST or None,
    )
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    user = request.user
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = user
        post.save()
        return redirect('posts:profile', user.username)
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )

    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'is_edit': True,
        'form': form,
    }
    return render(request, 'posts/post_create.html', context)


def paginator_func(request, posts):
    paginator = Paginator(posts, NUMBER_OF_RECORDS)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return page_obj


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    authors = Follow.objects.filter(
        user=request.user,
    ).select_related('author')
    posts = []
    for author in authors:
        author = get_object_or_404(User, following=author)
        for post in author.posts.all():
            posts.append(post)
    page_obj = paginator_func(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    follow = Follow.objects.filter(
        user=request.user,
        author=User.objects.get(username=username),
    ).exists()
    if request.user.username == username or follow:
        return redirect('posts:profile', username=username)
    else:
        author = User.objects.get(username=username)
        Follow.objects.create(
            user=request.user,
            author=author,
        )
        return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()
    return redirect('posts:profile', username=username)
