import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest
from django.forms import formset_factory
from accounts.utils import StatusChoices
from campaigns.utils import PaymentStatus
from django.contrib.auth.decorators import login_required
from events.models import EventModel, TicketModel, TicketOrderModel, EventTicketTypeModel
from events.forms import TicketOrderForm, TicketForm
from events.tasks import check_ticket_order_payment
from django.contrib import messages
from events.utils import generate_qr_and_bacode, generate_tickets_in_pdf
from django.db.models import Prefetch
from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger("utils")

def update_order_transaction_cost_subtotal(order_id) -> None:
    order = get_object_or_404(TicketOrderModel.objects.prefetch_related("tickets"), id=order_id)
    order.accepted_laws = True
    order.subtotal = sum([ticket.ticket_type.price for ticket in order.tickets.all()])
    order.total_transaction_costs = sum([ticket.ticket_type.transaction_cost for ticket in order.tickets.all()])
    order.save(update_fields=["total_transaction_costs", "subtotal", "accepted_laws"])

def create_order(order_form: TicketOrderForm, request: HttpRequest, event: EventModel) -> TicketOrderModel:
    order = order_form.save(commit=False)
    order.event = event
    order.buyer = request.user
    order.save()

    return order

def validate_tickets_quantity(forms, request: HttpRequest):
    custom_messages = []
    for form in forms:
        quantity = form.cleaned_data["quantity"]
        ticket_type: EventTicketTypeModel = form.cleaned_data["ticket_type"]

        plural = "are" if ticket_type.available_seats > 1 else "is only"
        if quantity > ticket_type.available_seats:
            custom_messages.append(f"Sorry, there {plural} {ticket_type.available_seats} seat available in {ticket_type.title}")
            
    if len(custom_messages) > 0:
        for message in custom_messages:
            messages.error(request, message)
        return False
    else:
        return True
        
    

def create_ticket(forms, order: TicketOrderModel, request: HttpRequest) -> bool:
    for form in forms:
        quantity = form.cleaned_data["quantity"]
        ticket_type: EventTicketTypeModel = form.cleaned_data["ticket_type"]
      
        if quantity > 0:
            for i in range(int(quantity)):
                TicketModel.objects.create(quantity=1, ticket_order=order, ticket_type=ticket_type)

        update_order_transaction_cost_subtotal(order.id)
            
        generated = generate_qr_and_bacode(order, request)
        if not generated:
            logger.error(f"Couldn't generate tickets for {order.order_number}")

    messages.success(request, "Ticket reserved successfully was created successfully")       
    return True

@login_required
def ticket_order(request, order_id, event_slug):
    event = get_object_or_404(EventModel, slug=event_slug, organiser=request.user)
    order_queryset = TicketOrderModel.objects.filter(event=event).prefetch_related("tickets")
    order = get_object_or_404(order_queryset, id=order_id)
    return render(request, "events/orders/order.html", {"order": order})

@login_required
def ticket_orders(request, event_id = None):
    ticketorders = None
    event_model = None
    if event_id:
        event_model = get_object_or_404(EventModel, id=event_id, organiser=request.user)
        ticketorders = TicketOrderModel.objects.filter(event = event)
    else:
        events = EventModel.objects.prefetch_related("ticket_orders").filter(organiser=request.user).order_by("-created")
        
        ticketorders = []
        for event in events:
            ticketorders.extend(event.ticket_orders.all())

    return render(request, "events/orders/orders.html", {"orders": ticketorders, "event": event_model})

