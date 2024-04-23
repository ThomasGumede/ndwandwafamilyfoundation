from django import forms
from home.models import CommentModel, EmailModel

class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ("comment", )

class SearchForm(forms.Form):
    SEARCH_CHOICES = (
        ("campaigns", "campaigns"),
        ("events", "events"),
        ("news", "news"),
        ("people", "people"),
    )
    search_by = forms.ChoiceField(choices=SEARCH_CHOICES, required=False, widget=forms.Select(attrs={"class": "bg-gray-50 outline-none focus:outline-none border-none p-4 border rounded-md text-lg text-black focus:border-none h-full"}))
    query = forms.CharField(widget=forms.TextInput(attrs={"type": "search", "class": "bg-gray-50 outline-none focus:outline-none border-none p-2 py-2 rounded-md text-lg text-black focus:border-none h-full"}))

class EmailForm(forms.ModelForm):
    class Meta:
        model = EmailModel
        fields = ('from_email', 'phone', 'name', 'message', 'subject')

        widgets = {
            "from_email": forms.EmailInput(attrs={"class": "text-body-color border-[#f0f0f0] focus:border-primary w-full rounded border py-3 px-[14px] text-base outline-none focus-visible:shadow-none", "placeholder": "Your email"}),
            "subject": forms.TextInput(attrs={"class": "text-body-color border-[#f0f0f0] focus:border-primary w-full rounded border py-3 px-[14px] text-base outline-none focus-visible:shadow-none", "placeholder": "Email subject"}),
            "name": forms.TextInput(attrs={"class": "text-body-color border-[#f0f0f0] focus:border-primary w-full rounded border py-3 px-[14px] text-base outline-none focus-visible:shadow-none", "placeholder": "Your name"}),
            "phone": forms.TextInput(attrs={"class": "text-body-color border-[#f0f0f0] focus:border-primary w-full rounded border py-3 px-[14px] text-base outline-none focus-visible:shadow-none", "type": "tel", "placeholder": "Your phone"}),
            "message": forms.Textarea(attrs={"class": "text-body-color border-[#f0f0f0] focus:border-primary w-full resize-none rounded border py-3 px-[14px] text-base outline-none focus-visible:shadow-none", "placeholder": "Your message", "row": "6"}),
        }