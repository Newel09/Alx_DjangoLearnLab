# api/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer


class IsAuthenticatedForWrite(AllowAny):
    """
    Custom permission class that allows:
    - Anyone (authenticated or not) to read (GET, HEAD, OPTIONS)
    - Only authenticated users to write (POST, PUT, PATCH, DELETE)
    """
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user and request.user.is_authenticated


class BookListCreateView(generics.ListCreateAPIView):
    """
    GET /api/books/ -> List all books (read-only, no auth required)
    POST /api/books/ -> Create a new book (authenticated users only)
    
    This view combines listing and creation in a single endpoint.
    - Query filtering by author_id is supported: /api/books/?author_id=1
    - Pagination is enabled via DRF settings
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedForWrite]

    def get_queryset(self):
        """
        Optionally filter books by author_id query parameter.
        Example: GET /api/books/?author_id=1
        """
        queryset = super().get_queryset()
        author_id = self.request.query_params.get('author_id', None)
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        return queryset

    def perform_create(self, serializer):
        """
        Custom logic when creating a book.
        - Saves the book instance
        - Validation errors are automatically handled by DRF
        """
        try:
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)

    def create(self, request, *args, **kwargs):
        """
        Override create() to add custom response handling.
        Returns the created book with 201 Created status.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookDetailView(generics.RetrieveAPIView):
    """
    GET /api/books/<pk>/ -> Retrieve a single book by ID (read-only, no auth required)
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]


class BookUpdateView(generics.UpdateAPIView):
    """
    PUT /api/books/<pk>/ -> Full update (authenticated users only)
    PATCH /api/books/<pk>/ -> Partial update (authenticated users only)
    
    This view handles both full (PUT) and partial (PATCH) updates.
    - Supports filtering by pk (primary key)
    - Full validation is performed on all fields for PUT requests
    - Partial validation for PATCH requests
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        """
        Custom logic when updating a book.
        Ensures validation is performed before save.
        """
        try:
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)

    def update(self, request, *args, **kwargs):
        """
        Override update() to add custom response handling.
        Supports both PUT (full update) and PATCH (partial update).
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/books/<pk>/ -> Delete a book (authenticated users only)
    
    This view handles deletion of Book instances.
    - Only authenticated users can delete books
    - Returns 204 No Content on successful deletion
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        """
        Custom logic when deleting a book.
        """
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy() to add custom response handling.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)