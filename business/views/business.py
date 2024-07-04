from django.db.models import Q
from django.forms import formset_factory, modelformset_factory, BaseModelFormSet
from business.forms import BusinessForm, BusinessHourForm, BusinessContent, BusinessReviewForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from business.models import Business, Category, BusinessHour
from django.core import serializers
from django.http import JsonResponse
from django.contrib import messages

class BaseBusinessHourFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instances = super().save(commit=False)
        for instance in instances:
            hour = None
            try:
                hour = self.queryset.get(day=instance.day)
                if self.business:
                    hour.business = self.business
                    hour.open_time = instance.open_time
                    hour.close_time = instance.close_time
                    hour.operating = instance.operating

                if commit:
                    hour.save()
            except Exception:
                pass
            
            
        self.save_m2m()
        return instances

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
    return render(request, "business/get_listing.html", {"listing": listing})

def get_listings(request, category=None):
    query = request.GET.get("query", None)
    listings = Business.objects.all()
    categories = Category.objects.all()
    if category:
        category = get_object_or_404(categories, slug=category)
        listings = listings.filter(category=category)
    
    if query:
        listings = listings.filter(Q(title__icontains=query) | Q(category__label__icontains=query) | Q(slogan__icontains=query))

    return render(request, "business/listings.html", {"listings": listings, "lcategories": categories})


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
    business_hour_forms = formset_factory(BusinessHourForm, extra=7, max_num=7)

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
            
            return render(request, "business/add_listing.html", {"form": form, "forms": forms})
    
    return render(request, "business/add_listing.html", {"form": buniness_form, "forms": business_hour_forms})

@login_required
def update_listing(request, listing_id):
    queryset = Business.objects.all().select_related("category").prefetch_related("business_hours", "reviews", "images")
    listing = get_object_or_404(queryset, id=listing_id, owner=request.user)
    buniness_form = BusinessForm(instance=listing)
    business_hour_formset = modelformset_factory(BusinessHour, BusinessHourForm, formset=BaseBusinessHourFormSet,extra=7, max_num=7)
    business_hour_forms = business_hour_formset(queryset=listing.business_hours.all())

    if request.method == "POST":
        form = BusinessForm(instance=listing, data=request.POST, files=request.FILES)
        forms = business_hour_formset(request.POST, queryset=listing.business_hours.all(), business=listing)
        if form.is_valid() and form.is_multipart() and forms.is_valid():
            email = form.cleaned_data["email"]
            print(email)
            form.save()
            forms.save()
            messages.success(request, "Listing updated successfully")
            return redirect("business:manage-listing", listing_slug=listing.slug)
        else:
            messages.error(request, "Something went wrong while trying to update your business")
            return render(request, "business/update-listing.html", {"form": form, "forms": forms})
        
    return render(request, "business/update-listing.html", {"listing": listing, "form": buniness_form, "forms": business_hour_forms})

@login_required
def delete_business_content(request):
    id = request.POST.get("id")
    try:
        content = BusinessContent.objects.get(id = id)
        content.delete()

    except BusinessContent.DoesNotExist:
        return JsonResponse({"success": False, "content": "Image does not exists"}, status=200)

@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Business, id=listing_id, owner=request.user)
    if request.method == "POST":
        listing.delete()
        messages.success(request, "Listing was deleted successfully")
        return redirect("business:manage-listings")
    else:
        return render(request, "business/delete-listing.html", {"message": f"Are you sure you want to delete this listing ({listing.title})?", "title": "Delete listing"})
