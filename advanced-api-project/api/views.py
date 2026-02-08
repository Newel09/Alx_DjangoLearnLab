from rest_framework import generics
from .models import Book
from .serializers import BookSerializer

class BookListView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        """
        Optional filters:
        /api/books/?search=<text>
        """
        qs = Book.objects.all()

        search = self.request.query_params.get("search")
        if search:
            # Adjust field name(s) to match your model:
            qs = qs.filter(title__icontains=search)

        return qs

