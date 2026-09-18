"""
Laboratorio N4 - Relacion de Modelos en Django
Script de operaciones y pruebas ORM para la aplicacion 'library'.

Ejecutar desde la raiz del proyecto con el shell interactivo de Django
(ver README.md para el comando exacto).

El script es idempotente: se puede re-ejecutar sobre la misma base de datos.
"""

import sys
from datetime import date

from django.db import connection, models
from django.db.models.deletion import ProtectedError

from library.models import (
    Author,
    AuthorProfile,
    Book,
    Category,
    Publication,
    Publisher,
)

sys.stdout.reconfigure(encoding='utf-8')


def print_header(title):
    print('')
    print('=' * 78)
    print(title)
    print('=' * 78)


def populate_database():
    print_header('a) POBLACION INICIAL')

    robert = Author.objects.get_or_create(
        email='robert.martin@example.com',
        defaults={
            'first_name': 'Robert',
            'last_name': 'Martin',
        },
    )[0]
    andrew = Author.objects.get_or_create(
        email='andrew.hunt@example.com',
        defaults={
            'first_name': 'Andrew',
            'last_name': 'Hunt',
        },
    )[0]
    AuthorProfile.objects.get_or_create(
        author=robert,
        defaults={
            'biography': 'Robert C. Martin, known as Uncle Bob, is a pioneer '
                         'of the software craftsmanship movement and author '
                         'of the Clean Code series.',
            'website': 'https://cleancoder.com',
        },
    )
    AuthorProfile.objects.get_or_create(
        author=andrew,
        defaults={
            'biography': 'Andrew Hunt is the co-author of The Pragmatic '
                         'Programmer and one of the founders of the Agile '
                         'manifesto.',
            'website': 'https://pragprog.com',
        },
    )
    print('- Autores creados:')
    for author in Author.objects.all():
        print(f'    * {author} <{author.email}>')

    software_engineering = Category.objects.get_or_create(
        name='Software Engineering',
        defaults={'description': 'Principles and practices for building '
                                 'high quality software systems.'},
    )[0]
    architecture = Category.objects.get_or_create(
        name='Architecture',
        defaults={'description': 'High level structure, layers and design '
                                 'decisions of software systems.'},
    )[0]
    agile = Category.objects.get_or_create(
        name='Agile',
        defaults={'description': 'Iterative development methodologies that '
                                 'embrace change and collaboration.'},
    )[0]
    print('- Categorias creadas:')
    for category in Category.objects.all():
        print(f'    * {category.name}')

    prentice_hall = Publisher.objects.get_or_create(
        name='Prentice Hall',
        defaults={
            'address': 'One Lake Street, Upper Saddle River, NJ, USA',
            'website': 'https://www.pearson.com',
        },
    )[0]
    pragmatic_bookshelf = Publisher.objects.get_or_create(
        name='Pragmatic Bookshelf',
        defaults={
            'address': 'Raleigh, North Carolina, USA',
            'website': 'https://pragprog.com',
        },
    )[0]
    print('- Editoriales creadas:')
    for publisher in Publisher.objects.all():
        print(f'    * {publisher.name}')

    book_clean_architecture = Book.objects.get_or_create(
        isbn='9780134494166',
        defaults={
            'title': 'Clean Architecture: A Craftsman\'s Guide to Software '
                     'Structure and Design',
            'summary': 'Presents the principles of clean architecture and how '
                       'to structure software to survive change.',
            'author': robert,
        },
    )[0]
    book_pragmatic = Book.objects.get_or_create(
        isbn='9780201616224',
        defaults={
            'title': 'The Pragmatic Programmer: Your Journey to Mastery',
            'summary': 'A journey through the best practices of pragmatic '
                       'software development.',
            'author': andrew,
        },
    )[0]
    book_clean_code = Book.objects.get_or_create(
        isbn='9780132350884',
        defaults={
            'title': 'Clean Code: A Handbook of Agile Software Craftsmanship',
            'summary': 'Best practices for writing readable, maintainable and '
                       'robust code.',
            'author': robert,
        },
    )[0]
    book_pragmatic_thinking = Book.objects.get_or_create(
        isbn='9781934356050',
        defaults={
            'title': 'Pragmatic Thinking and Learning',
            'summary': 'Explores how the brain works and how to improve your '
                       'learning and problem solving skills.',
            'author': andrew,
        },
    )[0]

    book_clean_architecture.categories.add(software_engineering, architecture)
    book_pragmatic.categories.add(software_engineering, agile)
    book_clean_code.categories.add(software_engineering)
    book_pragmatic_thinking.categories.add(software_engineering)

    publications = [
        {
            'book': book_clean_architecture,
            'publisher': prentice_hall,
            'publication_date': date(2017, 9, 25),
            'edition': 1,
        },
        {
            'book': book_pragmatic,
            'publisher': pragmatic_bookshelf,
            'publication_date': date(1999, 10, 30),
            'edition': 1,
        },
        {
            'book': book_pragmatic,
            'publisher': pragmatic_bookshelf,
            'publication_date': date(2019, 9, 13),
            'edition': 2,
        },
        {
            'book': book_clean_code,
            'publisher': prentice_hall,
            'publication_date': date(2008, 8, 1),
            'edition': 1,
        },
        {
            'book': book_pragmatic_thinking,
            'publisher': pragmatic_bookshelf,
            'publication_date': date(2008, 11, 11),
            'edition': 1,
        },
    ]
    for item in publications:
        Publication.objects.get_or_create(
            book=item['book'],
            publisher=item['publisher'],
            edition=item['edition'],
            defaults={'publication_date': item['publication_date']},
        )

    print('- Libros creados:')
    for book in Book.objects.all():
        categories = ', '.join(book.categories.values_list('name', flat=True))
        print(f'    * {book.title} (ISBN {book.isbn})')
        print(f'        Autor: {book.author} | Categorias: {categories}')

    print('- Historial del modelo intermedio Publication:')
    for publication in Publication.objects.select_related('book', 'publisher'):
        print(f'    * {publication.book.title} | {publication.publisher.name} '
              f'| ed. {publication.edition} | {publication.publication_date}')


