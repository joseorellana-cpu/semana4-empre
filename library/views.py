from django.shortcuts import get_object_or_404, render

from .models import Book


def book_detail(request, pk):
    book = get_object_or_404(
        Book.objects.select_related('author', 'author__profile')
        .prefetch_related('categories', 'publications__publisher'),
        pk=pk,
    )
    context = {'book': book}
    return render(request, 'library/book_detail.html', context)
