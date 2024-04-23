from django.db import models
from accounts.models import AbstractCreate
from home.utils import validate_fcbk_link, validate_insta_link, validate_twitter_link
from home.utils import handle_post_file_upload
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.urls import reverse
from django.template.defaultfilters import slugify
from taggit.managers import TaggableManager
from tinymce.models import HTMLField

class CategoryModel(AbstractCreate):
    thumbnail = models.ImageField(upload_to="category/", null=True, blank=True)
    slug = models.SlugField(max_length=350, unique=True, db_index=True)
    label = models.CharField(max_length=250, unique=True)
    

    def __str__(self):
        return str(self.label)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.label)
        super(CategoryModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Categorie")
        verbose_name_plural = _("Categories")
   
class PostModel(AbstractCreate):
    image = models.ImageField(help_text=_("Upload news image."), upload_to=handle_post_file_upload, blank=True, null=True)
    title = models.CharField(help_text=_("Enter title for your news"), max_length=150)
    description = models.CharField(help_text=_("Write a short description about this post"), max_length=200)
    slug = models.SlugField(max_length=250, blank=True, unique=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_DEFAULT, default=None, related_name="posts", null=True)
    category = models.ForeignKey(CategoryModel, on_delete=models.PROTECT, related_name="posts")
    content = HTMLField()
    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def save(self, *args, **kwargs):
        original_slug = slugify(self.title)
        queryset =  PostModel.objects.all().filter(slug__iexact=original_slug).count()

        count = 1
        slug = original_slug
        while(queryset):
            slug = original_slug + '-' + str(count)
            count += 1
            queryset = PostModel.objects.all().filter(slug__iexact=slug).count()

        self.slug = slug
        super(PostModel, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title}"
    
    def get_absolute_url(self):
        return reverse("home:news-details", kwargs={"category_slug": self.category.slug, "post_slug": self.slug})

class CommentModel(AbstractCreate):
    commenter = models.ForeignKey(get_user_model(), related_name="comments", on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

class EmailModel(AbstractCreate):
    subject = models.CharField(max_length=70)
    from_email = models.EmailField()
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    message = models.TextField(max_length=500)
    task_id = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'
        ordering = ["created"]

    def __str__(self) -> str:
        return self.subject

    def save(self, *args, **kwargs):
        super(EmailModel, self).save(*args, **kwargs)

PRIVACY_TITLES = (
    ("Website Terms and Community Guidlines", "Website Terms and Community Guidlines"),
    ("Refund Policy", "Refund Policy"),
    ("Privacy Policy", "Privacy Policy"),
    ("Terms of use: Consumers", "Terms of use: Consumers"),
    ("Terms of use: Organisers", "Terms of use: Organisers")
)

class PrivacyModel(AbstractCreate):
    title = models.CharField(max_length=150, unique=True, choices=PRIVACY_TITLES)
    slug = models.SlugField(max_length=250, unique=True, db_index=True)
    description = models.CharField(max_length=160)
    content = HTMLField()

    class Meta:
        verbose_name = 'Privacy'
        verbose_name_plural = 'Privacys'
        ordering = ['created']

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("home:privacy", kwargs={"terms_slug": self.slug})
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(PrivacyModel, self).save(*args, **kwargs)

class FAQ(AbstractCreate):
    question = models.CharField(max_length=250)
    answer = models.CharField(max_length=550)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question

@receiver(pre_delete, sender=PostModel)
def delete_Post_image_hook(sender, instance, using, **kwargs):
    instance.image.delete()

