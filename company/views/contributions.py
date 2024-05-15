from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from company.decorators import user_not_superuser_or_staff
from campaigns.models import CampaignModel, ContributionModel
from campaigns.utils import generate_order_number, PaymentStatus
from accounts.utils import StatusChoices
from campaigns.forms import ContributionForm
from django.contrib import messages
from django.utils import timezone

@login_required
@user_not_superuser_or_staff
def all_contributions(request, campaign_id = None):
    
    contributions = ContributionModel.objects.select_related("contributor").all()
    campaign_model = None

    if campaign_id:
        campaign_model = get_object_or_404(CampaignModel, id=campaign_id)
        contributions = ContributionModel.objects.filter(campaign = campaign_model).select_related("contributor")
        

    return render(request, "company/contributions/contributions.html", {"orders": contributions, "campaign": campaign_model})

@login_required
@user_not_superuser_or_staff
def contribution_details(request, contribution_id):
    contributions = ContributionModel.objects.all().select_related("contributor")
    contribution = get_object_or_404(contributions, id=contribution_id)
    return render(request, "company/contributions/details.html", {"order": contribution})

@login_required
@user_not_superuser_or_staff
def delete_contribution(request, contribution_id):
    contribution = get_object_or_404(ContributionModel, id = contribution_id)
    if contribution.paid == PaymentStatus.PAID:
        messages.warning(request, "You cannot delete already paid payment contribution, please visit our <a href='' class='text-custom-primary'>refund policy</a>")
        return redirect("company:all-contributions")
    
    if request.method == "POST":
        contribution.delete()
        messages.success(request, "You contribution was deleted successfully")
        return redirect("company:all-contributions")
    
    return render(request, "campaigns/delete/confirm_delete.html", {"message": f"Are you sure you want to cancel this contribution ({contribution.order_number})?", "title": "Cancel Contribution"})