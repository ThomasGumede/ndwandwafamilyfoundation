from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from company.decorators import user_not_superuser_or_staff
from campaigns.models import CampaignModel, ContributionModel
from events.models import EventModel, TicketOrderModel
from payments.models import NdwandwaBankModel

@login_required
@user_not_superuser_or_staff
def earnings(request):
    earnings = NdwandwaBankModel.objects.all()
    user_count = get_user_model().objects.all().count()
    campaigns_count = CampaignModel.objects.all().count()
    event_count = EventModel.objects.all().count()
    total = sum([bank.balance for bank in earnings])

    context = {
        "earnings": earnings,
        "total": total,
        "user_count": user_count,
        "campaigns_count": campaigns_count,
        "event_count": event_count
    }

    return render(request, "company/home/home.html", context)

@login_required
@user_not_superuser_or_staff
def view_order(request, order_uuid):
    try:
        contribution = ContributionModel.objects.select_related("contributor").get(id=order_uuid)
        return render(request, "company/contributions/details.html", {"order": contribution})
    except ContributionModel.DoesNotExist:
        order_queryset = TicketOrderModel.objects.select_related("event").prefetch_related("tickets")
        order = get_object_or_404(order_queryset, id=order_uuid)
        return render(request, "company/orders/details.html", {"order": order})