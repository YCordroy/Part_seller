from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers

from .views import (CategoryViewSet, LocationViewSet, MarkViewSet,
                    ModelViewSet, ModeratorViewSet, PartViewSet,
                    UserDetailView, UserPartsListView, FavoriteViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register(r'mark', MarkViewSet)
router_v1.register(r'model', ModelViewSet)
router_v1.register(r'location', LocationViewSet)
router_v1.register(r'part', PartViewSet, basename='part')
router_v1.register(r'category', CategoryViewSet)
router_v1.register(r'moderation', ModeratorViewSet, basename='moderation')
router_v1.register(r'favorites', FavoriteViewSet, basename='favorites')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('v1/user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path(
        'v1/user/<int:pk>/parts/',
        UserPartsListView.as_view(),
        name='user-parts'
    ),
    path('docs/', TemplateView.as_view(template_name='swagger_ui.html'), name='swagger-ui')
]
