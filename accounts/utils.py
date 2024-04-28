from datetime import datetime
import uuid, re, logging
from django.db import models
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from accounts.tokens import account_activation_token, generate_activation_token
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

logger = logging.getLogger("emails")

def validate_sa_id_number(id_number):
    error_messages = error_messages = {"success": True, "message": "ID number is valid"}

    if not re.match(r'^\d{13}$', id_number):
        error_messages = {"success": False, "message": "ID number should contain 13 numbers"}

    year = int(id_number[0:2])
    month = int(id_number[2:4])
    day = int(id_number[4:6])

    try:
        dob = datetime(year + 1900, month, day)

    except ValueError:
        error_messages = {"success": False, "message": "Your ID number is invalid"}

    if not (int(id_number[10]) in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]):
        error_messages = {"success": False, "message": "Your ID number is invalid"}

    check_sum = 0
    for i in range(13):
        digit = int(id_number[i])
        if i % 2 == 0:
            check_sum += digit
        else:
            check_sum += sum(divmod(digit * 2, 10))
    valid_check = check_sum % 10 == 0
    if not valid_check:
        error_messages = {"success": False, "message": "Your ID number is invalid"}

    return error_messages

def validate_sa_passport_number(passport_number):
    if not re.match(r'^[A-Z]{2}\d{8}$', passport_number):
        return False

    year = int(passport_number[2:4])

    current_year = datetime.now().year % 100
    if not (20 <= year <= current_year):
        return False

    return True


def custom_send_email(to_email, subject, html_content):
    message = Mail(
        from_email='Ndwandwa Family Foundation <noreply@ndwandwa.africa>',
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        response = sg.send(message)
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
        return True
    
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def send_html_email_with_attachments(to_email:str, subject: str, html_content, from_email:str, pdf_attachments:list):

    message = Mail(
        from_email=from_email,  # Replace with your email address
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )


    for pdf_attachment in pdf_attachments:
        

        attachment = Attachment(
            FileContent(pdf_attachment["file_content"]),
            FileName(pdf_attachment['name']),
            FileType('application/pdf'),
            Disposition('attachment')
        )

        message.add_attachment(attachment)

    # Send the email using SendGrid
    try:
        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        response = sg.send(message)
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
        return True
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def validate_fcbk_link(value):
    url_validator = URLValidator()
    facebook_regex = r'^https?://(www\.)?facebook\.com/.*$'
    if re.match(facebook_regex, value) == None:
        raise ValidationError('Invalid Facebook profile link')
    
def validate_twitter_link(value):
    url_validator = URLValidator()
    twitter_regrex = r'^https?://(www\.)?twitter\.com/.*$'
    if re.match(twitter_regrex, value) == None:
        raise ValidationError('Invalid Twitter profile link')

def validate_insta_link(value):
    url_validator = URLValidator()
    instagram_regex = r'^https?://(www\.)?instagram\.com/.*$'
    if re.match(instagram_regex, value) == None:
        raise ValidationError('Invalid Instagram profile link')
    
def validate_in_link(value):
    url_validator = URLValidator()
    linkedin_regex = r'^https?://(www\.)?linkedin\.com/.*$'
    if re.match(linkedin_regex, value) == None:
        raise ValidationError('Invalid LinkedIn profile link')

def send_email_confirmation_email(user, new_email, request):
    mail_subject = "New Email Confirmation"
    message = render_to_string("emails/account/email_activation.html",
            {
                "user": user.get_full_name(),
                "email": new_email,
                "uid": generate_activation_token(user),
                "token": account_activation_token.make_token(user),
            }, request
        )
    sent = custom_send_email(new_email, mail_subject, message)

    if not sent:
        logger.error("User did not receive email")
        return False
    return True

def send_verification_email(user, request):
        mail_subject = "Activate Account"
        message = render_to_string("emails/account/account_activate_email.html",
            {
                "user": user.get_full_name(),
                "uid": generate_activation_token(user),
                "token": account_activation_token.make_token(user),
            }, request
        )
        
        sent = custom_send_email(user.email, mail_subject, message)

        if not sent:
            logger.error("User did not receive email")
            return False
        
        return True

def send_password_reset_email(user, request):

        subject = "Password Reset request"
        message = render_to_string("emails/password/reset_password_email.html", {
            'user': user.get_full_name(),     
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        }, request)
            
            
        sent = custom_send_email(user.email, subject, message)
        if not sent:
            return False
           
        return True
    
def verify_rsa_phone():
    PHONE_REGEX = RegexValidator(r'^(\+27|0)[6-8][0-9]{8}$', 'RSA phone number is required')
    return PHONE_REGEX

def handle_profile_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return f"profile/{filename}"

def handle_relativeprofile_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return f"profile/relatives/{filename}"

def handle_verification_docs_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}-{}.{}'.format(uuid.uuid4().hex, instance.user.username,ext)
    return f"profile/verify/{filename}"

