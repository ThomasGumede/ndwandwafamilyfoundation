from django import forms
from campaigns.models import CampaignModel, ContributionModel, CampaignUpdateModel
from tinymce.widgets import TinyMCE

class CampaignForm(forms.ModelForm):
    class Meta:
        model = CampaignModel
        fields = ("category", "title", "details", "target", "start_date", "end_date", "image")
        widgets = {
            'title': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "placeholder": "e.g John Snow's 30th Birthday"}),
            'target': forms.NumberInput(attrs={"step": "0.01", "class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'category': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'image': forms.FileInput(attrs={"class": "w-[0.1px] h-[0.1px] opacity-0 overflow-hidden absolute -z-[1]"}),
            'details': TinyMCE(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "rows": 8}),
            'start_date': forms.DateTimeInput(attrs={"type": "text", "class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "step": "any"}),
            'end_date': forms.DateTimeInput(attrs={"type": "text", "class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "step": "any"})
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and start_date == end_date:
            raise forms.ValidationError("Campaign start and end times cannot be the same.")
        
        if end_date.date() < start_date.date():
            raise forms.ValidationError("Start date cannot be greater than end date")
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)
        for field_name, field_value in self.initial.items():
            if field_value is None:
                self.initial[field_name] = ''

class ContributionForm(forms.ModelForm):
    class Meta:
        model = ContributionModel
        fields = ("amount", "tip", "anonymous", "accepted_laws", "message")

class CampaignUpdateForm(forms.ModelForm):
    class Meta:
        model = CampaignUpdateModel
        fields = ("title", "content")

        widgets = {
            'title': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "placeholder": "e.g John Snow's 30th Birthday"}),
            }