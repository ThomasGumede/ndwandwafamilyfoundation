from django.contrib import admin
from accounts.models import CompanyModel, SubscriptionPackage, CustomUserModel, MailMessageModel, QualificationModel, RelativeModel, MailingGroupModel, IdentityVerificationModel, WalletModel, SubscribeModel
from events.models import EventModel
from campaigns.models import CampaignModel
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from accounts.tasks import send_notification_mail_to_subscribers, send_email_to_subscribers

@admin.register(SubscriptionPackage)
class SubscriptionPackageAdmin(admin.ModelAdmin):
    pass


class EventInline(admin.TabularInline):
    model = EventModel
    exclude = ("image", "content", "slug", "allocated_seats", "unallocated_seats")
    readonly_fields = ("title", "tip","category", "event_startdate", "event_enddate", "total_seats_sold", "venue_name", "event_address", "event_link")
    extra = 0

@admin.action(description="Payout the selected wallets")
def clear_wallet(modeladmin, request, querset):
    querset.update(balance=0.00, status="Approved Payout", cleared_date=timezone.now())

class WalletInline(admin.TabularInline):
    model = WalletModel
    readonly_fields = ("name", "balance", "created", "cleared_date")

@admin.register(CompanyModel)
class CompanyAdmin(admin.ModelAdmin):
    pass

class CampaignInline(admin.TabularInline):
    model = CampaignModel
    exclude = ("slug", "image", "details", "tags")
    readonly_fields = ("title", "category", "target", "current_amount", "start_date", "end_date", "created")
    extra = 0

class QualificationInline(admin.TabularInline):
    model = QualificationModel
    readonly_fields =("title", "institution", "qualification_type", "year")
    empty_value_display = "Empty"
    extra = 0


class RelativeInline(admin.TabularInline):
    model = RelativeModel
    exclude = ('description',)
    readonly_fields =('title', 'surname', 'full_name', 'relationship', 'phone', 'gender', 'relative_side', 'maiden_name')
    empty_value_display = "Empty"
    
    extra = 0

class IdentityVerificationInline(admin.TabularInline):
    model = IdentityVerificationModel
    readonly_fields = ("user", "identity_image", "identitybook_image")
    extra = 0

class SubscribeInline(admin.TabularInline):
    model = SubscribeModel
    extra = 0

@admin.register(MailMessageModel)
class MailMessageAdmin(admin.ModelAdmin):
    pass

    def save_model(self, request, obj, form, change):

        obj.save()
        if not change:
            protocol = "https" if request.is_secure() else "http"
            domain = get_current_site(request).domain
            send_email_to_subscribers.delay(obj.id, domain, protocol)

@admin.register(WalletModel)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "balance", "cleared_date")
    readonly_fields = ("name", "owner", "created", "balance", "cleared_date")
    actions = [clear_wallet]

@admin.register(CustomUserModel)
class CustomUserAdmin(admin.ModelAdmin):
    list_display =("username", "first_name", "last_name", "phone", "verification_status")
    exclude = ("password", "profile_image", "maiden_name", "address_one", "address_two", "groups", "user_permissions","city", "country", "facebook", "twitter", "instagram", "address_id", "linkedIn","province", "zipcode", "hobbies","first_name", "last_name", "email", "phone", "biography", "identity_number", "identity_choice", "occupation", "professional_affiliations")
    readonly_fields = ("image_tag", "title", "username", "full_names", "contact_details", "identity_information", "address", "employment_details", "last_login", "date_joined")
    empty_value_display = "Empty"
    inlines = [WalletInline, IdentityVerificationInline, QualificationInline, RelativeInline, CampaignInline, EventInline]

@admin.register(MailingGroupModel)
class MailingGroupAdmin(admin.ModelAdmin):
    list_display = ("title",)
    prepopulated_fields = {"slug": ["title"]}
    inlines = [SubscribeInline]

    def save_model(self, request, obj, form, change):

        obj.save()
        if not change:
            protocol = "https" if request.is_secure() else "http"
            domain = get_current_site(request).domain
            send_notification_mail_to_subscribers.delay(obj.id, domain, protocol)

        