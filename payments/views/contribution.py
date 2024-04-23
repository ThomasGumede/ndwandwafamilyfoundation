import json, logging
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from campaigns.models import ContributionModel
from payments.models import PaymentInformation
from payments.tasks import check_payment_update_contribution
from django.contrib import messages
from campaigns.utils import PaymentStatus
from payments.utils import headers, decimal_to_str, update_payment_status_contribution_order
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site

logger = logging.getLogger("payments")

@login_required
def contribution_payment(request, contribution_id):
    
    contributions_queryset = ContributionModel.objects.filter(contributor=request.user, paid=PaymentStatus.NOT_PAID)
    contribution = get_object_or_404(contributions_queryset, id=contribution_id)
    
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse("payments:contribution-payment-success", kwargs={"contribution_id": contribution.id}))
        cancel_url = request.build_absolute_uri(reverse("payments:contribution-payment-cancelled", kwargs={"contribution_id": contribution.id}))
        fail_url = request.build_absolute_uri(reverse("payments:contribution-payment-failed", kwargs={"contribution_id": contribution.id}))
        str_amount = decimal_to_str(contribution.total_amount)

        session_data = {
            'successUrl': success_url,
            'cancelUrl': cancel_url,
            "failureUrl": fail_url,
            'amount': int(str_amount),
            'currency': 'ZAR',
            'metadata': {
                "checkoutId": f"{contribution.order_number}"
            },
        }

        data = json.dumps(session_data)
        try:
            response = requests.request("POST", "https://payments.yoco.com/api/checkouts", data=data, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            contribution.checkout_id = response_data["id"]
            contribution.paid = PaymentStatus.PENDING
            contribution.save(update_fields=["paid", "checkout_id"])
            return redirect(response_data["redirectUrl"])

        except requests.ConnectionError as err:
            return render(request, "payments/timeout.html", {"err": err})
        
        except requests.HTTPError as err:
            logger.error(f"Yoco - {err}")
            return render(request, "payments/error.html", {"message": "Your payment was not processed due to internal error from our payment system, Please try again later"})
        
        except Exception as err:
            logger.error(f"Yoco - {err}")
            return render(request, "payments/error.html", {"message": "Your payment was not processed due to internal error from our payment system, Please try again later"})

    return render(request, "payments/contributions/payment.html", {"donation": contribution})


def contributions_payment_failed(request, contribution_id):
    contribution = get_object_or_404(ContributionModel, id=contribution_id)
    contribution.paid = PaymentStatus.NOT_PAID
    contribution.save(update_fields=["paid"])
    return render(request, "payments/contributions/failed.html")


def contributions_payment_cancelled(request, contribution_id):
    contribution = get_object_or_404(ContributionModel, id=contribution_id)
    contribution.delete()
    return render(request, "payments/contributions/cancelled.html")


def contributions_payment_success(request, contribution_id):
    domain = get_current_site(request).domain
    protocol = "https" if request.is_secure() else "http"
    
    contribution = get_object_or_404(ContributionModel, id=contribution_id)
    try:
        payment_information = PaymentInformation.objects.get(id = contribution.checkout_id)
        updated = update_payment_status_contribution_order(json.loads(payment_information.data), request, contribution)

        if updated:
            payment_information.order_number = contribution.order_number
            payment_information.order_updated = True
            payment_information.save(update_fields=["order_number", "order_updated"])

        else:
            check_payment_update_contribution.apply_async((contribution.checkout_id, domain, protocol), countdown=25*60)

    except PaymentInformation.DoesNotExist:
        check_payment_update_contribution.apply_async((contribution.checkout_id, protocol, domain), countdown=25*60)

    return render(request, "payments/contributions/success.html", {"contribution": contribution})