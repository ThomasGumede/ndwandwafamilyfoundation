from django.urls import path
from payments.views.contribution import contributions_payment_cancelled, contributions_payment_success, contribution_payment, contributions_payment_failed
from payments.views.ticket_order import tickets_payment_cancelled, tickets_payment_failed, tickets_payment_success, payment, resend_tickets
from payments.views.webhook import create_webhook, webhook

app_name = "payments"
urlpatterns = [
    path("webhook/create", create_webhook, name="create_webhook"),
    path("webhook", webhook, name="webhook"),
    path("contributions/payment/<contribution_id>", contribution_payment, name="contribution-payment"),
    path("contributions/payment/cancelled/<contribution_id>", contributions_payment_cancelled, name="contribution-payment-cancelled"),
    path("contributions/payment/failed/<contribution_id>", contributions_payment_failed, name="contribution-payment-failed"),
    path("contributions/payment/success/<contribution_id>", contributions_payment_success, name="contribution-payment-success"),

    path("tickets/payment/<uuid:ticket_order_id>", payment, name="ticket-payment"),
    path("tickets/payment/cancelled/<uuid:ticket_order_id>", tickets_payment_cancelled, name="ticket-payment-cancelled"),
    path("tickets/payment/failed/<uuid:ticket_order_id>", tickets_payment_failed, name="ticket-payment-failed"),
    path("tickets/payment/success/<uuid:ticket_order_id>", tickets_payment_success, name="ticket-payment-success"),
    path("tickets/manage/resend/<uuid:order_uuid>", resend_tickets, name="resend-tickets")
    
]
