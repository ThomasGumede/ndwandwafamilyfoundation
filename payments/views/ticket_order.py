import requests, logging, json
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from events.models import TicketOrderModel
from campaigns.utils import PaymentStatus
from payments.models import PaymentInformation
from django.contrib import messages
from payments.utils import headers, decimal_to_str, update_payment_status_ticket_order
from django.contrib.auth.decorators import login_required
from payments.tasks import resend_tickets_task, check_payment_update_ticket_order
from django.contrib.sites.shortcuts import get_current_site

logger = logging.getLogger("payments")

@login_required
def payment(request, ticket_order_id):
    ticket_orders_queryset = TicketOrderModel.objects.filter(paid = PaymentStatus.NOT_PAID, buyer=request.user)
    ticket_order = get_object_or_404(ticket_orders_queryset, buyer=request.user, id=ticket_order_id)
    
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse("payments:ticket-payment-success", kwargs={"ticket_order_id": ticket_order.id}))
        cancel_url = request.build_absolute_uri(reverse("payments:ticket-payment-cancelled", kwargs={"ticket_order_id": ticket_order.id}))
        fail_url = request.build_absolute_uri(reverse("payments:ticket-payment-failed", kwargs={"ticket_order_id": ticket_order.id}))
        str_amount = decimal_to_str(ticket_order.total_price)
        
        lineitems = []
        for ticket in ticket_order.tickets.all():
            lineitems.append(
                {
                    "displayName": ticket.ticket_type.title,
                    "quantity": ticket.quantity,
                    "pricingDetails": {
                        "price": int(decimal_to_str(ticket.ticket_type.price))
                    }
                }
            )

        session_data = {
            'successUrl': success_url,
            'cancelUrl': cancel_url,
            "failureUrl": fail_url,
            'amount': int(str_amount),
            'currency': 'ZAR',
            'metadata': {
                "checkoutId": f"{ticket_order.order_number}"
            },
            "lineItems": lineitems

        }
        data = json.dumps(session_data)
        try:
            response = requests.request("POST", "https://payments.yoco.com/api/checkouts", data=data, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            ticket_order.checkout_id = response_data["id"]
            ticket_order.paid = PaymentStatus.PENDING
            ticket_order.save(update_fields=["paid", "checkout_id"])
            return redirect(response_data["redirectUrl"])

        except requests.ConnectionError as err:
            return render(request, "payments/timeout.html", {"err": err})
        
        except requests.HTTPError as err:
            logger.error(f"Yoco - {err}")
            return render(request, "payments/error.html", {"message": "Your payment was not processed due to internal error from our payment system, Please try again later"})
        
        except Exception as err:
            logger.error(f"Yoco - {err}")
            return render(request, "payments/error.html", {"message": "Your payment was not processed due to internal error from our payment system, Please try again later"})

    return render(request, "payments/tickets/payment.html", {"ticketorder": ticket_order, "mode": "payment"})


def tickets_payment_success(request, ticket_order_id):
    domain = get_current_site(request).domain
    protocol = "https" if request.is_secure() else "http"
    ticket_order = get_object_or_404(TicketOrderModel, id=ticket_order_id)
    if ticket_order.paid == PaymentStatus.PENDING:
        try:
            payment_information = PaymentInformation.objects.get(id = ticket_order.checkout_id)
            updated = update_payment_status_ticket_order(json.loads(payment_information.data), request, ticket_order)

            if updated:
                payment_information.order_number = ticket_order.order_number
                payment_information.order_updated = True
                payment_information.save(update_fields=["order_number", "order_updated"])
            else:
                check_payment_update_ticket_order.apply_async((ticket_order.checkout_id, protocol, domain), countdown=25*60)

        except PaymentInformation.DoesNotExist:
            check_payment_update_ticket_order.apply_async((ticket_order.checkout_id, protocol, domain), countdown=25*60)
    else:
        pass
    
    return render(request, "payments/tickets/success.html", {"ticketorder": ticket_order})

def tickets_payment_cancelled(request, ticket_order_id):
    ticket_order = get_object_or_404(TicketOrderModel, id=ticket_order_id)
    ticket_order.delete()
    return render(request, "payments/tickets/cancelled.html")

def tickets_payment_failed(request, ticket_order_id):
    ticket_order = get_object_or_404(TicketOrderModel, id=ticket_order_id)

    try:
        payment_information = PaymentInformation.objects.get(id = ticket_order.checkout_id)
        payment_information.order_number = ticket_order.order_number
        payment_information.save(update_fields=["order_number"])
        updated = update_payment_status_ticket_order(json.loads(payment_information.data), request, ticket_order)
        
        if updated:
            print("done")
        else:
            print("Not done")

    except PaymentInformation.DoesNotExist:
        pass

    return render(request, "payments/tickets/failed.html")

def resend_tickets(request, order_uuid):
    order = get_object_or_404(TicketOrderModel, id=order_uuid, buyer=request.user)
    if order.paid == PaymentStatus.NOT_PAID:
        messages.error(request, "You have not paid for your tickets, if you did pay for them, please contact us <b>support@ndwandwafam.co.za</b>")
        return redirect("events:manage-ticket-order", id=order_uuid)
    
    protocol = "https" if request.is_secure() else "http"
    domain = get_current_site(request).domain
    resend_tickets_task.delay(order.checkout_id, protocol, domain)
    messages.success(request, "Your tickets were successfully sent, if you don't receive them, please contact us <b>support@ndwandwafam.co.za</b>")
    return redirect("events:manage-ticket-order", order_id=order.id)

