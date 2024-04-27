from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from accounts.models import CompanyModel
from home.models import CategoryModel

company: CompanyModel = CompanyModel.objects.all()[0]
def global_context(request):
    PROTOCOL = "https" if request.is_secure() else "http"
    DOMAIN = get_current_site(request).domain

    context = {
        'domain' : DOMAIN,
        'protocol': PROTOCOL,
        "categories": CategoryModel.objects.all(),
    }

    if company:
        context["company"] = company
        context["facebook"] = company.facebook
        context["twitter"] = company.twitter
        context["linkedIn"] = company.linkedIn
        context["company_support"]: company.phone # type: ignore
        context["company_support_mail"]: company.support_email  # type: ignore
        context["company_street_address_1"] = company.address_one
        context["company_city"] = company.city
        context["company_state"] = company.province

    return context

