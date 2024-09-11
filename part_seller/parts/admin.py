from django.contrib import admin

from .models import Location, Mark, Model, Part, PartImage, User


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'producer_country_name',
        'is_visible',
    )

    list_editable = (
        'is_visible',
    )


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'mark',
        'is_visible',
    )

    list_editable = (
        'is_visible',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_visible',
    )

    list_editable = (
        'is_visible',
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        'username',
        'email',
        'is_staff',
        'location',
        'contact'
    )


class PhotoInline(admin.TabularInline):
    model = PartImage
    extra = 1
    fields = ('image_tag', 'image')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return 'image_tag', 'image'
        return super().get_readonly_fields(request, obj)


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'mark',
        'model',
        'is_visible',
        'author',
        'is_approved',
        'contact'
    )

    list_editable = (
        'is_approved',
        'is_visible',
    )

    inlines = [PhotoInline]
