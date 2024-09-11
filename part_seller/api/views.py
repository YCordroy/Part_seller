from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    get_object_or_404
)
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from parts.models import Category, Location, Mark, Model, Part, PartImage, User

from .filters import LocationFilter, MarkFilter, ModelFilter, PartFilter
from .pagination import TenOnPagePaginator
from .permissions import IsAuthorOrReadOnly, IsModerOnly
from .serializers import (AuthorPartSerializer, CategorySerializer,
                          LocationSerializer, MarkSerializer, ModelSerializer,
                          ModerPartSerializer, PartSerializer, UserSerializer)
from .validators import validate_image


class MarkViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для марки"""
    queryset = Mark.objects.filter(is_visible=True).order_by('id')
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = MarkSerializer
    pagination_class = TenOnPagePaginator
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    filterset_class = MarkFilter


class ModelViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели"""
    queryset = Model.objects.select_related('mark').filter(is_visible=True).order_by('id')
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = ModelSerializer
    pagination_class = TenOnPagePaginator
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    filterset_class = ModelFilter


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для локации"""
    queryset = Location.objects.filter(is_visible=True).order_by('id')
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = LocationSerializer
    pagination_class = TenOnPagePaginator
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    filterset_class = LocationFilter


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для категории"""
    queryset = Category.objects.filter(is_visible=True).order_by('id')
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = TenOnPagePaginator
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    serializer_class = CategorySerializer


class PartViewSet(viewsets.ModelViewSet):
    """Вьюсет для запчасти"""
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = TenOnPagePaginator
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    filterset_class = PartFilter

    def perform_create(self, serializer):
        author = self.request.user
        self.check_count_of_parts()
        part = serializer.save(author=author)
        if images := self.request.FILES.getlist('images'):
            for image in images[:settings.COUNT_OF_IMAGES]:
                validate_image(image)
                PartImage.objects.create(part=part, image=image)

    def perform_destroy(self, instance):
        # Не удаляем что бы не блокировать бд
        instance.is_visible = False
        instance.save()
        return Response({'detail': 'Запись удалена'}, status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        self.check_count_of_parts()
        # Каждая запчасть при редактировании должна проходить модерацию
        serializer.save(
            is_approved=False,
            moder_checked=False
        )

    def get_serializer_class(self):
        try:
            part = Part.objects.get(pk=self.kwargs.get('pk'))
        except Part.DoesNotExist:
            part = None
        if part and self.request.user == part.author:
            return AuthorPartSerializer
        return PartSerializer

    def get_queryset(self):
        """Получение кверисета в зависимости от разрешений"""

        # Что бы можно было удалять все посты, даже не прошедшие модерацию
        if self.request.method in ('DELETE', 'PATCH', 'PUT'):
            return Part.objects.filter(
                pk=self.kwargs['pk'],
                is_visible=True
            )
        # Не опубликованый пост видит только автор
        if pk := self.kwargs.get('pk'):
            part = Part.objects.filter(pk=pk, is_visible=True)
            if part.first().author == self.request.user:
                return part
            return part.filter(is_approved=True)

        return Part.objects.filter(
            sold=False,
            is_visible=True,
            is_approved=True
        ).order_by('id')

    def check_count_of_parts(self):
        """Проверка колличествa постов у автора."""
        author = self.request.user
        post_count = author.user_parts.filter(is_visible=True, sold=False).count()
        if post_count >= settings.COUNT_OF_POSTS:
            raise ValidationError(
                F"Вы не можете создать более {settings.COUNT_OF_POSTS} постов."
            )


class UserDetailView(RetrieveAPIView):
    """Вьюха для просмотра профиля конкретного пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserPartsListView(ListAPIView):
    """Вьюха для просмотра запчастей конкретного пользователя"""
    serializer_class = PartSerializer
    pagination_class = TenOnPagePaginator
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        try:
            part = Part.objects.filter(author=self.kwargs['pk']).first()
        except Part.DoesNotExist:
            part = None
        if part and self.request.user == part.author:
            return AuthorPartSerializer
        return PartSerializer

    def get_queryset(self):
        # Автор при входе в свой профиль видит все свои посты
        user_id = self.kwargs['pk']
        user = get_object_or_404(User, pk=user_id)
        if self.request.user == user:
            return user.user_parts.filter(is_visible=True).order_by('id')
        return user.user_parts.filter(
            is_visible=True,
            is_approved=True)


class ModeratorViewSet(viewsets.ModelViewSet):
    """Вьюсет для модератора"""
    queryset = Part.objects.filter(
        is_approved=False,
        moder_checked=False,
        is_visible=True
    )
    serializer_class = ModerPartSerializer
    pagination_class = TenOnPagePaginator
    permission_classes = (IsModerOnly,)

    def perform_destroy(self, instance):
        # Не удаляем что бы не блокировать бд
        instance.is_visible = False
        instance.save()
        return Response({'detail': 'Запись удалена'}, status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        # Автоматически проставляется проверка модератором
        serializer.save(
            moder_checked=True
        )
