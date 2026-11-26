from django.contrib import admin

from .models import Review, WishlistItem

admin.site.register(Review)
admin.site.register(WishlistItem)