@login_required
def create_ticket_order(request, event_slug):
    queryset = EventModel.objects.filter(status = StatusChoices.APPROVED).prefetch_related(Prefetch("tickettypes", queryset=EventTicketTypeModel.objects.filter(available_seats__gte=1)))
    event = get_object_or_404(queryset, slug = event_slug)
    date = event.event_enddate  - timezone.now()

    if date.days <= 0:
        messages.error(request, "Sorry, this event is closed and no longer sells tickets, Thank you")
        event.status = StatusChoices.COMPLETED
        event.save(update_fields=["status"])
        return redirect("events:event-details", event_slug=event.slug)
    
    if event.get_total_seats() == 0 or event.tickettypes.count() == 0:
        messages.info(request, "Sorry this event has ran out of tickets")
        return redirect("events:event-details", event_slug=event.slug)
    
    formset = formset_factory(TicketForm, extra=event.tickettypes.count(), max_num=event.tickettypes.count(), absolute_max=event.tickettypes.count())
    
    if request.method == "POST":
        order_form = TicketOrderForm(request.POST)
        forms = formset(request.POST)
   
        if order_form.is_valid() and forms.is_valid():
            total_reserved_seats = sum([form.cleaned_data["quantity"] for form in forms])
            if total_reserved_seats == 0:
                messages.error(request, "Please select at least one ticket")
                return redirect("events:create-ticket-order", event_slug=event.slug)
            
            valid_tickets_quantity = validate_tickets_quantity(forms, request)
            
            if not valid_tickets_quantity:
                return redirect("events:create-ticket-order", event_slug=event.slug)

            order = create_order(order_form, request, event)
            created = create_ticket(forms, order, request)
            if not created:
                return redirect("events:create-ticket-order", event_slug=event.slug)
            
            check_ticket_order_payment.apply_async((order.id,), countdown=25*60)
            return redirect("events:add-guests", ticket_order_id=order.id)
        else:  
            messages.error(request, f"Something went wrong, please fix error below")
            return render(request, "events/orders/create.html", {"forms": forms, "order_form": order_form, "event": event, "mode": "create"})
        
    forms = formset()
    order_form = TicketOrderForm()
    return render(request, "events/orders/create.html", {"forms": forms, "order_form": order_form, "event": event, "mode": "create"})

@login_required
def add_guest_details(request, ticket_order_id):
    
    ticket_order = get_object_or_404(TicketOrderModel, buyer=request.user, id=ticket_order_id)
    tickets = TicketModel.objects.filter(ticket_order=ticket_order).select_related("ticket_type")
    formset = formset_factory(form=TicketForm, extra=tickets.count(), max_num=tickets.count(), absolute_max=tickets.count(), can_delete=False)

    if request.method == 'POST':
        forms = formset(request.POST)
        
        if forms.is_valid():
            for form, ticket in zip(forms, tickets):
                ticket.guest_full_name = form.cleaned_data["guest_full_name"]
                ticket.guest_email = form.cleaned_data["guest_email"]
                ticket.save(update_fields=["guest_email", "guest_full_name"])

            generated = generate_tickets_in_pdf(ticket_order, request)
            if not generated:
                logger.error(f"Failed to generate tickets for {ticket_order.order_number}")
                
            messages.success(request, "Ticket holders added successfully")
            return redirect("payments:ticket-payment", ticket_order_id=ticket_order.id)
        else:
            messages.error(request, "Please fix errors below")
            return render(request, "events/orders/add_guest_details.html", {"forms": forms, "order": ticket_order, "tickets": tickets, "mode": "guest"})
        
    forms = formset(initial=tickets.values("ticket_type", "quantity"))
    
    return render(request, "events/orders/add_guest_details.html", {"forms": forms, "order": ticket_order, "tickets": tickets, "mode": "guest"})

@login_required
def cancel_ticket_order(request, order_id):
    order = get_object_or_404(TicketOrderModel, buyer=request.user, id=order_id)
    if order.paid == PaymentStatus.PAID or order.paid == PaymentStatus.PENDING:
        messages.error(request, "You cannot delete order that is already paid or pending")
        return redirect("events:manage-ticket-orders")
    
    if request.method == 'POST':
        order.delete()
        messages.success(request, "Ticket order deleted successfully")
        return redirect("events:manage-ticket-orders")
    return render(request, "events/event/delete.html", {"message": f"Are you sure you want to delete this order? {order.order_number}", "title": "Cancel ticket order"})


