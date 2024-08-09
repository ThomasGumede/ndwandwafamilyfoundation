from django.urls import path

from company.views.accounts import all_accounts, get_account_detals
from company.views.blogs import all_blogs
from company.views.campaigns import all_campaigns, campaign_details
from company.views.contributions import all_contributions, delete_contribution, contribution_details
from company.views.events import all_events, event_details
from company.views.home import earnings, view_order
from company.views.ticket_orders import all_ticket_orders, ticket_order_details, delete_ticket_order


app_name = "company"
urlpatterns = [
    path("", earnings, name="earnings"),
    path("earning/<order_uuid>", view_order, name="view-earning"),
    path("accounts", all_accounts, name="all-accounts"),
    path("accounts/<username>", get_account_detals, name="get-account-details"),
    path("campaigns", all_campaigns, name="all-campaigns"),
    path("campaign/<slug:campaign_slug>", campaign_details, name="campaign-details"),
    path("accounts/campaigns/<username>", all_campaigns, name="all-campaigns-by-username"),
    path("events", all_events, name="all-events"),
    path("event/<slug:event_slug>", event_details, name="event-details"),
    path("accounts/events/<username>", all_events, name="all-events-by-username"),
    path("contributions", all_contributions, name="all-contributions"),
    path("contributions/<contribution_id>", contribution_details, name="contribution"),
    path("contribution/delete/<uuid:contribution_id>", delete_contribution, name="delete-contribution"),
    path("ticket-orders", all_ticket_orders, name="all-ticket-orders"),
    path("ticket-orders/<order_id>", ticket_order_details, name="order"),
    path("ticket-orders/delete/<uuid:order_id>", delete_ticket_order, name="cancel-ticket-order"),
    path("blogs", all_blogs, name="all-blogs"),
]