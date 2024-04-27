from celery import shared_task
from campaigns.models import CampaignModel, CampaignUpdateModel, ContributionModel
from accounts.utils import StatusChoices, custom_send_email
from django.utils import timezone
from campaigns.utils import PaymentStatus
from accounts.models import CompanyModel
from django.template.loader import render_to_string
from django.db.models import Q
from django.db.models import Prefetch
import logging

task_logger = logging.getLogger("tasks")
campaigns_logger = logging.getLogger("campaigns")

COMPANIES = CompanyModel.objects.all()
COMPANY = None
if COMPANIES.count() > 0:
    COMPANY = COMPANIES[0]

def update_status_email(model_name, model, domain = 'ndwandwa.africa', protocol = 'https'):
    message = render_to_string("global/emails/status_change_email.html", {
        "domain": domain,
        "protocol": protocol,
        "name": model.organiser.get_full_name(),
        "task": f'{model.title} {model_name}',
        "status": f'{model.status}',
        
        "facebook": COMPANY.facebook,
            "twitter": COMPANY.twitter,
            "linkedIn": COMPANY.linkedIn,
            "company_support": COMPANY.phone,
            "company_support_mail": COMPANY.support_email, 
            "company_street_address_1": COMPANY.address_one,
            "company_city": COMPANY.city,
            "company_state": COMPANY.province
    })
    
    sent = custom_send_email(model.organiser.email, f"{model_name} Status update", message)
    return sent

@shared_task
def check_campaigns_status():
    now = timezone.now()
    campaigns = CampaignModel.objects.select_related("organiser").filter(end_date__lte=now)
    
    for campaign in campaigns:
        campaign.status = StatusChoices.COMPLETED
        campaign.save(update_fields=["status"])
        if not update_status_email("campaign", campaign):
            task_logger.error(f"Failed to send campaign status update - id {campaign.id}")


    return f"{campaigns.count()} were marked at completed"

@shared_task
def notify_organiser_of_status_change(campaign_id, domain = 'ndwandwa.africa', protocol = 'https'):
    try:
        
        campaign = CampaignModel.objects.select_related("organiser").get(id=campaign_id)
        if not update_status_email("campaign", campaign, domain, protocol):
            task_logger.error(f"Failed to send campaign status update - id {campaign.id}")

        return "Done"
    
    except CampaignModel.DoesNotExist:
        pass

def send_campaign_created_email(campaign_id, domain, protocol):
    try:
        
        campaign = CampaignModel.objects.select_related("organiser").get(id=campaign_id)
        return f"Campaign created confirmation email was sent because campaign id={campaign.title} was created"
    
    except CampaignModel.DoesNotExist:
        return f"Campaign created confirmation email was not sent because campaign id={campaign_id} was not found"

@shared_task
def update_contributors(update_id, domain, protocol):
    try:
        update = CampaignUpdateModel.objects.get(id = update_id)
        contributions=ContributionModel.objects.filter(Q(paid=PaymentStatus.PAID) | Q(paid=PaymentStatus.PENDING))
        campaign = CampaignModel.objects.prefetch_related(Prefetch("contributions", queryset=contributions)).get(id=update.campaign.id)
        update_mail = render_to_string("mails/update.html", {
            "update": update,
            "protocol": protocol,
            "domain": domain,
            "name": "Contributor/Organisor",
            "facebook": COMPANY.facebook,
            "twitter": COMPANY.twitter,
            "linkedIn": COMPANY.linkedIn,
            "company_support": COMPANY.phone,
            "company_support_mail": COMPANY.support_email, 
            "company_street_address_1": COMPANY.address_one,
            "company_city": COMPANY.city,
            "company_state": COMPANY.province
        })
        for contribution in campaign.contributions.all():
            email = contribution.contributor.email
            sent = custom_send_email(email, "Campaign update", update_mail)
            if not sent:
                task_logger.error("Update email no sent")
                
        
        return True

    except CampaignModel.DoesNotExist:
        task_logger.error(f"campaign update {update_id} was not found")

    except CampaignModel.DoesNotExist:
        campaigns_logger.error(f"Campaign was not found when trying to send update")