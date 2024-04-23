import random, barcode, logging, qrcode
from events.models import TicketModel, TicketOrderModel, EventModel
from io import BytesIO
from django.urls import reverse
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from weasyprint import HTML
from barcode.writer import ImageWriter
from django.http import HttpResponse

logger = logging.getLogger("utils")

def create_new_barcode_number():
    not_unique = True
    while not_unique:
        unique_ref = random.randint(1000000000, 9999999999)
        if not TicketModel.objects.filter(barcode_value=str(unique_ref)).exists():
            not_unique = False
    return str(unique_ref)

def generate_qr_and_bacode(order: TicketOrderModel, request):
    try:
        order_url = request.build_absolute_uri(reverse("events:manage-ticket-order", kwargs={"order_id": order.id}))
        for ticket in TicketModel.objects.filter(ticket_order=order):
            
            barcode_value = create_new_barcode_number()
            barcode_image = barcode.Code128(barcode_value, writer=ImageWriter())
            barcode_image.save(f'media/tickets/barcodes/' + order.order_number)
                    
            qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
            
            qr.add_data(order_url)
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image.save(f'media/tickets/qrcodes/' + order.order_number + '_qrcode.png')
            
            ticket.qrcode_url = order_url
            ticket.barcode_value = barcode_value
            ticket.qrcode_image = f'tickets/qrcodes/' + order.order_number + '_qrcode.png'
            ticket.barcode_image = f'tickets/barcodes/' + order.order_number + '.png'
            ticket.save(update_fields=["qrcode_url", "barcode_value", "qrcode_image", "barcode_image"])
        
        return True

    except Exception as ex:
        logger.error(ex)
        return False

def generate_guests_list(orders, event:EventModel, domain, protocol):
    try:
        template = get_template("ticket/guests.html")
        context = {"orders": orders, 
                    "event": event,
                    "domain": domain, 
                    "protocol": protocol}
        
        render_template = template.render(context)
        pdf_file = HTML(string=render_template).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{event.title}_Guest_List.pdf"'

        return response
    except Exception as ex:
        logger.error(ex)
        return False

def generate_tickets_in_pdf(order: TicketOrderModel, request):
    try:
        domain = get_current_site(request).domain
        protocol = "https" if request.is_secure() else "http"
        template = get_template("ticket/tickets.html")
        context = {"tickets": TicketModel.objects.filter(ticket_order=order), 
                    "event": order.event, 
                    "buyer_full_name": order.buyer.get_full_name(),
                    "order_number": order.order_number,
                    "created": order.created,
                    "domain": domain, 
                    "protocol": protocol}
        
        render_template = template.render(context)
        pdf_file = HTML(string=render_template).write_pdf()
            
        buffer = BytesIO(pdf_file)

        order.tickets_pdf_file.save(f'{order.order_number}_tickets.pdf', buffer)
        return True
    except Exception as ex:
        logger.error(ex)
        return False
    