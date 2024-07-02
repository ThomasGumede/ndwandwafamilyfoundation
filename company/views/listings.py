from business.models import Business
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from company.decorators import user_not_superuser_or_staff
from django.contrib.auth import get_user_model
from django.db.models import Q

@login_required
@user_not_superuser_or_staff
def all_listings(request, username=None):
    listings = Business.objects.all()
    query = request.GET.get("query", None)

    if query:
        listings = listings.filter(Q(title__icontains=query)| Q(owner__first_name__icontains=query))

    return render(request, "company/business/all-listings.html", {"listings": listings})

@login_required
@user_not_superuser_or_staff
def get_listing(request, listing_slug):
    queryset = Business.objects.all().select_related("category").prefetch_related("business_hours", "reviews", "images")
    listing = get_object_or_404(queryset, slug=listing_slug)

    return render(request, "company/business/get-listing.html", {"listing": listing})