import uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.dispatch import receiver
from taggit.managers import TaggableManager
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_delete, post_save
from accounts.utils import (TITLE_CHOICES, WALLET_STATUS, Gender, RelationshipSides, StatusChoices, IdentityNumberChoices, RelationShip, QualificationType, 
                            handle_profile_upload, handle_relativeprofile_upload, handle_verification_docs_upload, verify_rsa_phone,
                            validate_twitter_link, validate_fcbk_link, validate_in_link, validate_insta_link)
from tinymce.models import HTMLField


PHONE_VALIDATOR = verify_rsa_phone()

class AbstractProfile(models.Model):
    address_one = models.CharField(max_length=300, blank=True, null=True)
    address_two = models.CharField(max_length=300, blank=True, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)
    province = models.CharField(max_length=300, blank=True, null=True)
    country = models.CharField(max_length=300, default="South Africa")
    zipcode = models.BigIntegerField(blank=True, null=True)
    address_id = models.CharField(max_length=300, null=True, blank=True)

    facebook = models.URLField(validators=[validate_fcbk_link], blank=True, null=True)
    twitter = models.URLField(validators=[validate_twitter_link], blank=True, null=True)
    instagram = models.URLField(validators=[validate_insta_link], blank=True, null=True)
    linkedIn = models.URLField(validators=[validate_in_link], blank=True, null=True)

    class Meta:
        abstract = True

class AbstractCreate(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CompanyModel(AbstractCreate, AbstractProfile):
    support_email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(help_text=_("Enter your cellphone number"), max_length=15, validators=[PHONE_VALIDATOR], unique=True, null=True, blank=True)
    
    class Meta:
        verbose_name = "Company Details"
        verbose_name_plural = "Company Details"
    
    def __str__(self):
        return "Ndwandwa Family Foundation"
    

class WalletModel(AbstractCreate):
    name = models.CharField(max_length=250)
    balance = models.DecimalField(max_digits=1000, decimal_places=2, default=0.00)
    owner = models.OneToOneField("CustomUserModel", on_delete=models.CASCADE, related_name="my_wallet")
    status = models.CharField(max_length=150, choices=WALLET_STATUS, default=WALLET_STATUS[0])
    cleared_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Wallet")
        verbose_name_plural = _("Wallets")
        ordering = ["-created"]

    def request_payout_details(self):
        pass

    def clear_account(self):
        self.balance = 0

    def __str__(self):
        return self.name
    
class CustomUserModel(AbstractUser, AbstractProfile):
    profile_image = models.ImageField(help_text=_("Upload profile image"), upload_to=handle_profile_upload, null=True, blank=True, default="images/global/no-image-available.webp")
    title = models.CharField(max_length=30, choices=TITLE_CHOICES)
    maiden_name = models.CharField(help_text=_("Enter your relative's maiden name"), max_length=300, blank=True, null=True)
    phone = models.CharField(help_text=_("Enter your cellphone number"), max_length=15, validators=[PHONE_VALIDATOR], unique=True, null=True, blank=True)
    occupation = models.CharField(default='N/A',help_text=_("Enter your current employment"), max_length=500, blank=True, null=True)
    biography = models.TextField(blank=True)
    professional_affiliations = models.CharField(default='N/A',help_text=_("Enter your professional affiliations"), max_length=700, blank=True, null=True)
    identity_choice = models.CharField(help_text=_("Select your identity document"), max_length=100, choices=IdentityNumberChoices.choices, default=IdentityNumberChoices.ID_NUMBER)
    identity_number = models.CharField(unique=True, max_length=13, null=True, blank=True)
    verification_status = models.CharField(max_length=100, choices=StatusChoices.choices, default=StatusChoices.NOT_APPROVED)
    hobbies = TaggableManager(blank=True)
    is_technical = models.BooleanField(default=False)
    is_email_activated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

  
    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ["-created"]
    
    def get_absolute_url(self):
        return reverse("accounts:user", kwargs={"username": self.username})
    
    def image_tag(self):
        if self.profile_image.url is not None:
            return mark_safe(f"<img src={self.profile_image.url} alt={self.first_name}-image height='60' width='60' style='border-radius: 50%; height: 60px; width: 60px;' />")
        return ""
    
    def address(self):
        if self.address_one and self.city and self.province and self.country:
            if self.address_two:
                return f"{self.address_one}, {self.address_two}, {self.city}, {self.province}, {self.country}"
            else:
                return f"{self.address_one}, {self.city}, {self.province}, {self.country}"
        else:
            return "No address"
    
    def contact_details(self):
        return mark_safe(f"""
            <div style="display: flex; align-items: center; background-color: #fff;;">
                <a href="mailto:{self.email}" style="margin: 0rem 1rem;">{self.email}</a>
                <a href="tel:{self.phone}" style="margin: 0rem 1rem;">{self.phone}</a>
            </div>
            <div style="display: flex; align-items: center; background-color: #fff;;">
                <a href="{self.facebook}" style="margin: 0rem 1rem;">{self.facebook}</a>
                <a href="{self.twitter}" style="margin: 0rem 1rem;">{self.twitter}</a>
            </div>
        """)

    def identity_information(self):
        return f"{self.identity_number} - {self.identity_choice}"
    
    def employment_details(self):
        if self.occupation and self.professional_affiliations:
            return f"{self.occupation} - {self.professional_affiliations}"
        elif self.occupation:
            return f"{self.occupation}"
        elif self.professional_affiliations:
            return f"No occupation - {self.professional_affiliations}"
        else:
            return "No occupation"
    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} - {self.username}"
    
