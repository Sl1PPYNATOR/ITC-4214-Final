from django.contrib import admin
from .models import Brand, Car, CarView, Category, SearchLog

admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Car)
admin.site.register(CarView)
admin.site.register(SearchLog)