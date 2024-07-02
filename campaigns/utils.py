import uuid
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.db import models

class PaymentStatus(models.TextChoices):
        PAID = ("PAID", "Paid")
        PENDING = ("PENDING", "Pending")
        NOT_PAID = ("NOT PAID", "Not paid")
        CANCELLED = ("CANCELLED", "Cancelled")

class Tip(models.TextChoices):
        TEN = ("10%", "10%")
        TEN_FIVE = ("15%", "15%")
        TEN_TEN = ("20%", "20%")
        TEN_TEN_FIVE = ("25%", "25%")

def handle_campaign_file_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return f"campaign/{filename}"

def handle_business_file_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return f"business/{filename}"

def generate_order_number(model) -> str:
    order_id_start = f'NFRF{timezone.now().year}{timezone.now().month}'
    queryset = model.objects.filter(order_number__iexact=order_id_start).count()
      
    count = 1
    order_number = order_id_start
    while(queryset):
        order_number = f'NFRF{timezone.now().year}{timezone.now().month}{count}'
        count += 1
        queryset = model.objects.all().filter(order_number__iexact=order_number).count()

    return order_number

def generate_slug(title: str, model) -> str:
    original_slug: str = slugify(title)
    queryset =  model.objects.all().filter(slug__iexact=original_slug).count()

    count = 1
    slug = original_slug
    while(queryset):
        slug = original_slug + '-' + str(count)
        count += 1
        queryset = model.objects.all().filter(slug__iexact=slug).count()

    return slug