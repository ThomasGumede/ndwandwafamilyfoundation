from django.urls import path
from business.views.business import add_listing, get_listings, get_listing, manage_listings, manage_listing

app_name = "business"

urlpatterns = [
    path("", get_listings, name="listings"),
    path("manage", manage_listings, name="manage-listings"),
    path("category=<slug:category>", get_listings, name="get-listings-by-category"),
    path("details/<slug:listing_slug>", get_listing, name="get-listing"),
    path("manage/<slug:listing_slug>", manage_listing, name="manage-listing"),
    path("add", add_listing, name = "add-listing")
]
