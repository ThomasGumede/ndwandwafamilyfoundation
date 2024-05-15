from django.urls import path
from events.views.event import create_event, event_details, events, update_event, delete_event
from events.views.order import create_ticket_order, add_guest_details, ticket_order, ticket_orders, cancel_ticket_order
from events.views.ticket_type import create_ticket_types, update_ticket_type, get_event_ticket_types, delete_ticket_type
from events.views.manage import manage_event, manage_events, manage_ticket_order, manage_ticket_orders, generate_guest_list, generate_ticket

app_name = "events"
urlpatterns = [
    path("", events, name="events"),
    path("<slug:category_slug>", events, name="events-by-category"),
    path("event/create", create_event, name="create-event"),
    path("event/details/<slug:event_slug>", event_details, name="event-details"),
    path("event/update/<slug:event_slug>", update_event, name="update-event"),
    path("event/delete/<slug:event_slug>", delete_event, name="delete-event"),
    path("event/manage", manage_events, name="manage-events"),
    path("event/manage/<slug:event_slug>", manage_event, name="manage-event"),

    path("ticket-types/<event_id>", get_event_ticket_types, name="event-ticket-types"),
    path("ticket-types/create/<event_id>", create_ticket_types, name="create-ticket-types"),
    path("ticket-types/update/<slug:event_slug>/<uuid:ticket_type_id>", update_ticket_type, name="update-ticket-type"),
    path("ticket-types/delete/<slug:event_slug>/<uuid:ticket_type_id>", delete_ticket_type, name="delete-ticket-type"),

    path("orders/all", ticket_orders, name="all-ticket-orders"),
    path("orders/all/<event_id>", ticket_orders, name="ticket-orders"),
    path("order/all/<slug:event_slug>/<uuid:order_id>", ticket_order, name="order"),
    path("order/generate/guest/<uuid:event_id>", generate_guest_list, name="generate-guest-list"),
    path("order/create/<slug:event_slug>", create_ticket_order, name="create-ticket-order"),
    path("order/cancel/<uuid:order_id>", cancel_ticket_order, name="cancel-ticket-order"),
    path("order/guest/<uuid:ticket_order_id>", add_guest_details, name="add-guests"),
    path("order/manage", manage_ticket_orders, name="manage-ticket-orders"),
    path("order/manage/<uuid:order_id>", manage_ticket_order, name="manage-ticket-order"),
    path("order/generate/ticket/<uuid:order_id>/<uuid:ticket_id>", generate_ticket, name="generate-ticket")

    
    
]
