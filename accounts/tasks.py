import logging
from celery import shared_task
from django.core.mail import EmailMessage
from accounts.models import CompanyModel
from .models import MailingGroupModel, MailMessageModel
from accounts.utils import custom_send_email
from django.template.loader import render_to_string

task_logger = logging.getLogger("tasks")
accounts_logger = logging.getLogger("accounts")

# COMPANY = CompanyModel.objects.first()

@shared_task
def send_email_to_subscribers(mail_message_id, domain, protocol):
    try:
        mail_message = MailMessageModel.objects.select_related("mailing_group").get(id=mail_message_id)
        message = render_to_string("emails/mailing_update.html", {
            "protocol": protocol,
            "domain": domain,
            "message": mail_message.message,
            
        })

        for subcriber in mail_message.mailing_group.subscribers.all():
            sent = custom_send_email(subcriber.email, mail_message.subject, message)
            if not sent:
                task_logger.error("Failed to send subscribe notification to subscriber")

        return "All subcription emails sent"
    except MailMessageModel.DoesNotExist:
        pass

@shared_task
def send_notification_mail_to_subscribers(mailing_group_id, domain, protocol):
    try:
        mailing_group = MailingGroupModel.objects.prefetch_related("subscribers").get(id=mailing_group_id)
        message = render_to_string("emails/subcriber_notification.html", {
            "protocol": protocol,
            "domain": domain,
            "title": mailing_group.title,
            "describe": mailing_group.description,
            "name": "Contributor/Organisor",
            
        })

        

        for subcriber in mailing_group.subscribers.all():
            sent = custom_send_email(subcriber.email, "Subcription Notification", message)
            if not sent:
                task_logger.error("Failed to send subscribe notification to subscriber")

        return "All subcription emails sent"
    
    except MailingGroupModel.DoesNotExist:
        pass