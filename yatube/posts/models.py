from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    class Meta:
        verbose_name = 'Группа'

    title = models.CharField(
        'Название',
        max_length=200,
    )
    slug = models.SlugField(
        'Адрес для страницы с группой',
        unique=True,
    )
    description = models.TextField(
        verbose_name='Описание',
    )

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        TITLE_LENGTH = 15
        return self.text[:TITLE_LENGTH]


class Comment(models.Model):
    class Meta:
        verbose_name = 'Комментарий'

    post = models.ForeignKey(
        Post,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        'Текст комментария',
    )
    created = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True,
    )


class Follow(models.Model):
    class Meta:
        verbose_name = 'Подписка'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
