from django import forms
from accounts.utils import IdentityNumberChoices, validate_sa_id_number, validate_sa_passport_number
from accounts.models import CustomUserModel, IdentityVerificationModel
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm,  UserCreationForm)

User = CustomUserModel

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
    
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'id': 'id_username'}), label="Username or Email*")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'id': 'id_password'}))

class RegistrationForm(UserCreationForm):
    identity_choices = forms.ChoiceField(choices=IdentityNumberChoices.choices, widget=forms.RadioSelect, initial=IdentityNumberChoices.ID_NUMBER)
    confirm_email = forms.EmailField(help_text="Confirm your email address", required=True, widget=forms.EmailInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}))

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'title', 'first_name', 'last_name', 'maiden_name', 'profile_image', "occupation", "professional_affiliations", 'identity_number', "address_one", "address_two", "city", "country", "province", "zipcode")

        widgets = {
            'username': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'email': forms.EmailInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'title': forms.Select(attrs={"class": "block p-2 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'confirm_email': forms.EmailInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'first_name': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'maiden_name': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'last_name': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            #'hobbies': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'password2': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'address_one': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'address_two': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'city': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'country': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'province': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'zipcode': forms.NumberInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"})
            
        }

    def clean_email(self):
        email = self.cleaned_data["email"]

        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError(f'This email: {email} is already in use.')
        
        return email
    
    def clean(self):
        clean = super().clean()
        identity_choice = clean.get('identity_choices', None)
        identity_number = clean.get('identity_number', None)
        # second_email = clean["confirm_email"]
        # mail = clean["email"]

        # if mail != second_email:
        #     raise forms.ValidationError(f'This email: {mail} does not match with confirmation email.')
        if identity_number and identity_choice:
            if identity_choice == IdentityNumberChoices.ID_NUMBER:
                message = validate_sa_id_number(identity_number)
                if message["success"] == False:
                    raise forms.ValidationError(message["message"])
            else:
                if not validate_sa_passport_number(identity_number):
                    raise forms.ValidationError("Your passport number is invalid")
                
        return clean

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()

        return user

class AccountUpdateForm(forms.ModelForm):
    identity_choices = forms.ChoiceField(choices=IdentityNumberChoices.choices, widget=forms.RadioSelect, initial=IdentityNumberChoices.ID_NUMBER)
    class Meta:
        model = get_user_model()
        fields = ["title", "profile_image", "first_name", "last_name", 'maiden_name', "hobbies", "biography", "occupation", "professional_affiliations", "identity_number"]

        widgets = {
            'username': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'title': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'first_name': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'maiden_name': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'last_name': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            #'hobbies': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            
        }

    def __init__(self, *args, **kwargs):
        super(AccountUpdateForm, self).__init__(*args, **kwargs)
        for field_name, field_value in self.initial.items():
            if field_value is None:
                self.initial[field_name] = ''
    
    def clean(self):
        clean = super().clean()
        identity_choice = clean["identity_choices"]
        identity_number = clean["identity_number"]
        
        if identity_choice == IdentityNumberChoices.ID_NUMBER:
            message = validate_sa_id_number(identity_number)
            if message["success"] == False:
                raise forms.ValidationError(message["message"])
        else:
            if not validate_sa_passport_number(identity_number):
                raise forms.ValidationError("Your passport number is invalid")
            
        return clean
    
class GeneralEditForm(forms.ModelForm):
    """
        Form to edit only username and email
    """
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "phone", "address_one", "address_two", "city", "country", "province", "zipcode"]

        widgets = {
            'address_one': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'address_two': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'city': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'country': forms.TextInput(attrs={"value": "South Africa", "class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'province': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'zipcode': forms.NumberInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"})
        }

    def __init__(self, *args, **kwargs):
        super(GeneralEditForm, self).__init__(*args, **kwargs)
        for field_name, field_value in self.initial.items():
            if field_value is None:
                self.initial[field_name] = ''

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get("email")
        if get_user_model().objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError(f'This username: {username} is already in use.')
        
        if get_user_model().objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError(f'This email: {email} is already in use.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super(GeneralEditForm, self).save(commit=False)
        email = self.cleaned_data['email']
        if commit:
            user.save()
            
        return user
    
class VerificationForm(forms.ModelForm):
    class Meta:
        model = IdentityVerificationModel
        fields = ("identity_image", "identitybook_image")

