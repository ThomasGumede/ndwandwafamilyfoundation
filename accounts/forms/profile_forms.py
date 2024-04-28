from accounts.models import MailingGroupModel, QualificationModel, RelativeModel
from django import forms
from django.contrib.auth import get_user_model

from accounts.utils import RelationShip

class QualificationForm(forms.ModelForm):
    class Meta:
        model = QualificationModel
        fields = ['institution', 'title', 'qualification_type', 'year']

        widgets = {
            'title': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "placeholder": "e.g Dip in Science"}),
            'qualification_type': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            
        }

    def clean(self):
        clean = super().clean()
        name = clean.get("title", None)
        last_name = clean.get("institution", None)
        other_surname = clean.get("year", None)
        qual_type = clean.get("qualification_type", None)
        relative = QualificationModel.objects.filter(title = name, institution = last_name, year = other_surname, qualification_type= qual_type).exists()

        if relative:
            raise forms.ValidationError("Qualification with following details already exists")

        return clean
    
class QualificationUpdateForm(forms.ModelForm):
    class Meta:
        model = QualificationModel
        fields = ['institution', 'title', 'qualification_type', 'year']

        widgets = {
            'title': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "placeholder": "e.g Dip in Science"}),
            'qualification_type': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            
        }

class RelativeForm(forms.ModelForm):
    class Meta:
        model = RelativeModel
        fields = ['title', 'surname', 'full_name', 'profile_image', 'relationship', 'phone', 'gender', 'relative_side', 'maiden_name', 'description']

        widgets = {
            'profile_image': forms.FileInput(attrs={"class": "w-[0.1px] h-[0.1px] opacity-0 overflow-hidden absolute -z-[1]"}),
            'title': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'full_name': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'surname': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'maiden_name': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'relationship': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'relative_side': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'gender': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
        }

    def clean_relative_side(self):
        clean = self.cleaned_data
        relation = clean.get('relationship', None)
        relation_side = clean.get('relative_side', None)
        relation_list = [RelationShip.GRANDMOTHER, RelationShip.GRANDFATHER, RelationShip.STEPBROTHER, RelationShip.STEPSISTER ,RelationShip.NIECE, RelationShip.NEPHEW, RelationShip.GREATGRANDFATHER, RelationShip.GREATGRANDMOTHER, RelationShip.GREATGREATGRANDFATHER, RelationShip.GREATGREATGRANDMOTHER]
        
        if relation and relation in relation_list and relation_side == None:
            raise forms.ValidationError(f'Please choose relationship side of your {relation}')
        
        return relation_side
    
    def __init__(self, *args, **kwargs):
        super(RelativeForm, self).__init__(*args, **kwargs)
        for field_name, field_value in self.initial.items():
            if field_value is None:
                self.initial[field_name] = ''

    def clean(self):
        clean = super().clean()
        name = clean.get("full_name", None)
        last_name = clean.get("surname", None)
        other_surname = clean.get("maiden_name", None)
        relation = clean.get("relationship", None)
        gender = clean.get("gender", None)
        relative = RelativeModel.objects.filter(full_name = name, surname = last_name, maiden_name = other_surname, gender=gender, relationship = relation).exists()

        if relative:
            raise forms.ValidationError(f"Relative with following details already exists")

        return clean

class RelativeUpdateForm(forms.ModelForm):
    class Meta:
        model = RelativeModel
        fields = ['title', 'surname', 'full_name', 'profile_image', 'relationship', 'phone', 'gender', 'relative_side', 'maiden_name', 'description']

        widgets = {
            'title': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'full_name': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'surname': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'maiden_name': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'relationship': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'relative_side': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'gender': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
        }

    def clean_relative_side(self):
        clean = self.cleaned_data
        relation = clean.get('relationship', None)
        relation_side = clean.get('relative_side', None)
        relation_list = [RelationShip.GRANDMOTHER, RelationShip.GRANDFATHER, RelationShip.STEPBROTHER, RelationShip.STEPSISTER ,RelationShip.NIECE, RelationShip.NEPHEW, RelationShip.GREATGRANDFATHER, RelationShip.GREATGRANDMOTHER, RelationShip.GREATGREATGRANDFATHER, RelationShip.GREATGREATGRANDMOTHER]
        
        if relation and relation in relation_list and relation_side == None:
            raise forms.ValidationError(f'Please choose relationship side of your {relation}')
        
        return relation_side
    
    def __init__(self, *args, **kwargs):
        super(RelativeUpdateForm, self).__init__(*args, **kwargs)
        for field_name, field_value in self.initial.items():
            if field_value is None:
                self.initial[field_name] = ''

class SocialLinksForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("facebook", "twitter", "instagram", "linkedIn")

class SubscribeForm(forms.Form):
    mailinggroups = forms.ModelMultipleChoiceField(queryset=MailingGroupModel.objects.all(), required=False,widget=forms.CheckboxSelectMultiple(attrs={"required": False}))