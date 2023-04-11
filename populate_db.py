import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

import json

from quotes_interface.models import Quotes

f = open('quotes.json')
data = json.load(f)

for obj in data:
    
    quote = obj["Quote"]
    author = obj["Author"]
    category = obj["Category"]

    quote_in_db, is_created = Quotes.objects.get_or_create(quote=quote, author=author)

    quote_in_db.categories.get_or_create(category=category)
