# from bot.services.expiry_service import get_expiring_customers
# from bot.services.whatsapp_service import send_whatsapp_message

# def run_renewal():

#     customers = get_expiring_customers()

#     for c in customers:

#         message = f"""
# Hello {c.name} 👋

# Your {c.policy_type} policy will expire on {c.expiry_date}.

# Please renew your policy.
# """

#         print(f"Sending to {c.phone}")

#         send_whatsapp_message(c.phone, message)

#         c.reminder_sent = True
#         c.save()




from bot.services.expiry_service import get_expiring_customers
from bot.services.whatsapp_service import send_whatsapp_message
from bot.models import ChatMessage
import time

def run_renewal():

    customers = get_expiring_customers()

    print("FINAL CUSTOMERS TO SEND:", customers)

    for c in customers:

        message = f"""
Hello {c.name} 👋

Your {c.policy_type} policy will expire on {c.expiry_date}.

Do you want to renew your policy?
"""

        print("Sending to:", c.phone)

        send_whatsapp_message(c.phone, message)


        ChatMessage.objects.create(
            customer=c,
            message=message,
            sender="bot"
        )

        c.reminder_sent = True
        c.save()

        time.sleep(2)