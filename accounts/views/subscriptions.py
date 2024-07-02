from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from business.models import Business
from accounts.models import SubscriptionPackage
from campaigns.utils import PaymentStatus

def choose_package(request):
    package = SubscriptionPackage.objects.first()
    businesses = Business.objects.count()
    is_price_droped = False
    return_url = request.GET.get("return_url", "/")
    if businesses < 100:
        is_price_droped = True
    if package == None:
        messages.warning(request, "Sorry there are currently no subscription packages")
        return redirect("home:home")
    
    if request.method == "POST":
        package_id = request.POST.get("package_id", None)
        
        request.user.subscription = package
        request.user.save(update_fields=["subscription"])
        if is_price_droped:
            request.user.is_paid = PaymentStatus.PAID
            request.user.save(update_fields=["is_paid"])
            messages.success(request, "You have successfully subscribe to our business listing package")
            return redirect(return_url)
        else:
            # return redirect("payments:subscription", package_id=package.id)
            return redirect(return_url)
    return render(request, "accounts/subscriptions/subscribe.html", {"package": package,"price_drop": is_price_droped})