def demonstrate_queries():
    print_header('b) CONSULTAS ORM BIDIRECCIONALES')

    print('- Consulta de ida (Forward Query): libro por ISBN -> '
          'autor y perfil')
    book = Book.objects.get(isbn='9780134494166')
    print(f'    Libro: {book.title}')
    print(f'    Autor: {book.author}')
    print(f'    Sitio web del perfil: {book.author.profile.website}')

    print('- Consulta inversa (Reverse Query): autor por email -> libros')
    author = Author.objects.get(email='andrew.hunt@example.com')
    print(f'    Autor: {author}')
    for authored_book in author.books.all():
        print(f'    * {authored_book.title}')

    print('- Lookup: filtro con "__" - libros por categoria "Agile":')
    for agile_book in Book.objects.filter(categories__name='Agile'):
        print(f'    * {agile_book.title}')

    print('- Lookup: filtro con "__" - libros por apellido "Martin":')
    for martin_book in Book.objects.filter(author__last_name='Martin'):
        print(f'    * {martin_book.title}')

    print('- Consulta del modelo intermedio - publicaciones de la editorial '
          '"Pragmatic Bookshelf":')
    for publication in Publication.objects.filter(
        publisher__name='Pragmatic Bookshelf'
    ):
        print(f'    * {publication.book.title} | ed. {publication.edition} '
              f'| {publication.publication_date}')


