from rest_framework import generics, viewsets, permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from .models import Book
from .serializers import BookSerializer


class BookList(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    """Provides CRUD operations for Book.

    Authentication: TokenAuthentication (also supports session auth).
    Permissions: Authenticated users can create/update/delete; unauthenticated users can only read (list/retrieve).
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

