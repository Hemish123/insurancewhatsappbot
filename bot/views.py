from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from bot.services.whatsapp_service import send_whatsapp_message
from bot.services.renewal_service import run_renewal
import time
from bot.models import Customer
from bot.models import Customer, ChatMessage

@api_view(["GET"])
def test_send_message(request):

    phone = "919104142402"  # your number with country code
    message = "Hello 👋 This is test message from Django bot"

    result = send_whatsapp_message(phone, message)

    return Response({
        "status": "message sent",
        "response": result
    })


@api_view(["GET"])
def run_renewal_api(request):

    run_renewal()

    return Response({"status": "renewal messages sent"})


@api_view(["POST"])
def whatsapp_webhook(request):
    data = request.data

    try:
        if data.get("event") != "messages.received":
            return Response({"status": "ignored"})

        message_data = data.get("data", {}).get("messages", {})

        phone = message_data.get("key", {}).get("cleanedSenderPn")
        text = message_data.get("messageBody", "").lower()
        # 🔥 ADD HERE
        print("PHONE FROM WEBHOOK:", phone)

        customer = Customer.objects.filter(phone=phone).first()
        print("CUSTOMER FOUND:", customer)



        # 🔥 Normalize text
        text = text.lower().strip()

        # 🔥 Get customer
        customer = Customer.objects.filter(phone=phone).first()

        if not customer:
            return Response({"status": "user not found"})

        ChatMessage.objects.create(
            customer=customer,
            message=text,
            sender="user"
        )

        # ================================
        # 🔥 NEW: GREETING / CLOSING LOGIC
        # ================================
        CLOSING_KEYWORDS = [
            "ok", "okay", "okk", "okkk",
            "thank you", "thanks", "thankyou",
            "bye", "bye bye", "goodbye",
            "thx", "ty"
        ]

        if any(word in text for word in CLOSING_KEYWORDS):

            reply = """You're welcome 😊"""

            send_whatsapp_message(phone, reply)

            ChatMessage.objects.create(
                customer=customer,
                message=reply,
                sender="bot"
            )

            # 🔥 mark conversation closed
            customer.conversation_state = "closed"
            customer.save()

            return Response({"status": "closed"})
        # ================================

        state = customer.conversation_state

        # 🟢 POSITIVE INTENT
        positive_intent = any(word in text for word in [
            "yes", "yeah", "yup", "ok", "okay", "sure",
            "renew", "please renew", "do it", "go ahead"
        ])

        # 🔴 NEGATIVE INTENT
        negative_intent = any(word in text for word in [
            "no", "nope", "not now", "later", "maybe later",
            "don't", "do not", "not interested"
        ])

        if not phone or not text:
            return Response({"status": "no data"})



        import time
        time.sleep(5)

        # ----------------------------
        # STATE: INITIAL
        # ----------------------------
        if state == "initial":

            if positive_intent:

                reply = """Great! 😊

I’ll help you renew your policy.

Here’s your secure payment link:
🔗 https://your-payment-link.com

"""

                customer.conversation_state = "done"

            elif negative_intent:

                reply = """No worries 😊

Would you like me to remind you again later?"""

                customer.conversation_state = "ask_reminder"

            else:
                reply = """I’m here to help 😊

Would you like to renew your policy now?"""

        # ----------------------------
        # STATE: ASK REMINDER
        # ----------------------------
        elif state == "ask_reminder":

            if positive_intent:

                reply = """Got it 👍

I’ll remind you again before your policy expires.

You don’t have to worry 😊"""

                customer.conversation_state = "done"

            elif negative_intent:

                reply = """Alright 😊

If you need anything later, feel free to reach out.

Take care! 👋"""

                customer.conversation_state = "done"

            else:
                reply = """Just to confirm 😊

Should I remind you again later?"""

        # ----------------------------
        # STATE: DONE
        # ----------------------------
        else:
            reply = """I’m here if you need any help 😊"""

        customer.save()

        send_whatsapp_message(phone, reply)

        ChatMessage.objects.create(
            customer=customer,
            message=reply,
            sender="bot"
        )

    except Exception as e:
        print("ERROR:", str(e))

    return Response({"status": "received"})


from bot.models import Customer, ChatMessage

@api_view(["GET"])
def get_conversations(request):

    customers = Customer.objects.all()

    data = []

    for c in customers:
        last_msg = ChatMessage.objects.filter(customer=c).order_by('-timestamp').first()

        data.append({
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "last_message": last_msg.message if last_msg else ""
        })

    return Response({"conversations": data})

@api_view(["GET"])
def get_messages(request, customer_id):

    messages = ChatMessage.objects.filter(customer_id=customer_id).order_by('timestamp')

    data = []

    for m in messages:
        data.append({
            "message": m.message,
            "sender": m.sender,
            "time": m.timestamp
        })

    return Response({"messages": data})

@api_view(["POST"])
def send_message_dashboard(request):

    from bot.services.whatsapp_service import send_whatsapp_message

    customer_id = request.data.get("customer_id")
    message = request.data.get("message")

    customer = Customer.objects.get(id=customer_id)

    # send message
    send_whatsapp_message(customer.phone, message)

    # save message
    ChatMessage.objects.create(
        customer=customer,
        message=message,
        sender="bot"
    )

    return Response({"status": "sent"})


from bot.models import Customer, ChatMessage
from django.db.models import Min, Max, Count

