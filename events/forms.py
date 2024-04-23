from django import forms
from events.models import EventModel, TicketOrderModel, EventTicketTypeModel, TicketModel, EVENT_CATEGORIES
from tinymce.widgets import TinyMCE

class EventForm(forms.ModelForm):
    class Meta:
        model = EventModel
        fields = ("image", "title", "category", "content", "venue_name", "tip", "event_address", "map_coordinates", "event_startdate", "event_enddate", "event_link")

        widgets = {
            'title': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "placeholder": "e.g John Snow's 30th Birthday"}),
            'tip': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'category': forms.Select(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'image': forms.FileInput(attrs={"class": "w-[0.1px] h-[0.1px] opacity-0 overflow-hidden absolute -z-[1]"}),
            'map_coordinates': forms.HiddenInput(),
            'venue_name': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "placeholder": "e.g John Snow Hall, Next to Asgard"}),
            'event_link': forms.URLInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "placeholder": "e.g https://www.eventtitle.co.za"}),
            'event_address': forms.TextInput(attrs={"class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150", "placeholder": "e.g Durban St, Durban, 4312, KZN"}),
            'event_startdate': forms.DateTimeInput(attrs={"type": "text", "step": "any", "class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'content': TinyMCE(attrs={"class": "border-0 px-3 py-3 {% if form.content.errors %} h-44 border-2 border-red-500{% endif %} placeholder-gray-300 text-gray-600 bg-white rounded text-sm shadow focus:outline-none focus:ring w-full ease-linear transition-all duration-150", "rows": 8}),
            'event_enddate': forms.DateTimeInput(attrs={"type": "text", "step": "any", "class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"})
        }
            
  
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("event_startdate")
        end_date = cleaned_data.get("event_enddate")
        if start_date and end_date and start_date == end_date:
            raise forms.ValidationError("Event start and end times cannot be the same.")
        
        if end_date.date() < start_date.date():
            raise forms.ValidationError("Start date cannot be greater than end date")
        
        return cleaned_data
        
        
class EventTicketTypeForm(forms.ModelForm):
    class Meta:
        model = EventTicketTypeModel
        fields = ("title", "available_seats", "price", "sale_start", "sale_end")

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'type': 'text', 
                    'class': 'block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150'
                    }
                ),
            'available_seats': forms.NumberInput(
                attrs={
                    'type': 'number', 
                    'class': 'block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150'
                    }
                ),
            'price': forms.NumberInput(
                attrs={
                    'type': 'number',
                    'step': '0.01',
                    'class': 'block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150'
                    }
                ),
            
            'sale_start': forms.DateTimeInput(attrs={"type": "datetime-local", "class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            'sale_end': forms.DateTimeInput(attrs={"type": "datetime-local", "class": "block p-3 md:text-base w-full text-sm text-custom-h outline-none placeholder:text-gray-400 bg-gray-50 rounded-lg border border-gray-300 focus:ring-custom-primary focus:border-custom-primary ease-linear transition-all duration-150"}),
            
        }

class TicketOrderForm(forms.ModelForm):
    class Meta:
        model = TicketOrderModel
        fields = ("accepted_laws", "email", "quantity", "total_price")

class TicketForm(forms.ModelForm):
    class Meta:
        model = TicketModel
        exclude=["id"]
        fields = ("quantity", "ticket_type", "guest_email", "guest_full_name")
