"""
Query Samples for Django ORM Relationships
This script demonstrates how to query data using ForeignKey, ManyToMany, and OneToOne relationships.

To run these queries, use Django shell:
    python manage.py shell
    exec(open('relationship_app/query_samples.py').read())
"""

from relationship_app.models import Author, Book, Library, Librarian

# ============================================================================
# 1. ForeignKey Query - Query all books by a specific author
# ============================================================================

def query_books_by_author(author_name):
    """
    Query all books by a specific author using ForeignKey relationship.
    Author has a one-to-many relationship with Book.
    """
    try:
        # Method 1: Filter books by author name
        author = Author.objects.get(name=author_name)
        books = Book.objects.filter(author=author)
        
        print(f"\n=== Books by Author: {author_name} ===")
        print(f"Author: {author.name}")
        print(f"Number of books: {books.count()}")
        for book in books:
            print(f"  - {book.title} (Author: {book.author.name})")
        
        return books
    except Author.DoesNotExist:
        print(f"Author '{author_name}' not found.")
        return None


def query_books_by_author_alternative(author_id):
    """
    Alternative method using reverse relationship from Author to Book.
    """
    try:
        author = Author.objects.get(id=author_id)
        # Using reverse relationship via related_name 'books'
        books = author.books.all()
        
        print(f"\n=== Books by Author (using reverse relation): {author.name} ===")
        for book in books:
            print(f"  - {book.title}")
        
        return books
    except Author.DoesNotExist:
        print(f"Author with ID {author_id} not found.")
        return None


# ============================================================================
# 2. ManyToMany Query - List all books in a library
# ============================================================================

def query_books_in_library(library_name):
    """
    Query all books in a specific library using ManyToMany relationship.
    Library has a many-to-many relationship with Book.
    """
    try:
        library = Library.objects.get(name=library_name)
        books = library.books.all()
        
        print(f"\n=== Books in Library: {library_name} ===")
        print(f"Library: {library.name}")
        print(f"Total books in library: {books.count()}")
        for book in books:
            print(f"  - {book.title} (Author: {book.author.name})")
        
        return books
    except Library.DoesNotExist:
        print(f"Library '{library_name}' not found.")
        return None


def query_libraries_by_book(book_title):
    """
    Reverse ManyToMany query - Find all libraries that contain a specific book.
    """
    try:
        book = Book.objects.get(title=book_title)
        libraries = book.libraries.all()
        
        print(f"\n=== Libraries containing book: {book_title} ===")
        print(f"Book: {book.title} (Author: {book.author.name})")
        print(f"Available in {libraries.count()} libraries:")
        for library in libraries:
            print(f"  - {library.name}")
        
        return libraries
    except Book.DoesNotExist:
        print(f"Book '{book_title}' not found.")
        return None


# ============================================================================
# 3. OneToOne Query - Retrieve the librarian for a library
# ============================================================================

def query_librarian_for_library(library_name):
    """
    Query the librarian for a specific library using OneToOne relationship.
    Librarian has a one-to-one relationship with Library.
    """
    try:
        library = Library.objects.get(name=library_name)
        librarian = library.librarian
        
        print(f"\n=== Librarian for Library: {library_name} ===")
        print(f"Library: {library.name}")
        print(f"Librarian: {librarian.name}")
        
        return librarian
    except Library.DoesNotExist:
        print(f"Library '{library_name}' not found.")
        return None
    except Librarian.DoesNotExist:
        print(f"No librarian assigned to library '{library_name}'.")
        return None


def query_library_by_librarian(librarian_name):
    """
    Reverse OneToOne query - Find the library managed by a specific librarian.
    """
    try:
        librarian = Librarian.objects.get(name=librarian_name)
        library = librarian.library
        
        print(f"\n=== Library managed by Librarian: {librarian_name} ===")
        print(f"Librarian: {librarian.name}")
        print(f"Library: {library.name}")
        print(f"Total books: {library.books.count()}")
        
        return library
    except Librarian.DoesNotExist:
        print(f"Librarian '{librarian_name}' not found.")
        return None


# ============================================================================
# 4. Complex Queries combining multiple relationships
# ============================================================================

def query_all_books_by_author_in_library(author_name, library_name):
    """
    Complex query: Find books by a specific author that are also in a specific library.
    Combines ForeignKey and ManyToMany relationships.
    """
    try:
        author = Author.objects.get(name=author_name)
        library = Library.objects.get(name=library_name)
        
        # Books by author that are also in this library
        books = library.books.filter(author=author)
        
        print(f"\n=== Books by {author_name} in {library_name} ===")
        print(f"Author: {author.name}")
        print(f"Library: {library.name}")
        print(f"Matching books: {books.count()}")
        for book in books:
            print(f"  - {book.title}")
        
        return books
    except (Author.DoesNotExist, Library.DoesNotExist) as e:
        print(f"Query failed: {e}")
        return None


def query_all_library_data():
    """
    Comprehensive query showing all entities and their relationships.
    """
    print("\n=== All Library Data ===")
    
    print("\nAuthors:")
    for author in Author.objects.all():
        print(f"  - {author.name} ({author.books.count()} books)")
    
    print("\nBooks:")
    for book in Book.objects.all():
        libraries_count = book.libraries.count()
        print(f"  - {book.title} by {book.author.name} ({libraries_count} libraries)")
    
    print("\nLibraries:")
    for library in Library.objects.all():
        books_count = library.books.count()
        librarian = getattr(library, 'librarian', None)
        librarian_name = librarian.name if librarian else "Not assigned"
        print(f"  - {library.name} ({books_count} books, Librarian: {librarian_name})")


# ============================================================================
# Sample Usage and Data Creation
# ============================================================================

def create_sample_data():
    """
    Create sample data for demonstration purposes.
    Run this function first to populate the database.
    """
    print("\n=== Creating Sample Data ===")
    
    # Create Authors
    author1, created = Author.objects.get_or_create(name="J.K. Rowling")
    author2, created = Author.objects.get_or_create(name="George R.R. Martin")
    author3, created = Author.objects.get_or_create(name="J.R.R. Tolkien")
    print("✓ Authors created")
    
    # Create Books
    book1, created = Book.objects.get_or_create(title="Harry Potter and the Philosopher's Stone", author=author1)
    book2, created = Book.objects.get_or_create(title="Harry Potter and the Chamber of Secrets", author=author1)
    book3, created = Book.objects.get_or_create(title="A Game of Thrones", author=author2)
    book4, created = Book.objects.get_or_create(title="The Fellowship of the Ring", author=author3)
    print("✓ Books created")
    
    # Create Libraries
    lib1, created = Library.objects.get_or_create(name="Central Library")
    lib2, created = Library.objects.get_or_create(name="Downtown Library")
    print("✓ Libraries created")
    
    # Add books to libraries (ManyToMany)
    lib1.books.add(book1, book2, book3, book4)
    lib2.books.add(book1, book3)
    print("✓ Books added to libraries")
    
    # Create Librarians (OneToOne)
    librarian1, created = Librarian.objects.get_or_create(name="Alice Johnson", library=lib1)
    librarian2, created = Librarian.objects.get_or_create(name="Bob Smith", library=lib2)
    print("✓ Librarians created")
    
    print("\n✓ Sample data created successfully!")


if __name__ == "__main__":
    # Uncomment below to create sample data
    # create_sample_data()
    
    # Uncomment below to run sample queries
    # query_books_by_author("J.K. Rowling")
    # query_books_in_library("Central Library")
    # query_librarian_for_library("Central Library")
    # query_all_library_data()
    pass
