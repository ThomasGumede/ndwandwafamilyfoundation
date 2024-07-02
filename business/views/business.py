from django.db.models import Q
from django.forms import formset_factory
from business.forms import BusinessForm, BusinessHourForm, BusinessContent, BusinessReviewForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from business.models import Business, Category, BusinessHour
from django.contrib import messages

@login_required
def manage_listings(request):
    listings = Business.objects.filter(owner = request.user)
    query = request.GET.get("query", None)

    if query:
        listings = listings.filter(Q(title__icontains=query)| Q(owner__first_name__icontains=query))
        
    return render(request, "business/manage/manage-listings.html", {"listings": listings})

@login_required
def manage_listing(request, listing_slug):
    queryset = Business.objects.all().select_related("category").prefetch_related("business_hours", "reviews", "images")
    listing = get_object_or_404(queryset, slug=listing_slug, owner=request.user)
    return render(request, "business/manage/manage-listing.html", {"listing": listing})

def get_listings(request, category=None):
    listings = Business.objects.all()
    if category:
        category = get_object_or_404(Category, slug=category)
        listings = listings.filter(category=category)

    return render(request, "business/listings.html", {"listings": listings})

def get_listing(request, listing_slug):
    queryset = Business.objects.all().select_related("category").prefetch_related("business_hours", "reviews", "images")
    listing = get_object_or_404(queryset, slug=listing_slug)
    form = BusinessReviewForm()

    if request.method == "POST":
        form = BusinessReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.business = listing
            if request.user.is_authenticated:
                review.commenter = request.user
            review.save()
            messages.success(request, "Review added successfully")
            return redirect("business:get-listing", listing_slug=listing.slug)
        
        messages.error(request, "Error trying to add your review")
        return render(request, "business/get_listing.html", {"listing": listing, "form": form})

    return render(request, "business/get_listing.html", {"listing": listing, "form": form})

@login_required
def add_listing(request):
    if request.user.subscription == None:
        messages.warning(request, "Sorry, you cannot add listing without subscription")
        return redirect("accounts:choose-package")
    
    buniness_form = BusinessForm()
    business_hour_forms = formset_factory(BusinessHourForm, extra=6, max_num=6)

    if request.method == "POST":
        form = BusinessForm(request.POST, request.FILES)
        forms = business_hour_forms(request.POST)
        if form.is_valid() and form.is_multipart() and forms.is_valid():
            files = request.FILES.getlist("files")
            business = form.save(commit=False)
            business.owner = request.user
            business.save()

            if len(files) > 0:
                for file in files:
                    business_content = BusinessContent(image=file, business=business)
                    business_content.save()

            for hours in forms:
                business_hours = hours.save(commit=False)
                business_hours.business = business
                business_hours.save()
            
            return redirect("business:manage-listing", listing_slug=business.slug)
        else:
            messages.error(request, "Something went wrong while trying to add your business")
            
            print(forms.errors)
            print(form.errors)
            return render(request, "business/add_listing.html", {"form": form, "forms": forms})
    
    return render(request, "business/add_listing.html", {"form": buniness_form, "forms": business_hour_forms})


@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Business, id=listing_id, owner=request.user)
