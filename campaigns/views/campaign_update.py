from campaigns.models import CampaignModel, CampaignUpdateModel
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from campaigns.forms import CampaignUpdateForm
from campaigns.tasks import update_contributors
from django.contrib.sites.shortcuts import get_current_site


@login_required
def create_campaign_update(request, campaign_slug):
    campaign = get_object_or_404(CampaignModel, slug=campaign_slug, organiser = request.user)
    if request.method == 'POST':
        form = CampaignUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.campaign = campaign
            update.save()
            messages.success(request, "Campaign update was successfully added")
            protocol = "https" if request.is_secure() else "http"
            domain = get_current_site(request).domain
            update_contributors.delay(update.id, domain, protocol)
            return redirect("campaigns:manage-campaign", campaign_id=campaign.id)
        else:
            messages.error(request, "Something went wrong, please fix errors below")
            return render(request, "campaigns/updates/create.html", {"form": form})
    
    return render(request, "campaigns/updates/create.html", {"form": CampaignUpdateForm()})

@login_required
def delete_campaign_update(request, update_id):
    campaign_update = get_object_or_404(CampaignUpdateModel, id = update_id)
    
    if request.method == "POST":
        campaign_update.delete()
        messages.success(request, "Campaign Update Deleted successfully!")
        return redirect("campaigns:manage-campaign", campaign_id=campaign_update.campaign.id)
    
    return render(request, "campaigns/delete/confirm_delete.html", {"message": f"Are you sure you want to delete this campaign update ({campaign_update.title})?", "title": "Delete campaign update"})
