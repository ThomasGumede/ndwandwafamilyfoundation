from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from campaigns.models import CampaignModel, ContributionModel
from campaigns.utils import generate_order_number, PaymentStatus
from accounts.utils import StatusChoices
from campaigns.forms import ContributionForm
from django.contrib import messages
from django.utils import timezone

@login_required
def manage_contributions(request):
    contributions = ContributionModel.objects.filter(contributor = request.user).select_related("campaign", "contributor")
    return render(request, "campaigns/contributions/manage/contributions.html", {"contributions": contributions})

@login_required
def manage_contribution(request, contribution_id):
    contributions = ContributionModel.objects.filter(contributor = request.user).select_related("campaign", "contributor")
    contribution = get_object_or_404(contributions, id=contribution_id)

    return render(request, "campaigns/contributions/manage/contribution.html", {"order": contribution})

@login_required
def contributions(request, campaign_id = None):
    
    contributions = None
    campaign_model = None

    if campaign_id:
        campaign_model = get_object_or_404(CampaignModel, id=campaign_id, organiser=request.user)
        contributions = ContributionModel.objects.filter(campaign = campaign_model).select_related("contributor")
    else:
        campaigns = CampaignModel.objects.prefetch_related("contributions").filter(organiser=request.user).order_by("-created")
        
        contributions = []
        for campaign in campaigns:
            contributions.extend(campaign.contributions.all())
        

    return render(request, "campaigns/contributions/contributions.html", {"orders": contributions, "campaign": campaign_model})

@login_required
def contribution(request, contribution_id, campaign_id):
    campaign = get_object_or_404(CampaignModel, id=campaign_id, organiser=request.user)
    contributions = ContributionModel.objects.filter(campaign = campaign).select_related("contributor")
    contribution = get_object_or_404(contributions, id=contribution_id)
    return render(request, "campaigns/contributions/contribution.html", {"order": contribution})

@login_required
def create_contribution(request, campaign_id):
    campaign = get_object_or_404(CampaignModel.objects.filter(status = StatusChoices.APPROVED), id = campaign_id)
    date = campaign.end_date  - timezone.now()
    if date.days <= 0:
        messages.error(request, "Sorry, this campaign is closed and no longer receives contributions, Thank you")
        campaign.status = StatusChoices.COMPLETED
        campaign.save(update_fields=["status"])
        return redirect("campaigns:campaign", campaign_slug=campaign.slug)
    
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.accepted_laws = True
            contribution.campaign = campaign
            contribution.contributor = request.user
            contribution.order_number = generate_order_number(ContributionModel)
            contribution.save()
            messages.success(request, "Your contribution was added successfully")
            return redirect("payments:contribution-payment", contribution_id=contribution.id)
        else:
           messages.error(request, "Please fix errors below")
           return render(request, "campaigns/contributions/summary.html", {"campaign": campaign, "form": form}) 

    form = ContributionForm()
    return render(request, "campaigns/contributions/summary.html", {"campaign": campaign, "form": form})

@login_required
def cancel_contribution(request, contribution_id):
    contribution = get_object_or_404(ContributionModel, contributor = request.user, id = contribution_id)
    if contribution.paid == PaymentStatus.PAID:
        messages.warning(request, "You cannot cancel an already paid or pending payment contribution, please visit our <a href='' class='text-custom-primary'>refund policy</a>")
        return redirect("accounts:contributions")
    
    if request.method == "POST":
        contribution.delete()
        return redirect("accounts:contributions")
    
    return render(request, "campaigns/delete/confirm_delete.html", {"message": f"Are you sure you want to cancel this contribution ({contribution.order_number})?", "title": "Cancel Contribution"})
