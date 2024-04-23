import hashlib
import base64
import hmac, logging
from events.models import TicketOrderModel, reservation_time
from campaigns.models import ContributionModel, in_fourteen_days
from accounts.models import WalletModel
from accounts.utils import send_html_email_with_attachments
from campaigns.utils import PaymentStatus
from events.models import TicketOrderModel
from django.conf import settings
from io import BytesIO
from django.template.loader import render_to_string
from django.template.loader import get_template
from weasyprint import HTML


from payments.models import NdwandwaBankModel

logger = logging.getLogger("payments")
email_logger = logging.getLogger("emails")
key = settings.YOCO_API_KEY

headers= { "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

def generate_expected_signature(signed_content, secret):
    secret_bytes = base64.b64decode(secret.split('_')[1])
    hmac_signature = hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    expected_signature = base64.b64encode(hmac_signature).decode()

    return expected_signature

def decimal_to_str(dec_value):
    # Returns a decimal to string and removes a comma
    return f"{dec_value}".replace(".", "")

def send_tickets_email(status, order: TicketOrderModel, request):
    
    invoice = get_template("emails/tickets/invoice.html")
    render_invoice = invoice.render({
            "buyer_full_name": order.buyer.get_full_name(),
            "order": order,
            "due_date": reservation_time(),
                
        }, request=request)
        
    pdf_file = HTML(string=render_invoice).write_pdf()
    files = [
            {"file_content": base64.b64encode(pdf_file).decode(), "name": f'{order.order_number}_invoice.pdf'}
        ]
        
    context = {
                "user": order.buyer.get_full_name(),
                "order": order
            }
    if status == "payment.succeeded" or status == PaymentStatus.PAID:

        mail_subject = f"Your tickets for {order.event.title} on {order.event.date_time_formatter()}"
        message = render_to_string("emails/tickets/ticket-order-email.html", context, request=request
            )
                    
        with open(order.tickets_pdf_file.path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()

        encoded_content = base64.b64encode(pdf_content).decode()
        
        files.append({"file_content": encoded_content, "name": f'{order.order_number}_tickets.pdf'})

    else:
        mail_subject = f"Your tickets order for {order.event.title} on {order.event.date_time_formatter()} was cancelled"
        message = render_to_string("emails/tickets/order-cancelled.html", context,
            )

    sent = send_html_email_with_attachments(order.buyer.email, mail_subject, message, "Ndwandwa Fam Events <events@ndwandwa.africa>", files)
            
    if not sent:
        email_logger.error(f"Trouble sending tickets email to {order.buyer.email} order number {order.order_number}")
        return False
        
    return True
    
def send_contribution_confirm_email(order: ContributionModel, request, status):

    template = get_template("emails/contributions/invoice-contribution.html")
    rendered_template = template.render({
            "buyer_full_name": order.contributor.get_full_name(),
            "order": order,
            "due_time": in_fourteen_days()
        }, request=request)

    pdf_file = HTML(string=rendered_template).write_pdf()
    buffer = BytesIO(pdf_file)
    files = [
            {"file_content": base64.b64encode(pdf_file).decode(), "name": f'{order.order_number}_invoice.pdf'}
        ]
    context = {
                "user": order.contributor.get_full_name(),
                "order": order
            }

    if status == "payment.succeeded" or status == PaymentStatus.PAID:
        mail_subject = F"Your contribution confirmation {order.campaign.title} campaign was successful"
        message = render_to_string("emails/contributions/contribution-email.html",
                    context, request=request
                )
    else:
        mail_subject = F"Your contribution payment {order.campaign.title} campaign was unsuccessful"
        message = render_to_string("emails/contributions/contribution-cancelled.html",
                    context,
                )

    sent = send_html_email_with_attachments(order.contributor.email, mail_subject, message, "Ndwandwa Campaigns <campaigns@ndwandwa.africa>", files)
          
    if not sent:
        email_logger.error(f"confirmation email not sent for {order.order_number} to {order.contributor.email}")
        return False
            
    return True

def update_wallet(user, amount, tip, order_number):
    try:
        wallet, created = WalletModel.objects.get_or_create(owner = user)
        if wallet:
            wallet.balance += amount
            wallet.save(update_fields=['balance'])
        if created:
            wallet.balance += amount
            wallet.save(update_fields=['balance'])
        
        NdwandwaBankModel.objects.get_or_create(balance=tip, order_id=order_number)
        return True

    except WalletModel.DoesNotExist:
        return False
    
def update_payment_details(order, data, payment_status: PaymentStatus):
    payload = data["payload"]
    payment_method_details = payload["paymentMethodDetails"]
    card_details = payment_method_details.get("card", None)
    order.paid = payment_status
    if card_details:
        order.payment_method_type = card_details.get("type", "-")
        order.payment_method_card_holder = card_details.get("cardHolder", "-")
        order.payment_method_masked_card = card_details.get("maskedCard", "-")
        order.payment_method_scheme = card_details.get("scheme", "-")

    order.payment_date = str(payload.get("createdDate", "-"))
    order.save(update_fields=["paid", "payment_method_card_holder", "payment_method_type","payment_method_masked_card", "payment_method_scheme"])

def update_payment_status_ticket_order(data, request,  ticket_order: TicketOrderModel):

    if data["type"] == "payment.succeeded":
        payment_status = PaymentStatus.PAID
        admin_cost = ticket_order.calculate_total_admin_cost()
        organiser_profit = ticket_order.calculate_actual_profit()
        wallet_updated = update_wallet(ticket_order.event.organiser, organiser_profit, admin_cost, ticket_order.order_number)
        if not wallet_updated:
            logger.error("Failed to update wallet")
    else:
            payment_status = PaymentStatus.NOT_PAID
        
    update_payment_details(ticket_order, data, payment_status)
    sent = send_tickets_email(data["type"], ticket_order, request)

    if sent:
        return True
    else:
        return False
    
def update_payment_status_contribution_order(data, request, contribution: ContributionModel):

    if data["type"] == "payment.succeeded":
        payment_status = PaymentStatus.PAID
        contribution.campaign.current_amount += contribution.amount
        contribution.campaign.save(update_fields=['current_amount'])
        tip = contribution.total_amount - contribution.amount
        wallet_updated = update_wallet(contribution.campaign.organiser, contribution.amount, tip, contribution.order_number)
        if not wallet_updated:
            logger.error("Wallet not updated")
    else:
        payment_status = PaymentStatus.NOT_PAID

    update_payment_details(contribution, data, payment_status)
    sent = send_contribution_confirm_email(contribution, request, data["type"])

    if sent:
        return True
    else:
        return False

