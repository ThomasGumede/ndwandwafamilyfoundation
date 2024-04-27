from django.shortcuts import redirect, render, get_object_or_404
from accounts.forms.account_forms import *
from accounts.forms.profile_forms import SocialLinksForm
from accounts.utils import StatusChoices, send_verification_email, send_email_confirmation_email
from accounts.tokens import account_activation_token
from accounts.decorators import user_not_authenticated
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
import logging, jwt
from accounts.models import MailingGroupModel, SubscribeModel

logger = logging.getLogger("accounts")

User = get_user_model()

@user_not_authenticated
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        payload = jwt.decode(uidb64, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(pk=payload["user_id"], username=payload["username"])
    except User.DoesNotExist:
        user = None
    
    if user and account_activation_token.check_token(user, token):
        if user.is_active == True:
            messages.success(
                request,
                "Thank you for your email confirmation. Now you can login your account.",
            )
            return redirect("accounts:login")
        
        user.is_active = True
        user.is_email_activated = True

        for group in MailingGroupModel.objects.all():
            subscribed, created = SubscribeModel.objects.get_or_create(user=user, mailinggroup=group)
            if created:
                pass
        user.save(update_fields=["is_active", "is_email_activated"])

        messages.success(
            request,
            "Thank you for your email confirmation. Now you can login your account.",
        )
        return redirect("accounts:login")
    else:
        messages.error(request, f"Activation link is expired! New activation link was sent to {user.email}")
        sent = send_verification_email(user, request)
        if not sent:
            logger.error(f"Something went wrong trying to send email to {user.username}")

    return redirect("home:home")

def confirm_email(request, uidb64, token):
    logout(request)
    User = get_user_model()
    try:
        payload = jwt.decode(uidb64, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(pk=payload["user_id"], username=payload["username"])
    except:
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_email_activated = True
        user.save(update_fields=["is_active", "is_email_activated"])

        messages.success(
            request,
            "Thank you for your email confirmation. Now you can login to your account with your new email.",
        )

        return redirect("accounts:login")
    
    else:
        messages.error(request, f"Email confirmation link is expired! New email confirmation link was sent to {user.email}")
        sent = send_email_confirmation_email(user, user.email, request)

        if not sent:
            logger.error(f"Something went wrong trying to send email to {user.username}")

    return redirect("home:home")

def get_accounts(request):
    template = "accounts/account/users.html"
    query = request.GET.get("q", None)
    users = User.objects.filter(is_technical=False)
    if query:
        users = User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query) 
            | Q(address__address_one__icontains = query)
        )
        
    return render(request, template, {"users": users, "query": query})

@user_not_authenticated
def register(request):
    template_name = "accounts/account/register.html"
    success_url = "accounts:success"
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        
        
        if form.is_valid() and form.is_multipart():
            cd = form.cleaned_data
            user = form.save(commit=False)
            user.is_active = False
            identity_choice = cd.get('identity_choices', None)
            identity_number = cd.get('identity_number', None)
            if identity_choice and identity_number:
                user.identity_choice = cd['identity_choices']
                user.identity_number = cd['identity_number']
            user.save()
            sent = send_verification_email(user, request)

            if not sent:
                logger.error(f"Something went wrong trying to send email to {user.username}")

            messages.success(
                request,
                f"Dear {user}, please go to you email {user.email} inbox and click on \
                    received activation link to confirm and complete the registration. Note: Check your spam folder.",
            )
            return redirect(success_url)

        else:
            return render(
                request=request, template_name=template_name, context={"form": form}
            )

    else:
        form = RegistrationForm()

    return render(request=request, template_name=template_name, context={"form": form})

