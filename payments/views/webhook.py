import json, logging, requests, hashlib, base64, hmac
from django.shortcuts import render, redirect
from payments.models import PaymentInformation
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.urls import reverse
from payments.utils import headers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

logger = logging.getLogger("payments")

@csrf_exempt
def webhook(request):
    try:
        if request.method == 'POST':
            headers = request.headers
            id = headers.get('webhook-id')
            timestamp = headers.get('webhook-timestamp')
            

            # signatures = request.META["webhook-signature"]
            signed_content = str(id) + '.' + str(timestamp) + '.' + str(request.body.decode('utf-8'))
            secret = settings.YOCO_WEBHOOK_KEY
            secret_bytes = base64.b64decode(secret.split('_')[1])
            hmac_signature = hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
            expected_signature = base64.b64encode(hmac_signature).decode()

            # Compare the signatures
            signature = headers.get('webhook-signature').split(' ')[0].split(',')[1]
            
            if hmac.compare_digest(signature, expected_signature):
                body_dict = json.loads(request.body.decode('utf-8'))
                payload = body_dict["payload"]
                metadata = payload["metadata"]
                paymentinformation, created = PaymentInformation.objects.get_or_create(id=metadata["checkoutId"], data=json.dumps(body_dict))
                if created or paymentinformation is not None:
                    return HttpResponse(status=200)
            
            return HttpResponse(status=403)
        else:
            logger.error(request.body)
            return HttpResponse(status=403)
    except Exception as err:

        logger.error(f"Webhook - {err}")
        return HttpResponse(status=403)

@login_required  
def create_webhook(request):
    if request.user.is_superuser and request.user.is_technical:
        data = {
                    "name": "Ndwandwafam_signal_test",
                    "url": request.build_absolute_uri(reverse('payments:webhook'))
                }
        try:
            response = requests.request("POST", "https://payments.yoco.com/api/webhooks", data=json.dumps(data), headers=headers)
            
            response.raise_for_status()
            new_respone = response.json()
            return JsonResponse(new_respone)
        except requests.ConnectionError as err:
            return render(request, "payments/timeout.html", {"err": err})
            
        except requests.HTTPError as err:
            return render(request, "payments/error.html", {"message": "Your payment was not processed due to internal error from our payment system, Please try again later"})
        
    else:
        return redirect("home:home")
    