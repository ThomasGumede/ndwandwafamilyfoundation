from django.shortcuts import render, get_object_or_404, redirect
from django.forms import formset_factory
from django.core import serializers
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from events.models import EventModel, EventTicketTypeModel, TicketModel
from events.forms import EventTicketTypeForm, EventTicketTypeUpdateForm
from django.contrib import messages
from django.utils import timezone

@login_required
def get_event_ticket_types(request, event_id):
    try:
        event = EventModel.objects.get(id=event_id)
        event_ticket_types = EventTicketTypeModel.objects.filter(event = event, available_seats__gte=1)

        json_event_ticket_types = serializers.serialize("json", event_ticket_types)
        return JsonResponse({"success": True, "event_ticket_types": json_event_ticket_types}, status=200)
    except EventModel.DoesNotExist:
        return JsonResponse({"success": False, "event_ticket_types": "Event does not exists"}, status=200)


@login_required
def create_ticket_types(request, event_id):
    event = get_object_or_404(EventModel, organiser = request.user, id = event_id)
    max_forms =  5 if event.tickettypes.count() == 0 else 5 - event.tickettypes.count()
    
    if event.tickettypes.count() == 5:
        messages.error(request, "Cannot add another ticket type, it either you already have 5 tickets or there are no tickets available to allocate")
        return redirect("events:manage-events")
    
    if request.method == 'POST':
        
        form = EventTicketTypeForm(request.POST)

        if form.is_valid():
            add_another = form.cleaned_data.get("add_another", None)
            title = form.cleaned_data.get("title", None)
            ticket_type = form.save(commit=False)
            ticket_type.event = event
            ticket_type.save()
            messages.success(request, f"Your Ticket type({title}) we successfully created")
            if add_another:
                return redirect("events:create-ticket-types", event_id=event.id)
            
            return redirect("events:manage-event", event_slug=event.slug)
        else:
            messages.error(request, "Something is missing, please fix errors below")
            return render(request, "events/ticket/create_tickets_type.html", {"form": form, "event": event, "max_forms": max_forms})
    else:    
        
        form = EventTicketTypeForm()
        return render(request, "events/ticket/create_tickets_type.html", {"form": form, "event": event, "max_forms": max_forms})
    
@login_required
def update_ticket_type(request, event_slug, ticket_type_id):
    event = get_object_or_404(EventModel, organiser = request.user, slug = event_slug)
    ticket = get_object_or_404(EventTicketTypeModel, event=event, id=ticket_type_id)
    
    if request.method == 'POST':
        form = EventTicketTypeUpdateForm(instance=ticket, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Ticket type {ticket.title} was updated successfully")
            return redirect("events:manage-event", event_slug=event.slug)
        else:
            messages.error(request, f"Ticket type {ticket.title} was not updated successfully. Fix errors below")
            return render(request, "events/ticket/update.html", {"form": form, "event": event })

    form = EventTicketTypeUpdateForm(instance=ticket)
    return render(request, "events/ticket/update.html", {"form": form, "event": event })

@login_required
def delete_ticket_type(request, event_slug, ticket_type_id):
    event = get_object_or_404(EventModel, organiser = request.user, slug = event_slug)
    
    ticket = get_object_or_404(EventTicketTypeModel, event=event, id=ticket_type_id)
    tickets = TicketModel.objects.filter(ticket_type=ticket)
    if tickets.count() > 0:
        messages.error(request, f"You cannot delete this ticket type because {tickets.count()} people have already paid for it")
        return redirect("events:manage-event", event_slug=event.slug)
    
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, "Ticket order deleted successfully")
        return redirect("events:manage-event", event_slug=event.slug)
    return render(request, "events/event/delete.html", {"message": f"Are you sure you want to delete this ticket type? {ticket.title}", "title": "Delete ticket type"})

