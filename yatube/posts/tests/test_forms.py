import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_post_create(self):
        '''Валидная форма создаёт запись в Post'''
        post_count = Post.objects.count()
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
        form_data = {
            'author': PostFormTests.user,
            'text': 'Тестовый пост 2',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        expected_name = PostFormTests.user
        expected_text = 'Тестовый пост 2'
        expected_image = 'posts/small.gif'
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': PostFormTests.user})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=expected_name,
                text=expected_text,
                image=expected_image,
            ).exists()
        )

    def test_edit_post(self):
        '''Валидная форма изменяет запись в Post'''
        post_id = PostFormTests.post.id
        post_count = Post.objects.count()
        form_data = {
            'author': PostFormTests.user,
            'text': 'Изменённый тестовый пост 1',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True,
        )
        last_obj = Post.objects.all().last()
        expected_name = PostFormTests.user
        expected_text = 'Изменённый тестовый пост 1'
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(last_obj.author, expected_name)
        self.assertEqual(last_obj.text, expected_text)

    def test_comment_post(self):
        '''Валидная форма добавляет комментарий'''
        post_id = PostFormTests.post.id
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True,
        )
        last_obj = Comment.objects.all().last()
        expected_author = 'Loly'
        expected_text = 'Тестовый комментарий'
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(last_obj.author.username, expected_author)
        self.assertEqual(last_obj.text, expected_text)
