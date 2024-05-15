import logging
from django.shortcuts import render, get_object_or_404, redirect
from company.decorators import user_not_superuser_or_staff
from accounts.utils import StatusChoices
from campaigns.utils import PaymentStatus
from django.contrib.auth.decorators import login_required
from events.models import EventModel, TicketModel, TicketOrderModel, EventTicketTypeModel
from django.contrib import messages
from django.db.models import Prefetch
from django.utils import timezone
from django.db.models import Q

@login_required
@user_not_superuser_or_staff
def all_ticket_orders(request, event_id = None):
    ticketorders = TicketOrderModel.objects.all()
    event_model = None
    if event_id:
        event_model = get_object_or_404(EventModel, id=event_id)
        ticketorders = TicketOrderModel.objects.filter(event = event_model)
    

    return render(request, "company/orders/orders.html", {"orders": ticketorders, "event": event_model})

@login_required
@user_not_superuser_or_staff
def ticket_order_details(request, order_id):
    order_queryset = TicketOrderModel.objects.select_related("event").prefetch_related("tickets")
    order = get_object_or_404(order_queryset, id=order_id)
    return render(request, "company/orders/details.html", {"order": order})

@login_required
def delete_ticket_order(request, order_id):
    order = get_object_or_404(TicketOrderModel, id=order_id)
    if order.paid == PaymentStatus.PAID:
        messages.error(request, "You cannot delete order that is already paid")
        return redirect("company:all-ticket-orders")
    
    if request.method == 'POST':
        order.delete()
        messages.success(request, "Ticket order deleted successfully")
        return redirect("company:all-ticket-orders")
    return render(request, "events/event/delete.html", {"message": f"Are you sure you want to delete this order? {order.order_number}", "title": "Cancel ticket order"})

