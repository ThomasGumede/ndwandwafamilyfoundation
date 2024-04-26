from django.urls import path
from home.views import home, search, news, post_details, help, contact, terms_and_conditions

app_name = "home"
urlpatterns = [
    path("", home, name="home"),
    path("privacy", terms_and_conditions, name="terms"),
    path("privacy/<slug:terms_slug>", terms_and_conditions, name="privacy"),
    path("faq", help, name="help"),
    path("contact", contact, name="contact"),
    path("search", search, name="search"),
    path("posts", news, name="news"),
    path("posts/<slug:category_slug>", news, name="news-category"),
    path("posts/<slug:category_slug>/<slug:post_slug>", post_details, name="news-details")
]
