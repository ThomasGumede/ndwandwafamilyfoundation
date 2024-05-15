from django import forms
from django.contrib.auth import get_user_model
from campaigns.models import CampaignModel
from accounts.models import WalletModel
from events.models import EventModel

class CampaignUpdateStatusForm(forms.ModelForm):
    class Meta:
        model = CampaignModel
        fields = ("status", )

        widget = {
            'status': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-white rounded-md rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
        }

class EventUpdateStatusForm(forms.ModelForm):
    class Meta:
        model = EventModel
        fields = ("status", )

        widget = {
            'status': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-white rounded-md rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
        }

class WalletStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = WalletModel
        fields = ("status", )