from django import forms
from business.models import Business, BusinessContent, BusinessHour, BusinessReview
from tinymce.widgets import TinyMCE

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = (
            "title", "background_image", "logo", 
            "details", "slogan", "category", "bbbee_level", 
            "map_coordinates", "phone", "website", "email",
            "operation", "address_one", "address_two", 
            "city", "province", "zipcode",
            "facebook", "twitter", "instagram", "linkedIn"
        )

        widgets = {
            'background_image': forms.FileInput(attrs={"class": "w-[0.1px] h-[0.1px] opacity-0 overflow-hidden absolute -z-[1]"}),
            'logo': forms.FileInput(attrs={"class": "w-[0.1px] h-[0.1px] opacity-0 overflow-hidden absolute -z-[1]"}),
            'map_coordinates': forms.HiddenInput(),
            'website': forms.URLInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "placeholder": "e.g https://www.business.co.za"}),
            'slogan': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'email': forms.EmailInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'category': forms.Select(attrs={"class": "block p-2 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'operation': forms.HiddenInput(attrs={"value": "CUSTOM"}),
            'bbbee_level': forms.Select(attrs={"class": "block p-2 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'title': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'address_one': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'address_two': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'city': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'province': forms.TextInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"}),
            'details': TinyMCE(attrs={"class": "border-0 px-3 py-3 {% if form.content.errors %} h-44 border-2 border-red-500{% endif %} placeholder-gray-300 text-gray-600 bg-white rounded text-sm shadow focus:outline-none focus:ring w-full ease-linear transition-all duration-150", "rows": 8}),
            'zipcode': forms.NumberInput(attrs={"class": "block p-2 md:text-base w-full text-sm text-gray-900 outline-none bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary placeholder:text-gray-400 focus:border-custom-primary ease-linear transition-all duration-150"})
            
        }

class BusinessHourForm(forms.ModelForm):
    class Meta:
        model = BusinessHour
        exclude=["id"]
        fields = ("day", "open_time", "close_time", "operating")

class BusinessReviewForm(forms.ModelForm):
    class Meta:
        model = BusinessReview
        fields = ("comment", "commenter_full_names", "commenter_email")

        widget = {
            'comment': forms.Textarea(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "rows": 8}),
        }