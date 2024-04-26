from django.urls import path 
from campaigns.views.campaign import (campaigns, campaign_details, 
                                      create_campaign, update_campaign, delete_campaign, manage_campaigns, manage_campaign, generate_contributors_list)
from campaigns.views.contribution import (
    create_contribution, cancel_contribution, contribution, contributions, manage_contribution, manage_contributions
)
from campaigns.views.campaign_update import create_campaign_update, delete_campaign_update

app_name = "campaigns"
urlpatterns = [
    path("", campaigns, name="campaigns"),
    path("campaign/manage", manage_campaigns, name="manage-campaigns"),
    path("campaign/create", create_campaign, name="create-campaign"),
    path("<slug:category_slug>", campaigns, name="campaign-by-category"),
    path("campaing/<slug:campaign_slug>", campaign_details, name="campaign"),
    path("campaign/manage/<uuid:campaign_id>", manage_campaign, name="manage-campaign"),
    path("campaign/update/<slug:campaign_slug>", update_campaign, name="update-campaign"),
    path("campaign/delete/<slug:campaign_slug>", delete_campaign, name="delete-campaign"),

    path("campaign/updates/create/<slug:campaign_slug>", create_campaign_update, name="create-campaign-update"),
    path("campaign/updates/delete/<uuid:update_id>", delete_campaign_update, name="delete-campaign-update"),

    path("contributions/all", contributions, name="all-contributions"),
    path("contribution/all/<uuid:campaign_id>", contributions, name="contributions"),
    path("contribution/manage", manage_contributions, name="manage-contributions"),
    path("contribution/<uuid:campaign_id>/<uuid:contribution_id>", contribution, name="contribution"),
    path("contribution/manage/<uuid:contribution_id>", manage_contribution, name="manage-contribution"),
    path("contribution/create/<uuid:campaign_id>", create_contribution, name="create-contribution"),
    path("contribution/cancel/<uuid:contribution_id>", cancel_contribution, name="cancel-contribution"),
    path("contribution/generate/contributors/<uuid:campaign_id>", generate_contributors_list, name="generate-contributors-list")
    
]
