from django.db import models
from django.urls import reverse
from accounts.utils import StatusChoices
from campaigns.utils import handle_business_file_upload
from accounts.models import PHONE_VALIDATOR, AbstractCreate, AbstractProfile, SubscriptionPackage
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from tinymce.models import HTMLField
from django.template.defaultfilters import slugify

DAYCHOICES = [
    ("MO", "Monday"),
    ("TU", "Tuesday"),
    ("WE", "Wednesday"),
    ("TH", "Thursday"),
    ("FR", "Friday"),
    ("SA", "Saturday"),
    ("SU", "Sunday")
    ]

BBBEE_RATINGS = [
    ("BEL1", "BEE Level 1"),
    ("BEL2", "BEE Level 2"),
    ("BEL3", "BEE Level 3"),
    ("BEL4", "BEE Level 4"),
    ("BEL5", "BEE Level 5"),
    ("BEL6", "BEE Level 6"),
    ("NC", "Non-compliance")
    ]

class OperatingChoices(models.TextChoices):
    CUSTOM = ("CUSTOM", "Custom")
    CLOSED = ("CLOSED", "Closed")
    OPEN = ("OPEN", "Open 24/7")

class Category(AbstractCreate):
    thumbnail = models.ImageField(upload_to="category/business/", null=True, blank=True)
    slug = models.SlugField(max_length=350, unique=True, db_index=True)
    label = models.CharField(max_length=250, unique=True)
    

    def __str__(self):
        return str(self.label)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.label)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Business(AbstractProfile, AbstractCreate):
    background_image = models.ImageField(help_text=_("Upload company/business background image."), upload_to=handle_business_file_upload, blank=True, null=True)
    logo = models.ImageField(help_text=_("Upload company/business logo."), upload_to=handle_business_file_upload, blank=True, null=True)
    title = models.CharField(help_text=_("Enter title for your company/business"), max_length=150)
    slogan = models.CharField(_("Enter your business slug"), max_length=350, null=True, blank=True)
    slug = models.SlugField(max_length=250, blank=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=None, related_name="businesses")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="businesses")
    details = HTMLField(help_text=_("Enter additional details about your company/business"))
    map_coordinates  = models.CharField(max_length=300, blank=True, null=True)
    phone = models.CharField(help_text=_("Enter your company/business number"), max_length=15, validators=[PHONE_VALIDATOR], unique=True, null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    email = models.URLField(_("Enter your business website"), max_length=250, blank=True, null=True)
    bbbee_level = models.CharField(max_length=100, choices=BBBEE_RATINGS, default=BBBEE_RATINGS[1])
    operation = models.CharField(max_length=100, choices=OperatingChoices.choices, default=OperatingChoices.OPEN)
    status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.NOT_APPROVED)

    class Meta:
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Business, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        return reverse("business:get-listing", kwargs={"listing_slug": self.slug})
    
    def get_full_location(self):
        if self.address_one and self.city and self.province and self.country:
            if self.address_two:
                return f"{self.address_one}, {self.address_two}, {self.city}, {self.province}, {self.country}"
            else:
                return f"{self.address_one}, {self.city}, {self.province}, {self.country}"
        else:
            return "No address"
    
    def get_location(self):
        if self.address_one and self.city and self.province and self.country:
            return f"{self.city}, {self.province}"
        else:
            return "No address"

    def is_open(self):

        if self.operation == "CUSTOM":
            now = timezone.now()
            current_day = now.strftime('%a').upper()[:2]
            current_time = now.time()

            business_hours_today = self.business_hours.filter(day=current_day)
            for hours in business_hours_today:
                if hours.operating:
                    if hours.open_time <= current_time <= hours.close_time:
                        return True
                    else:
                        return False
                else:
                    return False
        elif self.operation == "OPEN":
            return True

        else:
            return False

class BusinessContent(AbstractCreate):
    image = models.ImageField(help_text=_("Upload company/business images."), upload_to=handle_business_file_upload, blank=True, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="images")

class BusinessReview(AbstractCreate):
    commenter = models.ForeignKey(get_user_model(), related_name="reviews", on_delete=models.SET_NULL, null=True)
    commenter_email = models.EmailField()
    commenter_full_names = models.CharField(max_length=250)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField()

    class Meta:
        verbose_name = 'Business Review'
        verbose_name_plural = 'Business Reviews'

    def __str__(self) -> str:
        return self.commenter_email

class BusinessHour(AbstractCreate):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="business_hours")
    day = models.CharField(max_length=250, choices=DAYCHOICES, default=DAYCHOICES[1])
    operating = models.BooleanField(default=True)
    open_time = models.TimeField()
    close_time = models.TimeField()

    class Meta:
        unique_together = ('business', 'day')
        verbose_name = 'Business Hour'
        verbose_name_plural = 'Business Hours'

# class BusinessProduct(AbstractCreate):
#     product_image = models.ImageField()
#     description = HTMLField(help_text=_("Decribe your product or service"))
#     price = models.DecimalField()