@api_view(["GET"])
def dashboard_data(request):

    total_customers = Customer.objects.count()
    total_messages = ChatMessage.objects.count()
    total_conversations = Customer.objects.count()  # one per customer

    customers = Customer.objects.all()

    table_data = []

    for c in customers:

        msgs = ChatMessage.objects.filter(customer=c)

        first_msg = msgs.order_by('timestamp').first()
        last_msg = msgs.order_by('-timestamp').first()

        table_data.append({
            "id": c.id,
            "phone": c.phone,
            "name": c.name,
            "first_contact": first_msg.timestamp if first_msg else None,
            "last_contact": last_msg.timestamp if last_msg else None,
        })

    return Response({
        "total_customers": total_customers,
        "total_messages": total_messages,
        "total_conversations": total_conversations,
        "customers": table_data
    })

import os
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone

from bot.models import UploadedFile, Customer
from bot.services.whatsapp_service import send_whatsapp_message
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(["POST"])
@authentication_classes([])   # disable session auth
@permission_classes([AllowAny])
def upload_file(request):
    file = request.FILES.get("file")

    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    # ✅ Save file
    obj = UploadedFile.objects.create(file=file)

    file_path = obj.file.path
    ext = os.path.splitext(file_path)[1].lower()

    customers = []

    # ---------------- EXCEL ----------------
    if ext in [".xlsx", ".xls"]:
        import pandas as pd

        df = pd.read_excel(file_path)

        print("COLUMNS:",df.columns)

        for _, row in df.iterrows():

            expiry = row.get("policy_expiry")   # ✅ CORRECT COLUMN

            print("RAW EXPIRY:",expiry,type(expiry))

            # ✅ HANDLE DATETIME CORRECTLY
            # ✅ BEST PRACTICE conversion
            if pd.notnull(expiry):
                try:
                    expiry = pd.to_datetime(expiry, errors="coerce")

                    if pd.notnull(expiry):
                        expiry = expiry.date()
                    else:
                        expiry = None

                except Exception as e:
                    print("DATE ERROR:", e)
                    expiry = None
            else:
                expiry = None

            name = row.get("name") or "Customer"
            phone = str(row.get("phone") or "").strip()

            if not phone:
                continue

            customers.append({
                "name": name,
                "phone": phone,
                "policy_type": "Insurance",
                "expiry_date": expiry
            })

    # ---------------- PDF ----------------
    elif ext == ".pdf":
        from PyPDF2 import PdfReader

        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text()

        # ⚠️ Simple parsing (you can improve later)
        lines = text.split("\n")

        for line in lines:
            parts = line.split(",")

            if len(parts) >= 2:
                customers.append({
                    "name": parts[0],
                    "phone": parts[1],
                    "policy_type": "Insurance",
                    "expiry_date": expiry
                })

    # ---------------- WORD ----------------
    elif ext == ".docx":
        import docx

        doc = docx.Document(file_path)

        for para in doc.paragraphs:
            parts = para.text.split(",")

            if len(parts) >= 3:
                expiry = parts[2].strip()
            else:
                expiry = None

            # convert to date
            import pandas as pd
            expiry = pd.to_datetime(expiry, errors="coerce")

            if pd.notnull(expiry):
                expiry = expiry.date()
            else:
                expiry = None

            customers.append({
                "name": parts[0],
                "phone": parts[1],
                "policy_type": "Insurance",
                "expiry_date": expiry
            })

    else:
        return Response({"error": "Unsupported file type"}, status=400)

    # ---------------- SAVE ONLY ----------------
    for c in customers:

        customer, created = Customer.objects.get_or_create(
            phone=c["phone"],
            defaults={
                "name": c["name"],
                "policy_type": c["policy_type"],
                "expiry_date": c["expiry_date"]
            }
        )

        if not created:
            customer.expiry_date = c["expiry_date"]
            customer.name = c["name"]
            customer.policy_type = c["policy_type"]

        customer.conversation_state = "initial"
        customer.reminder_sent = False
        customer.save()


    # 🔥 NOW CALL RENEWAL
    from bot.services.renewal_service import run_renewal

    print("CALLING RENEWAL...")
    run_renewal()

    return Response({"status": "file processed & messages sent"})


def dashboard_view(request):
    return render(request, "dashboard.html")

def upload_page_view(request):
    return render(request, "upload.html")

# @api_view(["POST"])
# def whatsapp_webhook(request):
#     data = request.data

#     print("INCOMING MESSAGE:", data)

#     try:
#         if data.get("event") != "messages.received":
#             return Response({"status": "ignored"})

#         message_data = data.get("data", {}).get("messages", {})

#         phone = message_data.get("key", {}).get("cleanedSenderPn")
#         text = message_data.get("messageBody", "").lower()

#         print("PHONE:", phone)
#         print("TEXT:", text)

#         if phone and text:

#             import time
#             time.sleep(5)

#             # 🟢 POSITIVE INTENT
#             if any(word in text for word in ["yes", "yeah", "ok", "sure", "renew", "done"]):

#                 reply = """Great! 😊

# I’ll help you renew your policy.

# Here’s your secure payment link:
# 🔗 https://your-payment-link.com

# Once done, just reply *Done* and I’ll confirm it for you 👍"""

#             # 🔴 NEGATIVE INTENT
#             elif any(word in text for word in ["no", "not now", "later"]):

#                 reply = """No worries 😊

# Would you like me to remind you again later?"""

#             # 🟡 REMINDER CONFIRMATION
#             elif "remind" in text:

#                 reply = """Got it 👍

# I’ll remind you again before your policy expires.

# You don’t have to worry 😊"""

#             # 🤖 DEFAULT HUMAN RESPONSE
#             else:
#                 reply = """I’m here to help 😊

# Would you like to renew your policy now?"""

#             send_whatsapp_message(phone, reply)

#     except Exception as e:
#         print("ERROR:", str(e))

#     return Response({"status": "received"})

