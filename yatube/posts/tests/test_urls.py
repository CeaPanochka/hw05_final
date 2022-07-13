from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


STATUS_OK = HTTPStatus.OK.value


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.second_user = User.objects.create_user(username='second_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.second_post = Post.objects.create(
            author=cls.second_user,
            text='Второй тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        cache.clear()

    def test_home_url_exists_at_desired_location(self):
        response = self.guest_client.get(reverse('posts:main'))
        self.assertEqual(response.status_code, STATUS_OK)

    def test_group_detail_url_exists_at_desired_location(self):
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(response.status_code, STATUS_OK)

    def test_profile_url_exists_at_desired_location(self):
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(response.status_code, STATUS_OK)

    def test_post_detail_url_exists_at_desired_location(self):
        post_id = PostURLTests.post.id
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )
        self.assertEqual(response.status_code, STATUS_OK)

    def test_post_create_edit_url_exists_at_desired_location_authorized(self):
        post_id = PostURLTests.post.id
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id})
        )
        self.assertEqual(response.status_code, STATUS_OK)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, STATUS_OK)

    def test_post_create_edit_url_redirect_noauthor_on_post_detail(self):
        post_id = PostURLTests.second_post.id
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            follow=True,
        )
        self.assertRedirects(response, f'/posts/{post_id}/')

    def test_post_create_url_redirect_anonymous_on_login(self):
        post_id = PostURLTests.post.id
        response = self.guest_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            follow=True,
        )
        LOGIN = 'users:login'
        CREATE = 'posts:post_edit'
        self.assertRedirects(
            response,
            reverse(LOGIN) + "?next=" + reverse(
                CREATE, kwargs={'post_id': post_id}
            )
        )

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        NOT_FOUND = HTTPStatus.NOT_FOUND.value
        self.assertEqual(response.status_code, NOT_FOUND)

    def test_urls_uses_correct_template(self):
        '''Url-адрес использует соответствующий шаблон'''
        post_id = PostURLTests.post.id
        templates_url_names = {
            reverse('posts:main'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': post_id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': post_id}):
            'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
