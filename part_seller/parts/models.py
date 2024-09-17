from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.html import format_html


class VisibleModel(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=100,
        db_index=True
    )
    is_visible = models.BooleanField(
        verbose_name='В зоне видимости',
        default=True,
        help_text='Снимите галочку, что бы убрать из поиска'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def mark_name(self):
        return self.mark.name

    def model_name(self):
        return self.model.name

    mark_name.short_description = 'Марка'
    model_name.short_description = 'Модель'


class Mark(VisibleModel):
    producer_country_name = models.CharField(
        verbose_name='Страна производитель',
        max_length=25
    )

    class Meta:
        verbose_name = 'марка'
        verbose_name_plural = 'Марки'
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='unique_mark'
            )
        ]


class Model(VisibleModel):
    mark = models.ForeignKey(
        Mark,
        verbose_name='Марка',
        related_name='mark',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'модель'
        verbose_name_plural = 'Модели'
        constraints = [
            models.UniqueConstraint(
                fields=['mark_id', 'name'],
                name='unique_model_mark'
            )
        ]


class Part(VisibleModel):
    description = models.TextField(
        verbose_name='Описание',
        validators=[
            MaxLengthValidator(
                250,
                'Максимальное число символов 250'
            )
        ]
    )
    location = models.ForeignKey(
        'Location',
        verbose_name='Местоположение',
        related_name='location_parts',
        on_delete=models.SET('-')
    )
    mark = models.ForeignKey(
        Mark,
        verbose_name='Марка',
        related_name='mark_parts',
        on_delete=models.CASCADE,
    )
    model = models.ForeignKey(
        Model,
        verbose_name='Модель',
        related_name='model_parts',
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        verbose_name='Цена',
        max_digits=10,
        decimal_places=2
    )
    json_data = models.JSONField()
    contact = models.CharField(
        verbose_name='Контакт',
        max_length=25,
        db_index=True
    )
    is_approved = models.BooleanField(
        verbose_name='Прошло модерацию',
        default=False,
    )
    author = models.ForeignKey(
        'User',
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='user_parts'
    )
    sold = models.BooleanField(
        verbose_name='Продано',
        default=False
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    moder_checked = models.BooleanField(
        verbose_name='Проверено модератором',
        default=False,
    )
    moder_comment = models.TextField(
        verbose_name='Комментарий модератора',
        blank=True,
        validators=[
            MaxLengthValidator(
                250,
                'Максимальное число символов 250'
            )
        ]
    )
    category = models.ForeignKey(
        'Category',
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='category_parts'

    )

    class Meta:
        verbose_name = 'запчасть'
        verbose_name_plural = 'Запчасти'


class Location(VisibleModel):
    class Meta:
        verbose_name = 'локация'
        verbose_name_plural = 'Локации'
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='unique_location'
            )
        ]


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Эмейл',
        max_length=50,
        unique=True,
    )
    location = models.ForeignKey(
        'Location',
        verbose_name='Местоположение',
        on_delete=models.SET_NULL,
        null=True,
    )
    contact = models.CharField(
        verbose_name='Контакт',
        max_length=25,
    )

    is_admin = models.BooleanField(
        verbose_name='Администратор',
        default=False,
    )
    is_moder = models.BooleanField(
        verbose_name='Модератор',
        default=False,
    )

    def __str__(self):
        return self.username


class PartImage(models.Model):
    part = models.ForeignKey('Part', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=f'part_images/{date.today()}'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def image_tag(self):
        if self.image:
            return format_html(
                '<img src="{}" width="100" height="100" />',
                self.image.url
            )
        return "No Image"

    image_tag.short_description = 'Image'

    class Meta:
        verbose_name = 'Фотография запчасти'
        verbose_name_plural = 'Фотографии запчастей'


class Category(VisibleModel):
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='unique_category'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'part')
