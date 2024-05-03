from django.contrib import admin
from campaigns.tasks import notify_organiser_of_status_change
from django.contrib.sites.shortcuts import get_current_site
from campaigns.models import CampaignModel, ContributionModel, CampaignUpdateModel

# Actions
@admin.action(description="Approve selected campaigns")
def make_approve(modeladmin, request, querset):
    querset.update(status="APPROVED")
    for campaign in querset:
        notify_organiser_of_status_change.delay(campaign.id)

@admin.action(description="Pending selected campaigns")
def make_pending(modeladmin, request, querset):
    querset.update(status="PENDING")
    for campaign in querset:
        notify_organiser_of_status_change.delay(campaign.id)


class ContributionInline(admin.TabularInline):
    model = ContributionModel
    exclude = ("amount", "tip", "accepted_laws", "message", "payment_method_type", "receipt","payment_method_card_holder", "payment_method_masked_card", "payment_method_scheme", "payment_date")
    readonly_fields = ("order_number", "checkout_id", "total_amount", "contributor", "paid", "created")
    extra = 0
    empty_value_display = "Empty"

class CampaignUpdateInline(admin.TabularInline):
    model = CampaignUpdateModel
    readonly_fields = ("title", "content", "created")
    extra = 0
    empty_value_display = "Empty"

@admin.register(CampaignModel)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("thumpnail","title", "category","target", "current_amount","get_days", "status")
    list_editable = ("status", )
    exclude = ("slug", "image", "details", "tags")
    readonly_fields = ("title", "category", "content_safe", "image_tag","target", "start_date", "end_date", "organiser", "created", "updated")
    date_hierarchy = "created"
    empty_value_display = "Empty"
    actions = [make_approve, make_pending]
    search_fields = ("title",)
    inlines = [ContributionInline, CampaignUpdateInline]

    def save_model(self, request, obj, form, change):

        obj.save()
        if change:
            protocol = "https" if request.is_secure() else "http"
            domain = get_current_site(request).domain
            notify_organiser_of_status_change.delay(obj.id, domain, protocol)

@admin.register(ContributionModel)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ("order_number", "checkout_id", "total_amount", "contributor", "paid", "payment_date", "created")
    list_editable = ("paid", )
    search_fields = ("order_number", "checkout_id", "payment_date")
    readonly_fields = ("order_number", "checkout_id",  "amount", "tip", "total_amount", "contributor", "anonymous", "campaign", "accepted_laws", "message", "payment_method_type", "payment_method_card_holder", "payment_method_masked_card", "payment_method_scheme", "payment_date", "created")
    extra = 0
    empty_value_display = "Empty"

@admin.register(CampaignUpdateModel)
class CampaignUpdateAdmin(admin.ModelAdmin):
    pass






