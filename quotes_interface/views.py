import random

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .models import Quotes, Categories
from .serializers import QuoteSerializer


@api_view(['GET'])
def quote_generator(request, format=None):
    """
    Randomly generates a quote to type and returns it.
    """

    if request.method == "GET":
        quotes = Quotes.objects.all()
        random_quote = random.choice(list(quotes))


        categories = quotes.get(id = random_quote.id).categories.all()
        category_list = []
        for category in list(categories):
            category_list.append(category.category)

        serializer = QuoteSerializer(data = {'quote' : random_quote.quote, 'author' : random_quote.author, 'categories': category_list,})
        # serializer.is_valid()

        print(serializer.initial_data)
        return Response(serializer.initial_data)