class IdentityVerificationModel(AbstractCreate):
    identity_image =  models.ImageField(upload_to=handle_verification_docs_upload, null=False, help_text=_("Please take a selfie while holding an official identification document(ID Card, Passport)"))
    identitybook_image = models.ImageField(upload_to=handle_verification_docs_upload, null=False, help_text=_("Please take a picture of your official identification document(ID Card, Passport, drivers license, etc)"))
    user = models.OneToOneField(CustomUserModel, related_name="verification", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Identity Verification")
        verbose_name_plural = _("Identity Verifications")
        ordering = ["-created"]

    def get_absolute_url(self):
        return reverse("accounts:verify")
    
    def __str__(self) -> str:
        return f"{self.user.get_full_name()} - Identity verification data"

class RelativeModel(AbstractCreate):
    profile_image = models.ImageField(help_text=_("Upload relative's profile image"), upload_to=handle_relativeprofile_upload, null=True, blank=True, default="images/global/no-image-available.webp")
    title = models.CharField(max_length=30, choices=TITLE_CHOICES)
    full_name = models.CharField(help_text=_("Enter your relative's name"), max_length=300)
    maiden_name = models.CharField(help_text=_("Enter your relative's maiden name"), max_length=300, blank=True, null=True)
    surname = models.CharField(help_text=_("Enter your relative's surname"), max_length=300)
    relationship = models.CharField(max_length=300, choices=RelationShip.choices, default=RelationShip.OTHER)
    phone = models.CharField(help_text=_("Enter relative's cell phone number"), max_length=15,  validators=[PHONE_VALIDATOR], null=True, blank=True)
    relative = models.ForeignKey(CustomUserModel, related_name="relatives", on_delete=models.CASCADE)
    gender = models.CharField(help_text=_("Select relative's gender"), max_length=15, choices=Gender.choices)
    relative_side = models.CharField(max_length=300, choices=RelationshipSides.choices, blank=True, null=True)
    description = models.TextField(blank=True, null=True, help_text=_("Provide a small description of this relative, e.g His/Her Children"))

    class Meta:
        verbose_name = 'Relative'
        verbose_name_plural = 'Relatives'
        unique_together = ['title', 'full_name', 'maiden_name', 'surname', 'relative', 'relationship', 'relative_side', 'phone']

    def get_absolute_url(self):
        return reverse("accounts:relative", kwargs={"id": self.id})

    def get_full_names(self):
        if self.maiden_name != None:
            return f"{self.title} {self.full_name} {self.surname} {self.maiden_name}"
        else:
            return f"{self.title} {self.full_name} {self.surname}"
    
    def __str__(self):
        return self.full_name
    
class QualificationModel(AbstractCreate):
    institution = models.CharField(max_length=300)
    title = models.CharField(max_length=300)
    qualification_type = models.CharField(max_length=300, choices=QualificationType.choices, default=QualificationType.MATRIC)
    year = models.CharField(max_length=50, help_text="Enter year range e.g 2019 - 2022")
    owner = models.ForeignKey(CustomUserModel, related_name="qualifications", on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("accounts:update-qualification", kwargs={"id": self.id})

    class Meta:
        verbose_name = 'Qualification'
        verbose_name_plural = 'Qualifications'
        unique_together = ['title', 'qualification_type', 'year', 'owner']

    def __str__(self):
        return self.title

class MailingGroupModel(AbstractCreate):
    slug = models.SlugField(max_length=100, unique=True, db_index=True, null=True)
    title = models.CharField(max_length=80, unique=True)
    description = models.CharField(help_text="Describe mailing list", max_length=500)
    subscribers = models.ManyToManyField(CustomUserModel, through="SubscribeModel", related_name="mailing_groups")

    class Meta:
        verbose_name = 'Mailing group'
        verbose_name_plural = 'Mailing groups'

    def get_absolute_url(self):
        return reverse("accounts:subscribe")
    

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(MailingGroupModel, self).save(*args, **kwargs)
   
class SubscribeModel(AbstractCreate):
    user = models.ForeignKey(CustomUserModel, related_name="subscriber", on_delete=models.CASCADE)
    mailinggroup = models.ForeignKey(MailingGroupModel, related_name="subscribe_to", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Subscribe'
        verbose_name_plural = 'Subscribes'

    def __str__(self):
        return f"{self.user.get_full_name} subscibed to {self.mailinggroup.title}"

class MailMessageModel(AbstractCreate):
    from_mail = models.CharField(help_text="e.g John Snow <<john@ndwandwa.africa>>",max_length=150)
    subject = models.CharField(max_length=250)
    message = HTMLField()
    mailing_group = models.ForeignKey(MailingGroupModel, related_name="email_messagess", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.subject
    
    class Meta:
        verbose_name = 'Mail Message'
        verbose_name_plural = 'Mail Messages'

@receiver(pre_delete, sender=CustomUserModel)
def delete_content_files_hook(sender, instance, using, **kwargs):
	instance.profile_image.delete()

@receiver(pre_delete, sender=IdentityVerificationModel)
def delete_content_files_hook(sender, instance, using, **kwargs):
	instance.identity_image.delete()
	instance.identitybook_image.delete()

# @receiver(post_save, sender=MailingGroupModel)
# def notify_subscriber(sender, instance, created, **kwargs):
#     from accounts.tasks import send_notification_mail_to_subscribers
#     if created:
#         send_notification_mail_to_subscribers.delay(instance.id)