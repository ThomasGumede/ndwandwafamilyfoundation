from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from events.models import EventModel
from campaigns.utils import generate_slug, PaymentStatus
from events.forms import EventForm
from django.contrib import messages
from django.db.models import Q
from accounts.utils import StatusChoices
from home.models import CategoryModel

def events(request, category_slug=None):
    query = request.GET.get("query", None)
    queryset = EventModel.objects.filter(Q(status = StatusChoices.APPROVED) | Q(status = StatusChoices.COMPLETED))
    if category_slug:
        category = get_object_or_404(CategoryModel, slug=category_slug)
        if query:
            events = queryset.filter(Q(category = category) & Q(title__icontains=query)| Q(organiser__first_name__icontains=query))
        else:
            events = queryset.filter(category = category)
    else:
        if query:
            events = queryset.filter(Q(title__icontains=query)| Q(organiser__first_name__icontains=query))
        else:
            events = queryset

    return render(request, "events/event/list.html", {"events": events, "query": query})

def event_details(request, event_slug):
    queryset = EventModel.objects.all().select_related("organiser")
    event = get_object_or_404(queryset, slug = event_slug)
    recent_events = EventModel.objects.filter(Q(status = StatusChoices.APPROVED) | Q(status = StatusChoices.COMPLETED)).order_by("-created")[:6]
    return render(request, "events/event/details.html", {"event": event, "recent_events": recent_events})

@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid() and form.is_multipart():
            event = form.save(commit=False)
            event.organiser = request.user
            event.slug = generate_slug(form.cleaned_data["title"], EventModel)
            event.save()
            messages.success(request, "Event was added successfully")
            return redirect("events:create-ticket-types", event_id=event.id)
        else:
            
            messages.error(request, "Please fix below errors")
            return render(request, "events/event/create.html", {"form": form })
    form = EventForm()
    return render(request, "events/event/create.html", {"form": form })

@login_required
def update_event(request, event_slug):
    event = get_object_or_404(EventModel, organiser = request.user, slug = event_slug)
    if request.method == "POST":
        form = EventForm(instance=event, data=request.POST, files=request.FILES)
        if form.is_valid() and form.is_multipart():
            
            event = form.save(commit=False)
            event.save()
            messages.success(request, "Event was updated successfully")
            return redirect("events:manage-events")
        else:
            messages.error(request, "Please fix below errors")
            return render(request, "events/event/update.html", {"form": form })
        
    form = EventForm(instance=event)
    return render(request, "events/event/update.html", {"form": form })

@login_required
def delete_event(request, event_slug):
    event = get_object_or_404(EventModel.objects.prefetch_related("ticket_orders"), organiser = request.user, slug = event_slug)

    if event.total_seats_sold / event.get_total_seats() == 0.25 or event.ticket_orders.filter(Q(paid = PaymentStatus.PENDING)| Q(paid = PaymentStatus.PAID)).count() > 0:
        messages.warning(request, "Because of our no refund policy, You cannot delete an event that has pending or paid tickets orders!")
        return redirect("events:manage-events")
    if request.method == "POST":
        event.delete()
        
        messages.success(request, "Event deleted successfully")
        return redirect("events:manage-events")
    return render(request, "events/event/delete.html", {"message": f"Are you sure you want to delete this event ({event.title})?", "title": "Delete event"})