def demonstrate_on_delete():
    print_header('c) VERIFICACION DE INTEGRIDAD REFERENCIAL (on_delete)')

    print('- CASCADE: eliminar al autor Robert Martin')
    robert = Author.objects.get(email='robert.martin@example.com')
    books_before = robert.books.count()
    profile_before = AuthorProfile.objects.filter(author=robert).exists()
    print(f'    Antes del borrado -> libros asociados: {books_before}, '
          f'perfil existente: {profile_before}')
    for book in robert.books.all():
        print(f'        Se eliminara tambien el libro: {book.title}')
    robert.delete()
    books_after = Book.objects.filter(
        author__email='robert.martin@example.com'
    ).count()
    profile_after = AuthorProfile.objects.filter(
        author__email='robert.martin@example.com'
    ).exists()
    print(f'    Despues del borrado -> libros restantes: {books_after}, '
          f'perfil existente: {profile_after}')
    print('    Conclusión CASCADE: la eliminacion del autor arrastro '
          'automaticamente sus libros y su perfil.')

    print('')
    print('- PROTECT: modelo scratch con ForeignKey(on_delete=PROTECT)')

    class ScratchContract(models.Model):
        author = models.ForeignKey(
            Author,
            on_delete=models.PROTECT,
            related_name='scratch_contracts',
        )
        note = models.CharField(max_length=100)

        class Meta:
            app_label = 'library'

    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(ScratchContract)

    andrew = Author.objects.get(email='andrew.hunt@example.com')
    ScratchContract.objects.get_or_create(
        author=andrew,
        defaults={'note': 'Protected contract against author deletion.'},
    )
    try:
        andrew.delete()
    except ProtectedError as error:
        print('    Excepcion capturada: django.db.models.deletion.'
              'ProtectedError')
        print(f'    Objetos que bloquean el borrado: '
              f'{error.protected_objects}')
    else:
        print('    No se lanzo ProtectedError -> el comportamiento '
              'esperado fallo.')
    still_exists = Author.objects.filter(
        email='andrew.hunt@example.com'
    ).exists()
    print(f'    Despues del intento, ¿sigue existiendo el autor? '
          f'{still_exists}')
    print('    Conclusion PROTECT: Django impide eliminar el autor y suelta '
          'ProtectedError cuando existe una relacion configurada con '
          'on_delete=PROTECT, preservando la integridad referencial.')

    ScratchContract.objects.all().delete()
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(ScratchContract)


def restore_robert():
    print_header('RESTAURACION DEL DATASET DE DEMOSTRACION')
    robert = Author.objects.get_or_create(
        email='robert.martin@example.com',
        defaults={
            'first_name': 'Robert',
            'last_name': 'Martin',
        },
    )[0]
    AuthorProfile.objects.get_or_create(
        author=robert,
        defaults={
            'biography': 'Robert C. Martin, known as Uncle Bob, is a pioneer '
                         'of the software craftsmanship movement and author '
                         'of the Clean Code series.',
            'website': 'https://cleancoder.com',
        },
    )
    software_engineering = Category.objects.get(name='Software Engineering')
    architecture = Category.objects.get(name='Architecture')
    prentice_hall = Publisher.objects.get(name='Prentice Hall')

    clean_architecture = Book.objects.get_or_create(
        isbn='9780134494166',
        defaults={
            'title': 'Clean Architecture: A Craftsman\'s Guide to Software '
                     'Structure and Design',
            'summary': 'Presents the principles of clean architecture and how '
                       'to structure software to survive change.',
            'author': robert,
        },
    )[0]
    clean_code = Book.objects.get_or_create(
        isbn='9780132350884',
        defaults={
            'title': 'Clean Code: A Handbook of Agile Software Craftsmanship',
            'summary': 'Best practices for writing readable, maintainable and '
                       'robust code.',
            'author': robert,
        },
    )[0]
    clean_architecture.categories.add(software_engineering, architecture)
    clean_code.categories.add(software_engineering)
    Publication.objects.get_or_create(
        book=clean_architecture,
        publisher=prentice_hall,
        edition=1,
        defaults={'publication_date': date(2017, 9, 25)},
    )
    Publication.objects.get_or_create(
        book=clean_code,
        publisher=prentice_hall,
        edition=1,
        defaults={'publication_date': date(2008, 8, 1)},
    )
    print('- Se restauro el autor Robert Martin, sus libros y sus '
          'publicaciones para dejar el dataset completo.')


populate_database()
demonstrate_queries()
demonstrate_on_delete()
restore_robert()

print_header('RESUMEN FINAL')
print(f'    Autores                     : {Author.objects.count()}')
print(f'    Perfiles de autor           : {AuthorProfile.objects.count()}')
print(f'    Categorias                  : {Category.objects.count()}')
print(f'    Editoriales                 : {Publisher.objects.count()}')
print(f'    Libros                      : {Book.objects.count()}')
print(f'    Publicaciones (intermedio)  : {Publication.objects.count()}')
print('')
print('Laboratorio completado con exito. Puedes revisar la vista')
print("'book/<int:pk>/' y el panel de administracion '/admin/'.")
