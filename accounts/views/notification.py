from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from accounts.forms.profile_forms import SubscribeForm

from accounts.models import MailingGroupModel, SubscribeModel

@login_required
def subscribe(request):
    mailinggroups = MailingGroupModel.objects.all()
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            selected = form.cleaned_data["mailinggroups"]
            for group in MailingGroupModel.objects.all():
                group.subscribers.remove(request.user)
                
            if selected.count() == 0:
                messages.success(request, 'You successfully unsubscribe from all Ndwandwa family foundation mailing groups')
                return redirect('accounts:subscribe')
            
            for group in MailingGroupModel.objects.all():
                group.subscribers.remove(request.user)

            for group in form.cleaned_data["mailinggroups"]:
                
                subscribed, created = SubscribeModel.objects.get_or_create(user=request.user, mailinggroup=group)
                if created:
                    messages.success(request, f"You have successfully subscribed to {group.title} mailing group")
            return render(request, "accounts/notification/index.html", {"mailinggroups": mailinggroups, "form": form})
        
        else:
            messages.error(request, "There is error, please fix it below")
            return render(request, "accounts/notification/index.html", {"mailinggroups": mailinggroups, "form": form})
    form = SubscribeForm()
    return render(request, "accounts/notification/index.html", {"mailinggroups": mailinggroups, "form": form})

def unsubscribe(request):
    try:
        for group in MailingGroupModel.objects.all():
            group.subscribers.remove(request.user)

        messages.success(request, 'You successfully unsubscribe from all Ndwandwa family foundation mailing groups')
        return redirect('accounts:subscribe')
    except get_user_model().DoesNotExist:
        messages.success(request, 'You successfully unsubscribe from all Ndwandwa family foundation mailing groups')

        return redirect('accounts:subscribe')
    
def create_mailing_group(request):
    form = None
    if request.method == 'POST':
        form = "MailingGroupForm(request.POST)"
        if form:
            pass