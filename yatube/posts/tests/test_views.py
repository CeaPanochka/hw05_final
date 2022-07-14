from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post, User

FIRST_COUNT_PAGE_OBJ = 10
SECOND_COUNT_PAGE_OBJ = 3


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        cls.user = User.objects.create_user(username='Loly')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
            image=uploaded,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        cache.clear()

    def test_group_post_detail_context(self):
        post_id = PostPagesTests.post.id
        templates_pages_names = {
            (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ): ['group', 'page_obj'],
            (
                reverse('posts:post_detail', kwargs={'post_id': post_id})
            ): 'post',
        }
        for reverse_name, obj in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                if len(obj) > 2:
                    self.assertEqual(
                        first=response.context.get(obj).author.username,
                        second='Loly'
                    )
                    self.assertEqual(
                        first=response.context.get(obj).text,
                        second='Тестовый пост'
                    )
                    self.assertTrue(
                        response.context.get(obj).image, 'posts/small.gif'
                    )
                else:
                    self.assertEqual(
                        first=response.context.get(obj[0]).title,
                        second='Тестовая группа'
                    )
                    self.assertEqual(
                        first=response.context.get(obj[0]).slug,
                        second='test-slug'
                    )
                    self.assertEqual(
                        first=response.context.get(obj[0]).description,
                        second='Тестовое описание'
                    )
                    self.assertEqual(
                        first=response.context.get(obj[1])[0].author.username,
                        second='Loly'
                    )
                    self.assertEqual(
                        first=response.context.get(obj[1])[0].text,
                        second='Тестовый пост'
                    )
                    self.assertTrue(
                        response.context.get(obj[1])[0].image,
                        'posts/small.gif'
                    )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = PostPagesTests.post.id
        templates_pages_names = {
            reverse('posts:main'): 'posts/index.html',
            (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ): 'posts/group_list.html',
            (
                reverse('posts:profile', kwargs={'username': 'Loly'})
            ): 'posts/profile.html',
            (
                reverse('posts:post_detail', kwargs={'post_id': post_id})
            ): 'posts/post_detail.html',
            (
                reverse('posts:post_edit', kwargs={'post_id': post_id})
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_show_correct_context(self):
        """Шаблон main сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:main'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, 'Loly')
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertTrue(post_image_0)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(reverse(
                'posts:profile', kwargs={'username': 'Loly'}
            ))
        )
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, 'Loly')
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertTrue(post_image_0)

    def test_post_create_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        post_id = PostPagesTests.post.id
        response = (
            self.authorized_client.get(reverse(
                'posts:post_edit', kwargs={'post_id': post_id}
            ))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache(self):
        new_post = Post.objects.create(
            author=PostPagesTests.user,
            text='Текст, кешируемого поста',
        )
        response = (
            self.authorized_client.get(reverse('posts:main'))
        )
        self.assertEqual(new_post.text, response.context['page_obj'][0].text)
        response_content = response.content
        new_post.delete()
        response_cached_content = (
            self.authorized_client.get(reverse('posts:main')).content
        )
        cache.clear()
        response_deleted_content = (
            self.authorized_client.get(reverse('posts:main')).content
        )
        self.assertEqual(response_content, response_cached_content)
        self.assertNotEqual(response_cached_content, response_deleted_content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Pan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f'Тестовый пост {i+1}',
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)
        cache.clear()

    def test_first_main_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:main'))
        self.assertEqual(
            len(response.context['page_obj']), FIRST_COUNT_PAGE_OBJ
        )

    def test_second_main_page_contains_three_records(self):
        response = self.client.get(reverse('posts:main'))
        self.assertEqual(
            len(response.context['page_obj'].paginator.page(2)),
            SECOND_COUNT_PAGE_OBJ
        )

    def test_first_group_list_page_contains_ten_records(self):
        response = (
            self.authorized_client.get(reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ))
        )
        self.assertEqual(
            len(response.context['page_obj']), FIRST_COUNT_PAGE_OBJ
        )

    def test_second_group_list_page_contains_three_records(self):
        response = (
            self.authorized_client.get(reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ) + '?page=2')
        )
        self.assertEqual(
            len(response.context['page_obj']), SECOND_COUNT_PAGE_OBJ
        )

    def test_first_profile_page_contains_ten_records(self):
        response = (
            self.authorized_client.get(reverse(
                'posts:profile', kwargs={'username': 'Pan'}
            ))
        )
        self.assertEqual(
            len(response.context['page_obj']), FIRST_COUNT_PAGE_OBJ
        )

    def test_second_profile_page_contains_three_records(self):
        response = (
            self.authorized_client.get(reverse(
                'posts:profile', kwargs={'username': 'Pan'}
            ) + '?page=2')
        )
        self.assertEqual(
            len(response.context['page_obj']), SECOND_COUNT_PAGE_OBJ
        )


class FollowViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Loly')
        cls.follower = User.objects.create_user(username='Follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowViewTests.follower)
        cache.clear()

    def test_follow(self):
        self.assertFalse(Follow.objects.filter(
            user=FollowViewTests.follower,
            author=FollowViewTests.author,
        ).exists())
        response_follow = (
            self.authorized_client.get(reverse(
                'posts:profile_follow',
                kwargs={'username': FollowViewTests.author}
            ))
        )
        self.assertTrue(Follow.objects.filter(
            user=FollowViewTests.follower,
            author=FollowViewTests.author,
        ).exists())
        self.assertRedirects(response_follow, reverse('posts:profile', kwargs={
            'username': FollowViewTests.author
        }))
        response_follow_index = (
            self.authorized_client.get(reverse(
                'posts:follow_index',
            ))
        )
        first_object = response_follow_index.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, 'Loly')
        self.assertEqual(post_text_0, 'Тестовый пост')

        response_unfollow = (
            self.authorized_client.get(reverse(
                'posts:profile_unfollow',
                kwargs={'username': FollowViewTests.author}
            ))
        )
        self.assertFalse(Follow.objects.filter(
            user=FollowViewTests.follower,
            author=FollowViewTests.author,
        ).exists())
        self.assertRedirects(response_unfollow, reverse(
            'posts:profile', kwargs={
                'username': FollowViewTests.author
            }))
