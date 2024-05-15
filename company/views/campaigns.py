from django.contrib.auth.decorators import login_required
from company.decorators import user_not_superuser_or_staff
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from campaigns.models import CampaignModel
from company.forms import CampaignUpdateStatusForm
from home.models import CategoryModel
from django.contrib import messages

USER = get_user_model()

@login_required
@user_not_superuser_or_staff
def all_campaigns(request, username=None):
    query = request.GET.get("query", None)
    queryset = CampaignModel.objects.all()
    if username:
        user = get_object_or_404(USER, username=username)
        if query:
            campaigns = queryset.filter(Q(organiser = user) & Q(title__icontains=query)| Q(organiser__first_name__icontains=query))
        else:
            campaigns = queryset.filter(organiser = user)
    else:
        if query:
            campaigns = queryset.filter(Q(title__icontains=query)| Q(organiser__first_name__icontains=query))
        else:
            campaigns = queryset
    
    return render(request, "company/campaigns/all-campaigns.html", {"campaigns": campaigns, "query": query})

@login_required
@user_not_superuser_or_staff
def campaign_details(request, campaign_slug):
    
    queryset = CampaignModel.objects.select_related("organiser", "category").prefetch_related("contributions").order_by("-created")
    campaign = get_object_or_404(queryset, slug = campaign_slug)
    backers = campaign.contributions.filter(paid="PAID").count()
    form = CampaignUpdateStatusForm(instance=campaign)

    if request.method == "POST":
        form = CampaignUpdateStatusForm(instance=campaign, data=request.POST)
        if form.is_valid():
            campaign = form.save()
            messages.success(request, "Campaign status was changed successfully")
            return redirect("company:campaign-details", campaign_slug=campaign.slug)
    

    return render(request, "company/campaigns/campaign-details.html", {"campaign": campaign, "form": form, "backers": backers})