from django.db import models

WALLET_STATUS = (
    ("No status", "No status"),
    ("Requested Payout Details", "Requested Payout Details"),
    ("Verifying Payout Details", "Verifying Payout Details"),
    ("Approved Payout", "Approved Payout"),
    ("Payout Declined", "Payout Declined"),
    
)

TITLE_CHOICES = (
    ("Mr", "Mr"),
    ("Mrs", "Mrs"),
    ("Ms", "Ms"),
    ("Dr", "Dr"),
    ("Prof", "Prof.")
)

class StatusChoices(models.TextChoices):
    NOT_APPROVED = ("NOT APPROVED", "Not approved")
    PENDING = ("PENDING", "Pending")
    APPROVED = ("APPROVED", "Approved")
    COMPLETED = ("Completed", "Completed")
    BLOCKED = ("Blocked", "Blocked")

class IdentityNumberChoices(models.TextChoices):
    ID_NUMBER = ("ID_NUMBER", "ID number")
    PASSPORT = ("PASSPORT", "Passport")

class Gender(models.TextChoices):
    MALE = ("MALE", "Male")
    FEMALE = ("FEMALE", "Female")
    OTHER = ("OTHER", "Other")

class RelationShip(models.TextChoices):
    OTHER = ("OTHER", "Other")
    WIFE = ("WIFE", "Wife")
    HUSBAND = ("HUSBAND", "Husband")
    DAUGHTER = ("DAUGHTER", "Daughter")
    SON = ("SON", "Son")
    MOTHER = ("MOTHER", "Mother")
    FATHER = ("FATHER", "Father")
    STEPMOTHER = ("STEPMOTHER", "Step-mother")
    STEPFATHER = ("STEPFATHER", "Step-father")
    STEPBROTHER = ("STEPBROTHER", "Step-Brother")
    STEPSISTER = ("STEPSISTER", "Step-Sister")
    GRANDMOTHER = ("GRANDMOTHER", "Grandmother")
    GRANDFATHER = ("GRANDFATHER", "Grandfather")
    GREATGRANDMOTHER = ("GREATGRANDMOTHER", "Great Grandmother")
    GREATGRANDFATHER = ("GREATGRANDFATHER", "Great Grandfather")
    GREATGREATGRANDMOTHER = ("GREATGREATGRANDMOTHER", "Great Great Grandmother")
    GREATGREATGRANDFATHER = ("GREATGREATGRANDFATHER", "Great Great Grandfather")
    BROTHER = ("BROTHER", "Brother")
    SISTER = ("SISTER", "Sister")
    COUSIN = ("COUSIN", "Cousin")
    AUNT = ("AUNT", "Aunt")
    UNCLE = ("UNCLE", "Uncle")
    NEPHEW = ("NEPHEW", "Nephew")
    NIECE = ("NIECE", "Niece")

class RelationshipSides(models.TextChoices):
    MOTHER = ("MOTHER'S SIDE", "Mother's side")
    FATHER = ("FATHER'S SIDE", "Father's side")
    STEPMOTHER = ("STEPMOTHER'S SIDE", "Stepmother's side")
    STEPFATHER = ("STEPFATHER'S SIDE", "Stepfather's side")
    BROTHER = ("BROTHER'S SIDE", "Brother's side")
    SISTER = ("SISTER'S SIDE", "Sister's side")
    

class QualificationType(models.TextChoices):
    BACHELOR = ("BACHELOR", "Bachelor's Degree")
    MASTER = ("MASTER", "Master's Degree")
    DOCTORAL = ("DOCTORAL", "Doctoral Degree")
    POSTGRAD = ("POSTGRAD_CERT", "Postgraduate Certificate")
    HIGH_CERT = ("HIGH_CERTI", "Higher Certicate")
    ADVA_DIP = ("ADVANCE_DIP", "Advance Diploma")
    DIPLOMA = ("DIPLOMA", "Diploma")
    HONO = ("HONOURS", "Honour's Degree")
    MATRIC = ("MATRIC", "Grade 12 Matric")
    OTHER = ("OTHER", "Other")