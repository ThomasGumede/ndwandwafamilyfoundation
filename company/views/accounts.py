import logging
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import WalletModel
from company.decorators import user_not_superuser_or_staff
from django.contrib.auth import get_user_model
from django.db.models import Q

from company.forms import WalletStatusUpdateForm
from company.tasks import notify_user_of_status_change

USER = get_user_model()
logger = logging.getLogger("accounts")

messages_str = {
    "approved": """
    <p style='margin: 0; margin-bottom: 6px;'>We hope this email finds well<p>
    <p style='margin: 0; margin-bottom: 6px;'>
    This email serves to confirm that your wallet status has changed to <b>Payment Approved</b>. 
    Please expect your payment to reflex on your personal account in <b>2 to 3 working days</b>. Thank you for being part of Ndwandwa Family Foundation.
    <p>
    """,
    "request": """
    <p style='margin: 0; margin-bottom: 6px;'>We hope this email finds well<p>
    <p style='margin: 0; margin-bottom: 6px;'>
    This email serves to confirm that your wallet status has changed to <b>Request Payment Details</b>. 
    Please email your payment details(Bank account details) to <b>sazi.ndwandwa@gmail.com</b>. Thank you for being part of Ndwandwa Family Foundation.
    <p>
    """,
    "declined": """
    <p style='margin: 0; margin-bottom: 6px;'>We hope this email finds well<p>
    <p style='margin: 0; margin-bottom: 6px;'>
    This email serves to confirm that your wallet status has changed to <b>Payment Declined</b>. 
    Payment to your account was declined due to some errors while trying to verify your payment details. Please email <b>sazi.ndwandwa@gmail.com</b> for more details. Thank you for being part of Ndwandwa Family Foundation.
    <p>
    """,
}

@login_required
@user_not_superuser_or_staff
def all_accounts(request):
    template = "company/accounts/users.html"
    query = request.GET.get("q", None)
    users = USER.objects.all()
    if query:
        users = USER.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query) 
            | Q(address_one__icontains = query)
        )
        
    return render(request, "company/accounts/all-users.html", {"accounts": users, "query": query})

@login_required
@user_not_superuser_or_staff
def get_account_detals(request, username):
    model = get_object_or_404(get_user_model().objects.prefetch_related("qualifications", "campaigns", "events", "hobbies").all(), username=username)
    try:
        wallet = WalletModel.objects.get(owner=model)
    except WalletModel.DoesNotExist:
        wallet = WalletModel.objects.create(name=f"{model.username}-wallet", owner=model)

    
    form = WalletStatusUpdateForm(instance = wallet)
    if request.method == "POST":
        form = WalletStatusUpdateForm(instance=wallet, data=request.POST)
        if form.is_valid():
            wallet = form.save(commit=False)
            status = form.cleaned_data.get("status", None)
            if status == "Approved Payout":
                wallet.balance = 0.00
                wallet.save()
                notify_user_of_status_change.delay(user_id=model.id, message=messages_str["approved"])
            elif status == "":
                wallet.save()
                notify_user_of_status_change.delay(user_id=model.id, message=messages_str["Requested Payout Details"])
            else:
                wallet.save()
                notify_user_of_status_change.delay(user_id=model.id, message=messages_str["declined"])
                
            return redirect("company:get-account-details", model.username)
    
    context = {
        "user": model,
        "form": form
    }
   
    return render(request, "company/accounts/user-details.html", context)


@login_required
@user_not_superuser_or_staff
def update_wallet(request, user):
    pass