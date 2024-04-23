from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
import logging, jwt
from accounts.models import WalletModel

User = get_user_model()

@login_required
def my_wallet(request):
    wallet = get_object_or_404(WalletModel, owner = request.user)
    
    try:
        me = User.objects.prefetch_related("campaigns", "events").get(username = request.user.username)
        ticket_orders = []
        contributions = []

        for event in me.events.all():
            ticket_orders.extend(event.ticket_orders.all())
        
        for campaign in me.campaigns.all():
            contributions.extend(campaign.contributions.all())

        return render(request, "accounts/wallet/details.html", {"wallet": wallet, "ticketorders": ticket_orders, "contributions": contributions})
    except User.DoesNotExist:
        return redirect("home:home")

    