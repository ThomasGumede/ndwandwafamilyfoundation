from celery import shared_task
from django.contrib.auth import get_user_model
from accounts.utils import custom_send_email
from accounts.models import CompanyModel
from django.template.loader import render_to_string
import logging

task_logger = logging.getLogger("tasks")
campaigns_logger = logging.getLogger("campaigns")

COMPANY = CompanyModel.objects.first()

def update_status_email(user, content, domain = 'ndwandwa.africa', protocol = 'https'):
    message = render_to_string("company/emails/wallet_update.html", {
        "domain": domain,
        "protocol": protocol,
        "name": f"{user.title} {user.get_full_name()}",
        "message": content,
        
        "facebook": COMPANY.facebook if COMPANY else '',
            "twitter": COMPANY.twitter if COMPANY else '',
            "linkedIn": COMPANY.linkedIn if COMPANY else '',
            "company_support": COMPANY.phone if COMPANY else '',
            "company_support_mail": COMPANY.support_email if COMPANY else '', 
            "company_street_address_1": COMPANY.address_one if COMPANY else '',
            "company_city": COMPANY.city if COMPANY else '',
            "company_state": COMPANY.province if COMPANY else ''
    })
    
    sent = custom_send_email(user.email, f"Wallet Status update", message)
    return sent

@shared_task
def notify_user_of_status_change(user_id, message, domain = 'ndwandwa.africa', protocol = 'https'):
    try:
        
        user = get_user_model().objects.get(id = user_id)
        if not update_status_email(user, message, domain, protocol):
            task_logger.error(f"Failed to send wallet status update - id {user.my_wallet.id}")

        return "Done"
    
    except Exception as ex:
        task_logger.error(f"{user.my_wallet.id} - {ex}")