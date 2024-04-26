from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import WalletModel

User = get_user_model()

@login_required
def my_wallet(request):
    wallet = get_object_or_404(WalletModel, owner = request.user)
    
    try:
        message = None
        if wallet.status == "Requested Payout Details":
            message = "Your wallet status is 'Requested Payment Details', Please email your bank details to 'finance@ndwandwa.africa'. Thank you"
        
        if wallet.status == "Verifying Payout Details":
            message = "We received your bank details, we are still verifying them. For more enquires, please contact 'finance@ndwandwa.africa'. Thank you"

        if wallet.status == "Payout Declined":
            message = "Payout was declined due to some issues with your bank details or profile. For more enquires, please contact 'finance@ndwandwa.africa'. Thank you"

        me = User.objects.prefetch_related("campaigns", "events").get(username = request.user.username)
        ticket_orders = []
        contributions = []

        for event in me.events.all():
            ticket_orders.extend(event.ticket_orders.all())
        
        for campaign in me.campaigns.all():
            contributions.extend(campaign.contributions.all())

        return render(request, "accounts/wallet/details.html", {"wallet": wallet, "ticketorders": ticket_orders, "contributions": contributions, "infor": message})
    except User.DoesNotExist:
        return redirect("home:home")

    