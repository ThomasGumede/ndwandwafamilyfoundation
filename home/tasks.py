from celery import shared_task
from django.core.mail import EmailMessage
from accounts.utils import custom_send_email
import logging

logger = logging.getLogger("tasks")
email_logger = logging.getLogger("emails")

# def send_mail_to_campaign(campaigns):
#     try:
#         group = MailingGroupModel.objects.get(slug="campaigns-update")
#         email_subject = f"{campaigns[0].title} by {campaigns[0].organiser.get_full_name()}"
#         message = render_to_string("emails/email_updates.html",
#             {
                
#                 "campaigns": campaigns,
#                 "company_support_number": "+276513461134",
#                 "company_email_address": "ndwandwafam@gmail.com",
#                 "company_support_email": "support@ndwandwa.com",
#             },
#         )
#         try:
#             for subscriber in group.subscribers.all():
#                 email = EmailMessage(email_subject, message, "NdwandwaFam Daily Digest <noreply@ndwandwafam.co.za>", to=[subscriber.email])
#                 email.content_subtype = 'html'
                
#                 if not email.send():
#                     logger.error(f"Failed to send email to {subscriber.get_full_name()}")
                
                
#         except Exception as ex:
#             logger.error(ex)
            
#     except MailingGroupModel.DoesNotExist:
#         pass

# def send_mail_to_news(news):
#     try:
#         group = MailingGroupModel.objects.get(slug="news-update")
#         email_subject = f"{news[0].title} by {news[0].organiser.get_full_name()}"
#         message = render_to_string("emails/news_updates_email.html",
#             {
                
#                 "posts": news,
#                 "company_support_number": "+276513461134",
#                 "company_email_address": "ndwandwafam@gmail.com",
#                 "company_support_email": "support@ndwandwa.com",
#             },
#         )
#         try:
#             for subscriber in group.subscribers.all():
#                 email = EmailMessage(email_subject, message, "NdwandwaFam Daily Digest <noreply@ndwandwafam.co.za>", to=[subscriber.email])
#                 email.content_subtype = 'html'
                
#                 if not email.send():
#                     logger.error(f"Failed to send email to {subscriber.get_full_name()}")
                
                
#         except Exception as ex:
#             logger.error(ex)
            
#     except MailingGroupModel.DoesNotExist:
#         pass

# def send_mail_to_event(events):
#     try:
#         group = MailingGroupModel.objects.get(slug="events-update")
#         email_subject = f"{events[0].title} by {events[0].organiser.get_full_name()}"
#         message = render_to_string("emails/events_update_email.html",
#             {
                
#                 "events": events,
#                 "company_support_number": "+276513461134",
#                 "company_email_address": "ndwandwafam@gmail.com",
#                 "company_support_email": "support@ndwandwa.com",
#             },
#         )
#         try:
#             for subscriber in group.subscribers.all():
#                 email = EmailMessage(email_subject, message, "NdwandwaFam Daily Digest <noreply@ndwandwafam.co.za>", to=[subscriber.email])
#                 email.content_subtype = 'html'
                
#                 if not email.send():
#                     logger.error(f"Failed to send email to {subscriber.get_full_name()}")
                
                
#         except Exception as ex:
#             logger.error(ex)
            
#     except MailingGroupModel.DoesNotExist:
#         pass

@shared_task
def send_email_to_admin(subject, message, from_email, name):
    try:
        email = custom_send_email("thomasgumede12@gmail.com", subject, message)
        if not email.send():
            return f"Email not sent from {from_email}"
        else:
            return "Email sent"
    except Exception as ex:
        logger.error(ex)

# @shared_task
# def send_update_email():
#     try:
#         campaigns = CampaignModel.objects.all().order_by("-created")[:5]
#         events = EventModel.objects.all().order_by("-created")[:5]
#         posts = PostModel.objects.all().order_by("-created")[:5]
        
#         if campaigns.count() > 2:
#             send_mail_to_campaign(campaigns)

#         if events.count() > 2:
#             send_mail_to_event(events)
        
#         if posts.count() > 2:
#             send_mail_to_news(posts)

#         return "emails update sent"
    
#     except Exception as ex:
#         logger.error(ex)