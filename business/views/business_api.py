from django.contrib.auth.decorators import login_required
from business.models import Business, Category, BusinessHour
from django.core import serializers
from django.http import JsonResponse

@login_required
def get_business_hours_api(request, listing_id):
    try:
        listing = Business.objects.prefetch_related("business_hours").get(id = listing_id)
        business_hours = serializers.serialize("json", listing.business_hours.all())
        return JsonResponse({"success": True, "hours": business_hours}, status=200)
    
    except Business.DoesNotExist:
        return JsonResponse({"success": False, "hours": "Listing does not exists"}, status=200)

