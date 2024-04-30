from django.shortcuts import render, get_object_or_404, redirect
from home.models import PostModel, CategoryModel, PrivacyModel, FAQ
from home.forms import CommentForm, SearchForm, EmailForm
from accounts.models import RelativeModel
from django.contrib.auth import get_user_model
from django.utils import timezone
from campaigns.models import CampaignModel
from events.models import EventModel
from accounts.utils import StatusChoices
from datetime import timedelta
from home.tasks import send_email_to_admin
from django.db.models import Q
from django.contrib import messages

def home(request):
    in_five_days = timezone.now() - timedelta(days=5)
    template = "home/home.html"
    campaigns = CampaignModel.objects.filter(Q(status = StatusChoices.APPROVED) | Q(status = StatusChoices.COMPLETED))[:3]
    events = EventModel.objects.filter(Q(status = StatusChoices.APPROVED) | Q(status = StatusChoices.COMPLETED))[:3]

    posts = PostModel.objects.filter(created__gte=in_five_days)[:3]
    return render(request, template, {"campaigns": campaigns, "events": events, "posts": posts})

def terms_and_conditions(request, terms_slug=None):
    legals = PrivacyModel.objects.all().only("slug", "title")
    if terms_slug:
        term = get_object_or_404(PrivacyModel, slug=terms_slug)
    else:
        term = get_object_or_404(PrivacyModel, slug="website-terms-and-community-guidlines")

    return render(request, "home/privacy/terms_and_conditions.html", {"legals": legals, "term": term})

def help(request):
    return render(request, "home/help/FAQ.html", {"questions": FAQ.objects.all()})

def contact(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            form.save()
            send_email_to_admin.delay(form.cleaned_data["subject"], form.cleaned_data["message"], form.cleaned_data["from_email"], form.cleaned_data["name"])
            messages.success(request, "We have successfully receive your email, will be in touch shortly")
            return redirect("home:contact")
        else:
            messages.error(request, "Something went wrong, please fix errors below")
            for err in form.errors:
                messages.error(request, f"{err}")
                return render(request, "home/contact.html", {"form": form})
            
    form = EmailForm()
    return render(request, "home/contact.html", {"form": form})


def search(request):

    form = SearchForm()
    query = request.GET.get("query", None)
    query_by = request.GET.get("search_by", None)
    results_dic = {
        "campaigns" : CampaignModel.objects.filter(Q(title__icontains=query)| Q(organiser__first_name__icontains=query)),
        "events": EventModel.objects.filter(Q(title__icontains=query)| Q(organiser__first_name__icontains=query)),
        "news": PostModel.objects.filter(Q(title__icontains=query)),
        "people": get_user_model().objects.filter(Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query) 
            | Q(address_one__icontains = query)),
        "relatives": RelativeModel.objects.filter(Q(surname__icontains=query)
            | Q(full_name__icontains=query)
            | Q(maiden_name__icontains=query))
    }
    context = {}
    if query and query_by:
        context["results"] = results_dic[query_by]
        context["results_type"] = query_by
        context["query"] = query
    elif query:
        if results_dic["campaigns"].count() > 0:
            context["results"] = results_dic["campaigns"]
            context["results_type"] = "campaigns"
            context["query"] = query
        elif results_dic["events"].count() > 0:
            context["results"] = results_dic["events"]
            context["results_type"] = "events"
            context["query"] = query
        elif results_dic["news"].count() > 0:
            context["results"] = results_dic["news"]
            context["results_type"] = "news"
            context["query"] = query
        elif results_dic["people"].count() > 0:
            context["results"] = results_dic["people"]
            context["results_type"] = "people"
            context["query"] = query
        else:
            context["results"] = results_dic["relatives"]
            context["results_type"] = "relatives"
            context["query"] = query
        
    
    context["form"] = form
    template = "home/search.html"
    return render(request, template, context=context)

def news(request, category_slug=None):
    query = request.GET.get("query", None)
    template = "home/news/news.html"
    model = PostModel
    
    if category_slug:
        category = get_object_or_404(CategoryModel, slug=category_slug)
        news = model.objects.filter(category=category)
        if query:
            news = news.filter(title__icontains=query)
    else:
        news = model.objects.all()
        if query:
            news = news.filter(title__icontains=query)

    context = {"posts": news, "query": query}

    return render(request, template, context)


def post_details(request, post_slug, category_slug):
    post = get_object_or_404(PostModel.objects.select_related("category").prefetch_related("comments"), slug=post_slug)
    recent_posts = PostModel.objects.order_by("-created")[:5]

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.commenter = request.user
            instance.post = post
            instance.save()
            messages.success(request, "Comment added successfully")
            return redirect('home:news-details', category_slug=post.category.slug, post_slug=post.slug)
        else:
            messages.error(request, "Comment not added, fix errors below")
            return redirect('home:news-details', category_slug=post.category.slug, post_slug=post.slug)
        
    form = CommentForm()
        
    return render(request, "home/news/details.html", {"post": post, "recent_posts": recent_posts, "form": form})
    
