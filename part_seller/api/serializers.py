from django.conf import settings
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from parts.models import Category, Location, Mark, Model, Part, PartImage, User

from .validators import RegexpProc, UsernameValidator


class MarkSerializer(serializers.ModelSerializer):
    """Сериалайзер для марки"""

    class Meta:
        model = Mark
        fields = ('id', 'name', 'producer_country_name')


class ModelSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели"""
    mark = MarkSerializer(read_only=True)

    class Meta:
        model = Model
        fields = ('id', 'name', 'mark')


class LocationSerializer(serializers.ModelSerializer):
    """Сериалайзер для локации"""

    class Meta:
        model = Location
        fields = ('id', 'name')


class PartImageSerializer(serializers.ModelSerializer):
    """Сериалайзер для вложенных изображений"""

    class Meta:
        model = PartImage
        fields = ('image',)


class PartSerializer(serializers.ModelSerializer):
    """Сериалайзер для запчасти"""
    model = serializers.PrimaryKeyRelatedField(queryset=Model.objects.filter(is_visible=True))
    mark = serializers.PrimaryKeyRelatedField(queryset=Mark.objects.filter(is_visible=True))
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.filter(is_visible=True))
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(is_visible=True))
    author = serializers.StringRelatedField(read_only=True)
    images = PartImageSerializer(many=True, read_only=True)

    class Meta:
        model = Part
        fields = (
            'id',
            'mark',
            'model',
            'name',
            'category',
            'json_data',
            'description',
            'images',
            'location',
            'price',
            'author',
            'contact',
            'sold',
            'uploaded_at',
        )

    def to_internal_value(self, data):
        # Преобразуем названия в объекты модели без учета регистра
        data = data.copy()
        try:
            data['model'] = Model.objects.get(name__iexact=data['model']).id
        except Model.DoesNotExist:
            raise ValidationError({'model': 'Модель не найдена.'})
        except KeyError:
            pass

        try:
            data['mark'] = Mark.objects.get(name__iexact=data['mark']).id
        except Mark.DoesNotExist:
            raise ValidationError({'mark': 'Марка не найдена.'})
        except KeyError:
            pass

        try:
            data['location'] = Location.objects.get(name__iexact=data['location']).id
        except Location.DoesNotExist:
            raise ValidationError({'location': 'Местоположение не найдено.'})
        except KeyError:
            pass

        try:
            data['category'] = Category.objects.get(name__iexact=data['category']).id
        except Category.DoesNotExist:
            raise ValidationError({'category': 'Категория не найдена.'})
        except KeyError:
            pass

        return super().to_internal_value(data)

    def to_representation(self, instance):
        # Правильное отображение информации при GET запросе
        representation = super().to_representation(instance)
        representation['model'] = str(instance.model)
        representation['mark'] = MarkSerializer(instance.mark).data
        representation['location'] = str(instance.location)
        representation['category'] = str(instance.category)
        return representation

    def validate_name(self, value):
        if RegexpProc.test(value):
            raise serializers.ValidationError('Не корректные данные')
        return value

    def validate_description(self, value):
        if RegexpProc.test(value):
            raise serializers.ValidationError('Не корректные данные')
        return value

    def validate_json_data(self, value):
        for param, val in value.items():
            if RegexpProc.test(val):
                raise serializers.ValidationError(
                    f'{param}: Не корректные данные'
                )
        return value

    def validate_contact(self, value):
        if settings.PATTERN_CONTACT_PART.match(value):
            return value
        raise serializers.ValidationError(
            'Контакт может быть указан в форматах: '
            'telegram: @abc; '
            'whatsapp: +71231234567; '
            'telegram/whatsapp: +71231234567; '
            '+71231234567 '
            '(+ и : не обязательны)'
        )


class AuthorPartSerializer(PartSerializer):
    """Сериалайзер для запчасти при просмотре автором"""
    is_approved = serializers.BooleanField(read_only=True)
    moder_comment = serializers.StringRelatedField(read_only=True)
    moder_checked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Part
        fields = (
            'id',
            'mark',
            'model',
            'category',
            'name',
            'json_data',
            'description',
            'location',
            'price',
            'author',
            'contact',
            'sold',
            'is_approved',
            'uploaded_at',
            'moder_checked',
            'moder_comment'
        )


class ModerPartSerializer(AuthorPartSerializer):
    """Сериалайзер для запчасти при просмотре модератором"""
    is_approved = serializers.BooleanField()
    moder_comment = serializers.CharField(allow_blank=True)
    moder_checked = serializers.BooleanField()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериалайзер для создания пользователя"""
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.filter(is_visible=True)
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'location',
            'contact'
        )

    def to_internal_value(self, data):
        data = data.copy()
        try:
            data['location'] = Location.objects.get(name__iexact=data['location']).id
        except Location.DoesNotExist:
            raise ValidationError({'location': 'Местоположение не найдено.'})
        except KeyError:
            pass

        return super().to_internal_value(data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['location'] = str(instance.location)
        return representation

    def validate_contact(self, value):
        if settings.PATTERN_CONTACT_USER.match(value):
            return value
        raise serializers.ValidationError(
            'Контакт должен быть указан в формате: +71231234567'
        )

    def validate_username(self, value):
        UsernameValidator().validate_reserved(value)
        UsernameValidator().validate_confusables(value)
        return value

    def validate_email(self, value):
        UsernameValidator().validate_confusables_email(value)
        return value


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер детализации пользователя"""
    location = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ('id', 'username', 'location', 'contact')


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для категории"""

    class Meta:
        model = Category
        fields = ('id', 'name')
