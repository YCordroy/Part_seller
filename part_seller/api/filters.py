import json

import django_filters
from django.db.models import Q

from parts.models import Location, Mark, Model, Part


class ModelFilter(django_filters.FilterSet):
    """Фильтр для модели"""
    mark = django_filters.CharFilter(
        field_name='mark__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Model
        fields = ('mark',)


class MarkFilter(django_filters.FilterSet):
    """Фильтр для марки"""
    country = django_filters.CharFilter(
        field_name='producer_country_name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Mark
        fields = ('country',)


class LocationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Location
        fields = ('name',)


class PartFilter(django_filters.FilterSet):
    """Фильтр для запчасти"""
    model_name = django_filters.CharFilter(
        field_name='model__name',
        lookup_expr='icontains'
    )
    mark_name = django_filters.CharFilter(
        field_name='mark__name',
        lookup_expr='icontains'
    )
    part_name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    price_gte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte'
    )
    price_lte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte'
    )
    mark_list = django_filters.CharFilter(method='mark_list_filter')
    location = django_filters.CharFilter(
        field_name='location__name',
        lookup_expr='icontains'
    )
    category = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains'
    )
    color = django_filters.CharFilter(method='filter_by_color')
    is_new_part = django_filters.BooleanFilter(method='filter_by_is_new_part')

    class Meta:
        model = Part
        fields = [
            'model_name',
            'mark_name',
            'part_name',
            'price_gte',
            'price_lte',
            'mark_list',
            'location',
            'color',
            'category',
            'is_new_part'
        ]

    # Обработка фильтра mark_list
    def mark_list_filter(queryset, name, value):
        mark_list = json.loads(value)
        return queryset.filter(Q(mark__id__in=mark_list))

    def filter_by_color(self, queryset, name, value):
        return queryset.filter(json_data__color__icontains=value)

    def filter_by_is_new_part(self, queryset, name, value):
        return queryset.filter(json_data__is_new_part=value)
