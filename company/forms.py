from django import forms
from django.contrib.auth import get_user_model
from tinymce.widgets import TinyMCE
from home.models import PostModel
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

class PostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ("title", "image", "content", "category")

        widgets = {
            'title': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "placeholder": "e.g John Snow's 30th Birthday"}),
            'category': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'image': forms.FileInput(attrs={"class": "w-[0.1px] h-[0.1px] opacity-0 overflow-hidden absolute -z-[1]"}),
            'content': TinyMCE(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "rows": 8}),
        }