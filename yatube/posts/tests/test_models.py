from django.test import TestCase
from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        TITLE_LENGTH = 15
        expecter_object_post_name = post.text[:TITLE_LENGTH]
        self.assertEqual(expecter_object_post_name, str(post))

        group = PostModelTest.group
        expecter_object_group_name = group.title
        self.assertEqual(expecter_object_group_name, str(group))
