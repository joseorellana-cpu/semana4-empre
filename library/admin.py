from django.contrib import admin

from .models import (
    Author,
    AuthorProfile,
    Book,
    Category,
    Publication,
    Publisher,
)


class AuthorProfileInline(admin.StackedInline):
    model = AuthorProfile
    can_delete = False
    verbose_name_plural = 'Profile'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    list_display_links = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name', 'email')
    inlines = [AuthorProfileInline]


@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ('author', 'website')
    search_fields = ('author__first_name', 'author__last_name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'website')
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'author')
    list_display_links = ('title',)
    search_fields = (
        'title',
        'isbn',
        'author__first_name',
        'author__last_name',
    )
    filter_horizontal = ('categories',)


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('book', 'publisher', 'edition', 'publication_date')
    list_filter = ('publisher', 'publication_date')
    search_fields = ('book__title', 'publisher__name')
