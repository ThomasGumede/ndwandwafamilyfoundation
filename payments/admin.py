from django.contrib import admin
from payments.models import NdwandwaBankModel, PaymentInformation

@admin.register(NdwandwaBankModel)
class NdwandwaBankAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentInformation)
class PaymentInformation(admin.ModelAdmin):
    pass
    