@login_required
def add_social_links(request):
    social_link = get_object_or_404(get_user_model(), username=request.user.username)
    
    form = SocialLinksForm(instance=social_link)

    if request.method == 'POST':
        form = SocialLinksForm(instance=social_link, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Social links successfully updated")
            return redirect("accounts:update-social-links")
        else:
            return render(request, "accounts/account/social/update.html", {"form": form})
        
    return render(request, "accounts/account/social/update.html", {"form": form})

@user_not_authenticated
def activation_sent(request):
    return render(request, "accounts/account/activation_sent.html")


@user_not_authenticated
def custom_login(request):
    next_page = request.GET.get("next", None)
    template_name = "accounts/account/login.html"
    success_url = "home:home"
    if next_page:
        success_url = next_page

    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None and user.is_active:
                login(request, user)
                messages.success(
                    request, f"Hello <b>{user.username}</b>! You have been logged in"
                )
                return redirect(success_url)
        else:
            account = User.objects.filter(username=form.cleaned_data["username"]).first()
            if account != None and not account.is_active:
                messages.error(request, f"Sorry your account is not active. We have sent account activation email to your email {account.email}")
                sent = send_verification_email(account, request)
                if not sent:
                    pass
                return redirect("accounts:login")
            
            return render(
                request=request, template_name=template_name, context={"form": form}
            )

    form = UserLoginForm()
    return render(request=request, template_name=template_name, context={"form": form})

@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("home:home")

@login_required
def user_details(request, username):
    model = get_object_or_404(get_user_model().objects.prefetch_related("qualifications", "campaigns", "events", "hobbies").all(), username=username)
    template = "accounts/account/account.html"
    context = {
        "user": model
    }
   

    return render(request, template, context)

@login_required
def general(request):
    template = "accounts/account/manage/general.html"
    

    if request.method == 'POST':
        form = GeneralEditForm(instance=request.user, data=request.POST)
        old_email = request.user.email

        if form.is_valid():
            new_email = form.cleaned_data["email"]
            user = form.save(commit=False)
            if old_email != new_email:
                user.is_email_activated = False
                sent = send_email_confirmation_email(request.user, new_email, request)
                if not sent:
                    logger.error(f"Email error - failed to send email to  {form.cleaned_data['email']}")

                messages.success(request, "we have also sent email confirmation to your new email address")
            else:
                user.email = old_email

            user.save(update_fields=["username", "email", "phone", "address_one", "address_two", "city", "country", "province", "zipcode"])
            messages.success(request, "Your information was updated successfully")
            return redirect("accounts:contact-update")
        else:

            messages.error(request, "Your information was updated unsuccessfull, please fix errors below")
            return render(request, template, {"form": form})
        
    form = GeneralEditForm(instance=request.user)

    
    return render(request, template, {"form": form})

@login_required
def account_update(request):
    template = "accounts/account/manage/update.html"

    if request.method == 'POST':
        form = AccountUpdateForm(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid() and form.is_multipart():
            cd = form.cleaned_data
            user = form.save(commit=False)
            user.identity_choice = cd['identity_choices']
            user.identity_number = cd['identity_number']
            user.save(update_fields=["title", "profile_image", "first_name", "last_name", 'maiden_name', "biography", "occupation", "professional_affiliations", "identity_number"])
            messages.success(request, "Your information was updated successfully")
            return redirect("accounts:profile-update")
        else:
            return render(request, template, {"form": form})
        
    form = AccountUpdateForm(instance=request.user)  
    return render(request, template, {"form": form})

@login_required
def identitification(request):
    template = "accounts/account/manage/verify.html"

    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES)
        if form.is_valid() and form.is_multipart():
            identity = form.save(commit=False)
            identity.user = request.user
            request.user.verification_status = StatusChoices.PENDING
            request.user.save(update_fields=["verification_status"])
            identity.save()
            messages.success(request, "Your identitification verication is pending, will update you")
            return redirect("accounts:verify")
        else:
            return render(request, template, {"form": form})
        
    form = VerificationForm()
    return render(request, template, {"form": form})

@login_required
def get_me(request):
    try:
        me = User.objects.prefetch_related("campaigns", "events", "contributions", "ticketorders", "my_wallet").get(username = request.user.username)
        campaigns = me.campaigns.all()[0:5]
        events = me.events.all()[0:5]
        return render(request, "accounts/account/manage/me.html", {"user": me, "events": events, "campaigns": campaigns})
    except User.DoesNotExist:
        return redirect("home:home")