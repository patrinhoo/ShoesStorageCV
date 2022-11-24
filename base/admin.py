from django.contrib import admin
from .models import Seller, Buyer, IncommingShoe, InStorageShoe, SoldShoe, OnAuctionShoe

# Register your models here.
admin.site.register(Seller)
admin.site.register(Buyer)
admin.site.register(IncommingShoe)
admin.site.register(InStorageShoe)
admin.site.register(SoldShoe)
admin.site.register(OnAuctionShoe)
