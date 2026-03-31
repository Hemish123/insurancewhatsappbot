# from django.shortcuts import render

# # Create your views here.
# from rest_framework.decorators import api_view, authentication_classes
# from rest_framework.response import Response
# from bot.services.whatsapp_service import send_whatsapp_message
# from bot.services.renewal_service import run_renewal
# import time
# from bot.models import Customer
# from bot.models import Customer, ChatMessage

# @api_view(["GET"])
# def test_send_message(request):

#     phone = "919104142402"  # your number with country code
#     message = "Hello 👋 This is test message from Django bot"

#     result = send_whatsapp_message(phone, message)

#     return Response({
#         "status": "message sent",
#         "response": result
#     })


# @api_view(["GET"])
# def run_renewal_api(request):

#     run_renewal()

#     return Response({"status": "renewal messages sent"})


# @api_view(["POST"])
# def whatsapp_webhook(request):
#     data = request.data

#     try:
#         if data.get("event") != "messages.received":
#             return Response({"status": "ignored"})

#         message_data = data.get("data", {}).get("messages", {})

#         phone = message_data.get("key", {}).get("cleanedSenderPn")
#         text = message_data.get("messageBody", "").lower()
#         # 🔥 ADD HERE
#         print("PHONE FROM WEBHOOK:", phone)

#         # customer = Customer.objects.filter(phone=phone).first()
#         # print("CUSTOMER FOUND:", customer)



#         # 🔥 Normalize text
#         text = text.lower().strip()

#         # 🔥 Get customer
#         customer = Customer.objects.filter(phone=phone).first()

#         if not customer:
#             return Response({"status": "user not found"})

#         ChatMessage.objects.create(
#             customer=customer,
#             message=text,
#             sender="user"
#         )

#         # ================================
#         # 🔥 NEW: GREETING / CLOSING LOGIC
#         # ================================
#         CLOSING_KEYWORDS = [
#             "ok", "okay", "okk", "okkk",
#             "thank you", "thanks", "thankyou",
#             "bye", "bye bye", "goodbye",
#             "thx", "ty"
#         ]

#         if any(word in text for word in CLOSING_KEYWORDS):

#             reply = """You're welcome 😊"""

#             send_whatsapp_message(phone, reply)

#             ChatMessage.objects.create(
#                 customer=customer,
#                 message=reply,
#                 sender="bot"
#             )

#             # 🔥 mark conversation closed
#             customer.conversation_state = "closed"
#             customer.save()

#             return Response({"status": "closed"})
#         # ================================

#         state = customer.conversation_state

#         # 🟢 POSITIVE INTENT
#         positive_intent = any(word in text for word in [
#             "yes", "yeah", "yup", "ok", "okay", "sure",
#             "renew", "please renew", "do it", "go ahead"
#         ])

#         # 🔴 NEGATIVE INTENT
#         negative_intent = any(word in text for word in [
#             "no", "nope", "not now", "later", "maybe later",
#             "don't", "do not", "not interested"
#         ])

#         if not phone or not text:
#             return Response({"status": "no data"})



#         import time
#         time.sleep(5)

#         # ----------------------------
#         # STATE: INITIAL
#         # ----------------------------
#         if state == "initial":

#             if positive_intent:

#                 reply = """Great! 😊

# I’ll help you renew your policy.

# Here’s your secure payment link:
# 🔗 https://your-payment-link.com

# """

#                 customer.conversation_state = "done"

#             elif negative_intent:

#                 reply = """No worries 😊

# Would you like me to remind you again later?"""

#                 customer.conversation_state = "ask_reminder"

#             else:
#                 reply = """I’m here to help 😊

# Would you like to renew your policy now?"""

#         # ----------------------------
#         # STATE: ASK REMINDER
#         # ----------------------------
#         elif state == "ask_reminder":

#             if positive_intent:

#                 reply = """Got it 👍

# I’ll remind you again before your policy expires.

# You don’t have to worry 😊"""

#                 customer.conversation_state = "done"

#             elif negative_intent:

#                 reply = """Alright 😊

# If you need anything later, feel free to reach out.

# Take care! 👋"""

#                 customer.conversation_state = "done"

#             else:
#                 reply = """Just to confirm 😊

# Should I remind you again later?"""

#         # ----------------------------
#         # STATE: DONE
#         # ----------------------------
#         else:
#             reply = """I’m here if you need any help 😊"""

#         customer.save()

#         send_whatsapp_message(phone, reply)

#         ChatMessage.objects.create(
#             customer=customer,
#             message=reply,
#             sender="bot"
#         )

#     except Exception as e:
#         print("ERROR:", str(e))

#     return Response({"status": "received"})


# from bot.models import Customer, ChatMessage

# @api_view(["GET"])
# def get_conversations(request):

#     customers = Customer.objects.all()

#     data = []

#     for c in customers:
#         last_msg = ChatMessage.objects.filter(customer=c).order_by('-timestamp').first()

#         data.append({
#             "id": c.id,
#             "name": c.name,
#             "phone": c.phone,
#             "last_message": last_msg.message if last_msg else ""
#         })

#     return Response({"conversations": data})

# @api_view(["GET"])
# def get_messages(request, customer_id):

#     messages = ChatMessage.objects.filter(customer_id=customer_id).order_by('timestamp')

#     data = []

#     for m in messages:
#         data.append({
#             "message": m.message,
#             "sender": m.sender,
#             "time": m.timestamp
#         })

#     return Response({"messages": data})

# @api_view(["POST"])
# def send_message_dashboard(request):

#     from bot.services.whatsapp_service import send_whatsapp_message

#     customer_id = request.data.get("customer_id")
#     message = request.data.get("message")

#     customer = Customer.objects.get(id=customer_id)

#     # send message
#     send_whatsapp_message(customer.phone, message)

#     # save message
#     ChatMessage.objects.create(
#         customer=customer,
#         message=message,
#         sender="bot"
#     )

#     return Response({"status": "sent"})


# from bot.models import Customer, ChatMessage
# from django.db.models import Min, Max, Count

# @api_view(["GET"])
# def dashboard_data(request):

#     total_customers = Customer.objects.count()
#     total_messages = ChatMessage.objects.count()
#     total_conversations = Customer.objects.count()  # one per customer

#     customers = Customer.objects.all()

#     table_data = []

#     for c in customers:

#         msgs = ChatMessage.objects.filter(customer=c)

#         first_msg = msgs.order_by('timestamp').first()
#         last_msg = msgs.order_by('-timestamp').first()

#         table_data.append({
#             "id": c.id,
#             "phone": c.phone,
#             "name": c.name,
#             "first_contact": first_msg.timestamp if first_msg else None,
#             "last_contact": last_msg.timestamp if last_msg else None,
#         })

#     return Response({
#         "total_customers": total_customers,
#         "total_messages": total_messages,
#         "total_conversations": total_conversations,
#         "customers": table_data
#     })

# import os
# from rest_framework.parsers import MultiPartParser, FormParser
# from django.utils import timezone

# from bot.models import UploadedFile, Customer, UploadBatch
# from bot.services.whatsapp_service import send_whatsapp_message
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny

# # ===== UPLOAD PROGRESS TRACKING =====
# upload_progress = {"sent": 0, "total": 0, "active": False}


# @api_view(["POST"])
# @authentication_classes([])   # disable session auth
# @permission_classes([AllowAny])
# def upload_file(request):
#     file = request.FILES.get("file")

#     if not file:
#         return Response({"error": "No file uploaded"}, status=400)

#     # ✅ Save file
#     obj = UploadedFile.objects.create(file=file)

#     file_path = obj.file.path
#     ext = os.path.splitext(file_path)[1].lower()

#     customers = []

#     # ---------------- EXCEL ----------------
#     if ext in [".xlsx", ".xls"]:
#         import pandas as pd

#         df = pd.read_excel(file_path)

#         print("COLUMNS:",df.columns)

#         for _, row in df.iterrows():

#             expiry = row.get("policy_expiry")   # ✅ CORRECT COLUMN

#             print("RAW EXPIRY:",expiry,type(expiry))

#             # ✅ HANDLE DATETIME CORRECTLY
#             # ✅ BEST PRACTICE conversion
#             if pd.notnull(expiry):
#                 try:
#                     expiry = pd.to_datetime(expiry, errors="coerce")

#                     if pd.notnull(expiry):
#                         expiry = expiry.date()
#                     else:
#                         expiry = None

#                 except Exception as e:
#                     print("DATE ERROR:", e)
#                     expiry = None
#             else:
#                 expiry = None

#             name = row.get("name") or "Customer"
#             phone = str(row.get("phone") or "").strip()

#             if not phone:
#                 continue

#             customers.append({
#                 "name": name,
#                 "phone": phone,
#                 "policy_type": "Insurance",
#                 "expiry_date": expiry
#             })

#     # ---------------- PDF ----------------
#     elif ext == ".pdf":
#         from PyPDF2 import PdfReader

#         reader = PdfReader(file_path)
#         text = ""

#         for page in reader.pages:
#             text += page.extract_text()

#         # ⚠️ Simple parsing (you can improve later)
#         lines = text.split("\n")

#         for line in lines:
#             parts = line.split(",")

#             if len(parts) >= 2:
#                 customers.append({
#                     "name": parts[0],
#                     "phone": parts[1],
#                     "policy_type": "Insurance",
#                     "expiry_date": expiry
#                 })

#     # ---------------- WORD ----------------
#     elif ext == ".docx":
#         import docx

#         doc = docx.Document(file_path)

#         for para in doc.paragraphs:
#             parts = para.text.split(",")

#             if len(parts) >= 3:
#                 expiry = parts[2].strip()
#             else:
#                 expiry = None

#             # convert to date
#             import pandas as pd
#             expiry = pd.to_datetime(expiry, errors="coerce")

#             if pd.notnull(expiry):
#                 expiry = expiry.date()
#             else:
#                 expiry = None

#             customers.append({
#                 "name": parts[0],
#                 "phone": parts[1],
#                 "policy_type": "Insurance",
#                 "expiry_date": expiry
#             })

#     else:
#         return Response({"error": "Unsupported file type"}, status=400)

#     # ---------------- CREATE BATCH ----------------
#     batch = UploadBatch.objects.create(
#         name=file.name,
#         customer_count=len(customers)
#     )

#     # ---------------- SAVE ONLY ----------------
#     for c in customers:

#         customer, created = Customer.objects.get_or_create(
#             phone=c["phone"],
#             defaults={
#                 "name": c["name"],
#                 "policy_type": c["policy_type"],
#                 "expiry_date": c["expiry_date"]
#             }
#         )

#         if not created:
#             customer.expiry_date = c["expiry_date"]
#             customer.name = c["name"]
#             customer.policy_type = c["policy_type"]

#         customer.conversation_state = "initial"
#         customer.reminder_sent = False
#         customer.batch = batch
#         customer.save()


#     # 🔥 NOW CALL RENEWAL (with progress tracking)
#     from bot.services.expiry_service import get_expiring_customers
#     from bot.services.whatsapp_service import send_whatsapp_message as send_msg
#     from bot.models import ChatMessage as CM
#     import time as t

#     sending_customers = get_expiring_customers()
#     upload_progress["total"] = len(sending_customers)
#     upload_progress["sent"] = 0
#     upload_progress["active"] = True

#     print("CALLING RENEWAL...")

#     for c in sending_customers:
#         message = f"""
# Hello {c.name} 👋

# Your {c.policy_type} policy will expire on {c.expiry_date}.

# Do you want to renew your policy?
# """
#         print("Sending to:", c.phone)
#         send_msg(c.phone, message)

#         CM.objects.create(customer=c, message=message, sender="bot")
#         c.reminder_sent = True
#         c.save()

#         upload_progress["sent"] += 1
#         t.sleep(2)

#     upload_progress["active"] = False

#     return Response({"status": "file processed & messages sent"})


# def dashboard_view(request):
#     return render(request, "dashboard.html")

# def upload_page_view(request):
#     return render(request, "upload.html")

# @api_view(["GET"])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def get_upload_progress(request):
#     return Response(upload_progress)


# from bot.models import UploadBatch

# @api_view(["GET"])
# def get_batches(request):
#     batches = UploadBatch.objects.all().order_by('-uploaded_at')

#     data = []
#     for b in batches:
#         data.append({
#             "id": b.id,
#             "name": b.name,
#             "uploaded_at": b.uploaded_at,
#             "customer_count": b.customer_count
#         })

#     return Response({"batches": data})


# @api_view(["GET"])
# def get_batch_customers(request, batch_id):
#     customers = Customer.objects.filter(batch_id=batch_id)

#     data = []
#     for c in customers:
#         last_msg = ChatMessage.objects.filter(customer=c).order_by('-timestamp').first()

#         data.append({
#             "id": c.id,
#             "name": c.name,
#             "phone": c.phone,
#             "last_message": last_msg.message if last_msg else ""
#         })

#     return Response({"customers": data})
































# ============================================================
#  bot/views.py
# ============================================================
 
from datetime import date
import os
import re
import time
 
import pandas as pd
from django.core.cache import cache
from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
 
from bot.models import Customer, ChatMessage, UploadedFile, UploadBatch
from bot.services.whatsapp_service import send_whatsapp_message
from bot.services.renewal_service import run_renewal, run_new_insurance, run_all
from bot.services.expiry_service import get_expiring_customers, get_new_insurance_customers
 
 
# ============================================================
#  CONSTANTS & CONFIG
# ============================================================
 
UPLOAD_PROGRESS_KEY = "upload_progress"
 
CLOSING_KEYWORDS = {
    "ok", "okay", "okk", "okkk",
    "thank you", "thanks", "thankyou",
    "bye", "bye bye", "goodbye", "thx", "ty",
}
 
POSITIVE_KEYWORDS = {
    "yes", "yeah", "yup", "sure", "haan", "ha",
    "renew", "please renew", "do it", "go ahead", "proceed",
}
 
NEGATIVE_KEYWORDS = {
    "no", "nope", "not now", "later", "maybe later",
    "don't", "do not", "not interested", "nahi", "na",
}
 
# ✅ NEW: greeting keywords to activate inbound bot
GREETING_KEYWORDS = {
    "hi", "hello", "hey", "hii", "helo", "hlw",
    "hye", "start", "help", "namaskar", "namaste",
}
 
# ── Coverage options per vehicle type ──────────────────────
COVERAGE_OPTIONS = {
    "Car": [
        ("Third Party",       2094),
        ("Comprehensive",     8500),
        ("Zero Depreciation", 12000),
    ],
    "Bike": [
        ("Third Party",       714),
        ("Comprehensive",     2500),
        ("Long Term 2yr TP",  1200),
        ("Long Term 3yr TP",  1600),
    ],
    "Commercial": [
        ("Third Party",          4000),
        ("Comprehensive",        15000),
        ("Goods Carrying",       18000),
        ("Passenger Carrying",   20000),
    ],
    "Auto": [
        ("Third Party",    1500),
        ("Comprehensive",  4500),
    ],
    "Tractor": [
        ("Third Party Only",             1500),
        ("Comprehensive + Farm Equip",   7000),
        ("Fire & Theft Only",            3000),
    ],
}
 
# ── Add-on options per vehicle type (name, extra premium) ──
ADDON_OPTIONS = {
    "Car": [
        ("Zero Depreciation",  1500),
        ("Roadside Assistance", 500),
        ("Engine Protection",   800),
        ("Return to Invoice",   700),
        ("Key Replacement",     300),
        ("Consumables Cover",   400),
    ],
    "Bike": [
        ("Zero Depreciation",   500),
        ("Roadside Assistance", 200),
        ("Personal Accident",   300),
    ],
    "Commercial": [
        ("Goods in Transit",  1500),
        ("Driver PA Cover",    500),
        ("Cleaner/Helper Cover", 300),
    ],
    "Auto": [
        ("Passenger Cover (up to 3)", 400),
        ("Driver PA Cover",           300),
    ],
    "Tractor": [
        ("Driver PA Cover",          300),
        ("Trolley/Attachment Cover", 600),
    ],
}
 
PAYMENT_LINK = "https://your-payment-link.com"
 
 
# ============================================================
#  HELPERS
# ============================================================
 
def _set_progress(sent: int, total: int, active: bool) -> None:
    cache.set(UPLOAD_PROGRESS_KEY, {"sent": sent, "total": total, "active": active}, timeout=3600)
 
 
def _save_msg(customer: Customer, message: str, sender: str) -> None:
    ChatMessage.objects.create(customer=customer, message=message, sender=sender)
 
 
def _send_and_save(customer: Customer, reply: str) -> None:
    send_whatsapp_message(customer.phone, reply)
    _save_msg(customer, reply, "bot")
 
 
def _has_any(text: str, keyword_set: set) -> bool:
    return any(word in text for word in keyword_set)
 
 
def _parse_expiry(raw) -> "date | None":
    if pd.isnull(raw):
        return None
    try:
        parsed = pd.to_datetime(raw, errors="coerce")
        return parsed.date() if pd.notnull(parsed) else None
    except Exception:
        return None
 
 
def _validate_vehicle_number(text: str) -> bool:
    pattern = r'^[A-Z]{2}[\s\-]?\d{2}[\s\-]?[A-Z]{1,2}[\s\-]?\d{4}$'
    return bool(re.match(pattern, text.upper().strip()))
 
 
def _build_coverage_menu(vehicle_type: str) -> str:
    options = COVERAGE_OPTIONS.get(vehicle_type, [])
    lines = [f"{i+1}️⃣ {name}  (₹{price:,}/yr)" for i, (name, price) in enumerate(options)]
    return "\n".join(lines)
 
 
def _build_addon_menu(vehicle_type: str) -> str:
    options = ADDON_OPTIONS.get(vehicle_type, [])
    lines = [f"{i+1}️⃣ {name}  (+₹{price:,})" for i, (name, price) in enumerate(options)]
    lines.append(f"{len(options)+1}️⃣ No add-ons")
    return "\n".join(lines)
 
 
def _calculate_premium(vehicle_type: str, coverage_index: int, addon_indices: list) -> tuple:
    coverages = COVERAGE_OPTIONS.get(vehicle_type, [])
    addons    = ADDON_OPTIONS.get(vehicle_type, [])
 
    coverage_name, base_premium = coverages[coverage_index]
 
    selected_addon_names = []
    total_addon_premium  = 0
 
    for idx in addon_indices:
        if 0 <= idx < len(addons):
            name, price = addons[idx]
            selected_addon_names.append(name)
            total_addon_premium += price
 
    total     = base_premium + total_addon_premium
    addon_str = ", ".join(selected_addon_names) if selected_addon_names else "None"
 
    return coverage_name, addon_str, total
 
 
# ============================================================
#  WHATSAPP WEBHOOK — STATE MACHINE
# ============================================================
 
@api_view(["POST"])
def whatsapp_webhook(request):
    data = request.data
 
    try:
        if data.get("event") != "messages.received":
            return Response({"status": "ignored"})
 
        message_data = data.get("data", {}).get("messages", {})
        phone        = message_data.get("key", {}).get("cleanedSenderPn")
        raw_text     = message_data.get("messageBody", "")
 
        if not phone or not raw_text:
            return Response({"status": "no data"})
 
        text = raw_text.lower().strip()
        print(f"[webhook] phone={phone}  text={text!r}")
 
        # ── Smart routing: decide which customer record gets this msg ──
        inbound_cust  = Customer.objects.filter(phone=phone, source="inbound").first()
        outbound_cust = Customer.objects.filter(phone=phone, source="outbound").first()
 
        # Active = conversation is in progress (not idle)
        ACTIVE_STATES = {
            "initial", "ask_service_type", "ask_vehicle_category",
            "ask_vehicle_other", "ask_vehicle_details", "ask_vehicle_model",
            "ask_coverage", "ask_addons", "show_quote", "payment_sent",
            "ask_reminder",
        }
 
        outbound_active = outbound_cust and outbound_cust.conversation_state in ACTIVE_STATES
        inbound_active  = inbound_cust  and inbound_cust.conversation_state  in ACTIVE_STATES
 
        if outbound_active:
            # Outbound customer is mid-conversation → route reply there
            customer = outbound_cust
        elif inbound_active:
            # Inbound customer is mid-conversation → route there
            customer = inbound_cust
        elif inbound_cust:
            # Both idle → prefer inbound for new conversations
            customer = inbound_cust
        elif outbound_cust:
            # Only outbound exists
            customer = outbound_cust
        else:
            # No customer at all → create inbound if greeting
            if _has_any(text, GREETING_KEYWORDS):
                customer = Customer.objects.create(
                    phone=phone,
                    name="User",
                    source="inbound",
                    conversation_state="inactive",
                )
                print(f"[webhook] New inbound customer created: {phone}")
            else:
                return Response({"status": "user not found"})
 
        _save_msg(customer, text, "user")
 
        # ── Closing short-circuit ──────────────────────────────
        if _has_any(text, CLOSING_KEYWORDS):
            _send_and_save(customer, "You're welcome 😊Say *Hi* anytime to start a new conversation 👋")
            customer.conversation_state = "inactive"   # session reset
            customer.save()
            return Response({"status": "closed"})
 
        state    = customer.conversation_state
        positive = _has_any(text, POSITIVE_KEYWORDS)
        negative = _has_any(text, NEGATIVE_KEYWORDS)
        vtype    = customer.vehicle_type
 
        # ══════════════════════════════════════════════════════
        # ✅ NEW INBOUND STATES (added above existing flow)
        # ══════════════════════════════════════════════════════
 
        # ==================================================
        # STATE: inactive
        # User sends hi/hello → activate bot
        # ==================================================
        if state == "inactive":
            if _has_any(text, GREETING_KEYWORDS):
                reply = (
                    "Hello! 👋 Welcome to *Vehicle Insurance* 🚗🏍️\n\n"
                    "I'm here to help you with insurance.\n\n"
                    "What are you looking for?\n"
                    "1️⃣ New Insurance\n"
                    "2️⃣ Renewal"
                )
                customer.conversation_state = "ask_service_type"
            else:
                reply = (
                    "Hello! 👋 Please say *Hi* to get started 😊"
                )
 
        # ==================================================
        # STATE: ask_service_type
        # User picks New Insurance (1) or Renewal (2)
        # ==================================================
        elif state == "ask_service_type":
            if text == "1":
                customer.customer_type = "new"
                reply = (
                    "Great! 😊 Let's get you insured.\n\n"
                    "What type of vehicle do you have?\n"
                    "1️⃣ Two Wheeler  (Bike / Scooter)\n"
                    "2️⃣ Four Wheeler (Car / SUV / MUV)\n"
                    "3️⃣ Other        (Commercial / Auto / Tractor)"
                )
                customer.conversation_state = "ask_vehicle_category"
 
            elif text == "2":
                customer.customer_type = "renewal"
                reply = (
                    "Sure! Let's renew your policy 😊\n\n"
                    "What type of vehicle do you have?\n"
                    "1️⃣ Two Wheeler  (Bike / Scooter)\n"
                    "2️⃣ Four Wheeler (Car / SUV / MUV)\n"
                    "3️⃣ Other        (Commercial / Auto / Tractor)"
                )
                customer.conversation_state = "ask_vehicle_category"
 
            else:
                reply = (
                    "Please reply with *1* or *2* 😊\n\n"
                    "1️⃣ New Insurance\n"
                    "2️⃣ Renewal"
                )
 
        # ==================================================
        # STATE: ask_vehicle_category
        # 1 = Two Wheeler → Bike
        # 2 = Four Wheeler → Car
        # 3 = Other → ask sub-type
        # ==================================================
        elif state == "ask_vehicle_category":
            if text == "1":
                customer.vehicle_type = "Bike"
                reply = (
                    "Got it! 🏍️\n\n"
                    "Please share your *vehicle registration number*:\n\n"
                    "Example: *GJ05AB1234*"
                )
                customer.conversation_state = "ask_vehicle_details"
 
            elif text == "2":
                customer.vehicle_type = "Car"
                reply = (
                    "Got it! 🚗\n\n"
                    "Please share your *vehicle registration number*:\n\n"
                    "Example: *GJ01AB1234*"
                )
                customer.conversation_state = "ask_vehicle_details"
 
            elif text == "3":
                reply = (
                    "Please select your vehicle type:\n\n"
                    "1️⃣ Commercial Vehicle (Truck / Bus / Tempo)\n"
                    "2️⃣ Auto Rickshaw / E-Rickshaw\n"
                    "3️⃣ Tractor / Farm Equipment"
                )
                customer.conversation_state = "ask_vehicle_other"
 
            else:
                reply = (
                    "Please reply with *1*, *2* or *3* 😊\n\n"
                    "1️⃣ Two Wheeler\n"
                    "2️⃣ Four Wheeler\n"
                    "3️⃣ Other"
                )
 
        # ==================================================
        # STATE: ask_vehicle_other
        # Sub-menu for Commercial / Auto / Tractor
        # ==================================================
        elif state == "ask_vehicle_other":
            if text == "1":
                customer.vehicle_type = "Commercial"
                emoji = "🚛"
            elif text == "2":
                customer.vehicle_type = "Auto"
                emoji = "🛺"
            elif text == "3":
                customer.vehicle_type = "Tractor"
                emoji = "🚜"
            else:
                reply = (
                    "Please reply with *1*, *2* or *3* 😊\n\n"
                    "1️⃣ Commercial Vehicle\n"
                    "2️⃣ Auto Rickshaw / E-Rickshaw\n"
                    "3️⃣ Tractor / Farm Equipment"
                )
                customer.save()
                _send_and_save(customer, reply)
                return Response({"status": "received"})
 
            reply = (
                f"Got it! {emoji}\n\n"
                "Please share your *vehicle registration number*:\n\n"
                "Example: *GJ03AB1234*"
            )
            customer.conversation_state = "ask_vehicle_details"
 
        # ==================================================
        # STATE: ask_vehicle_details
        # Step 1 — Ask vehicle number only
        # ==================================================
        elif state == "ask_vehicle_details":
            vehicle_number = raw_text.strip().upper()
 
            if _validate_vehicle_number(vehicle_number):
                customer.vehicle_number = vehicle_number
                customer.policy_type    = customer.vehicle_type  # backward compat
 
                reply = (
                    f"Got it! ✅ *{vehicle_number}*\n\n"
                    f"Now please share your *vehicle model*:\n\n"
                    f"Example: *Honda Activa* / *Maruti Swift* / *Tata Ace*"
                )
                customer.conversation_state = "ask_vehicle_model"
 
            else:
                reply = (
                    "Please enter a valid vehicle registration number 😊\n\n"
                    "Example: *GJ01AB1234*"
                )
 
        # ==================================================
        # STATE: ask_vehicle_model
        # Step 2 — Ask vehicle model
        # ==================================================
        elif state == "ask_vehicle_model":
            vehicle_model = raw_text.strip()
 
            if len(vehicle_model) >= 2:
                customer.vehicle_model = vehicle_model
 
                vtype = customer.vehicle_type
                menu  = _build_coverage_menu(vtype)
 
                reply = (
                    f"Perfect! 🚗\n\n"
                    f"*Vehicle No* : {customer.vehicle_number}\n"
                    f"*Model*      : {vehicle_model}\n"
                    f"*Type*       : {vtype}\n\n"
                    f"Now choose your coverage:\n\n"
                    f"{menu}"
                )
                customer.conversation_state = "ask_coverage"
 
            else:
                reply = (
                    "Please enter your vehicle model 😊\n\n"
                    "Example: *Honda Activa* / *Maruti Swift*"
                )
 
        # ══════════════════════════════════════════════════════
        # EXISTING OUTBOUND FLOW — UNCHANGED BELOW THIS LINE
        # ══════════════════════════════════════════════════════
 
        # ==================================================
        # STATE: initial
        # Outbound user replies to bot's first message
        # ==================================================
        elif state == "initial":
            if positive:
                menu  = _build_coverage_menu(vtype)
                reply = (
                    f"Great! Let's get started 😊\n\n"
                    f"Choose your coverage for *{customer.vehicle_number or vtype}*:\n\n"
                    f"{menu}"
                )
                customer.conversation_state = "ask_coverage"
 
            elif negative:
                if customer.customer_type == "renewal":
                    reply = (
                        f"No worries 😊\n\n"
                        f"Your policy expires on *{customer.expiry_date}*.\n"
                        f"Should I remind you 3 days before expiry? (Yes / No)"
                    )
                else:
                    reply = (
                        "No worries 😊\n\n"
                        "But remember — driving uninsured is illegal ⚠️\n\n"
                        "Should I follow up with you tomorrow? (Yes / No)"
                    )
                customer.conversation_state = "ask_reminder"
 
            else:
                if customer.customer_type == "renewal":
                    reply = (
                        f"I'm here to help 😊\n\n"
                        f"Your *{vtype}* policy expires on *{customer.expiry_date}*.\n"
                        f"Would you like to renew it? (Yes / No)"
                    )
                else:
                    reply = (
                        f"I'm here to help 😊\n\n"
                        f"Would you like to get insurance for your "
                        f"*{vtype}* ({customer.vehicle_number})? (Yes / No)"
                    )
 
        # ==================================================
        # STATE: ask_coverage
        # ==================================================
        elif state == "ask_coverage":
            coverages = COVERAGE_OPTIONS.get(vtype, [])
 
            if text.isdigit() and 1 <= int(text) <= len(coverages):
                idx = int(text) - 1
                customer.selected_coverage = str(idx)
 
                menu  = _build_addon_menu(vtype)
                reply = (
                    f"Good choice! 👍\n\n"
                    f"Now select add-ons for your *{vtype}*:\n"
                    f"(Send numbers separated by space, e.g. *1 3*)\n\n"
                    f"{menu}"
                )
                customer.conversation_state = "ask_addons"
 
            else:
                menu  = _build_coverage_menu(vtype)
                reply = (
                    f"Please reply with a number 1–{len(coverages)} 😊\n\n"
                    f"{menu}"
                )
 
        # ==================================================
        # STATE: ask_addons
        # ==================================================
        elif state == "ask_addons":
            addons     = ADDON_OPTIONS.get(vtype, [])
            no_addon_n = len(addons) + 1
            parts      = text.split()
            valid      = True
            addon_indices = []
 
            for p in parts:
                if p.isdigit():
                    n = int(p)
                    if n == no_addon_n:
                        addon_indices = []
                        break
                    elif 1 <= n <= len(addons):
                        addon_indices.append(n - 1)
                    else:
                        valid = False
                        break
                else:
                    valid = False
                    break
 
            if not valid:
                menu  = _build_addon_menu(vtype)
                reply = (
                    f"Please send valid numbers 😊\n\n"
                    f"{menu}"
                )
            else:
                cov_idx = int(customer.selected_coverage or "0")
                coverage_name, addon_str, total = _calculate_premium(vtype, cov_idx, addon_indices)
 
                customer.selected_addons = addon_str
                customer.quoted_premium  = total
 
                action = "renew" if customer.customer_type == "renewal" else "get insured"
 
                reply = (
                    f"Here's your quote 📋\n"
                    f"──────────────────────────\n"
                    f"Name       : {customer.name}\n"
                    f"Vehicle    : {customer.vehicle_number or 'N/A'}\n"
                    f"Model      : {customer.vehicle_model or 'N/A'}\n"
                    f"Type       : {vtype}\n"
                    f"Coverage   : {coverage_name}\n"
                    f"Add-ons    : {addon_str}\n"
                    f"Premium    : ₹{total:,}/year\n"
                    f"──────────────────────────\n\n"
                    f"Shall I proceed to {action}? (Yes / No)"
                )
                customer.conversation_state = "show_quote"
 
        # ==================================================
        # STATE: show_quote
        # ==================================================
        elif state == "show_quote":
            if positive:
                reply = (
                    f"Perfect! 🎉\n\n"
                    f"Click below to pay securely:\n"
                    f"🔗 {PAYMENT_LINK}\n\n"
                    f"Your policy will be issued within minutes "
                    f"after payment ✅\n\n"
                    f"Please reply *Done* once payment is complete."
                )
                customer.conversation_state = "payment_sent"
 
            elif negative:
                menu  = _build_coverage_menu(vtype)
                reply = (
                    f"No problem 😊 Let's pick again.\n\n"
                    f"Choose your coverage for *{customer.vehicle_number or vtype}*:\n\n"
                    f"{menu}"
                )
                customer.conversation_state = "ask_coverage"
 
            else:
                reply = "Please reply *Yes* to proceed or *No* to change your plan 😊"
 
        # ==================================================
        # STATE: payment_sent
        # ==================================================
        elif state == "payment_sent":
            payment_done = any(w in text for w in [
                "done", "paid", "payment done", "completed",
                "complete", "yes", "sent"
            ])
 
            if payment_done:
                if customer.customer_type == "renewal":
                    action_msg = f"Your *{vtype}* insurance has been *renewed* ✅"
                else:
                    action_msg = f"Your *{vtype}* is now *insured* ✅"
 
                reply = (
                    f"🎉 Congratulations *{customer.name}*!\n\n"
                    f"{action_msg}\n\n"
                    f"Policy document will be sent to your "
                    f"registered email/WhatsApp shortly 📧\n\n"
                    f"Thank you for choosing us! 😊\n\n"
                    f"Say *Hi* anytime if you need help again 👋"
                )
                customer.conversation_state = "inactive"   # session reset
 
            else:
                reply = (
                    f"Please complete the payment here:\n"
                    f"🔗 {PAYMENT_LINK}\n\n"
                    f"Reply *Done* once payment is complete 😊"
                )
 
        # ==================================================
        # STATE: ask_reminder
        # ==================================================
        elif state == "ask_reminder":
            if positive:
                if customer.customer_type == "renewal":
                    reply = (
                        f"Done! ✅ I'll remind you 3 days before "
                        f"your policy expires on *{customer.expiry_date}* 😊"
                    )
                else:
                    reply = (
                        "Done! ✅ I'll follow up with you tomorrow 😊\n\n"
                        "Remember — getting insured takes just 2 minutes! ⚡"
                    )
                customer.conversation_state = "inactive"   # session reset
 
            elif negative:
                reply = (
                    "Alright 😊\n\n"
                    "Feel free to reach out whenever you're ready.\n\n"
                    "Say *Hi* anytime to start again! 👋"
                )
                customer.conversation_state = "inactive"   # session reset
 
            else:
                reply = "Please reply *Yes* or *No* 😊"
 
        # ==================================================
        # STATE: policy_issued / done / closed — fallback
        # ==================================================
        else:
            reply = (
                "I'm here if you need any help 😊\n\n"
                "You can always reach out for insurance queries!"
            )
 
        customer.save()
        _send_and_save(customer, reply)
 
    except Exception as e:
        print(f"[webhook] ERROR: {e}")
        import traceback; traceback.print_exc()
 
    return Response({"status": "received"})
 
 
# ============================================================
#  TEST / TRIGGER ENDPOINTS
# ============================================================
 
@api_view(["GET"])
def test_send_message(request):
    phone   = "919104142402"
    message = "Hello 👋 This is a test message from Django bot"
    result  = send_whatsapp_message(phone, message)
    return Response({"status": "message sent", "response": result})
 
 
@api_view(["GET"])
def run_renewal_api(request):
    run_renewal()
    return Response({"status": "renewal messages sent"})
 
 
@api_view(["GET"])
def run_new_insurance_api(request):
    run_new_insurance()
    return Response({"status": "new insurance messages sent"})
 
 
@api_view(["GET"])
def run_all_campaigns_api(request):
    run_all()
    return Response({"status": "all campaigns triggered"})
 
 
# ============================================================
#  FILE UPLOAD
# ============================================================
 
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def upload_file(request):
    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file uploaded"}, status=400)
 
    obj       = UploadedFile.objects.create(file=file)
    file_path = obj.file.path
    ext       = os.path.splitext(file_path)[1].lower()
 
    customers_data = []
 
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
        print("[upload] Columns:", df.columns.tolist())
 
        for _, row in df.iterrows():
            phone = str(row.get("phone") or "").strip()
            if not phone:
                continue
 
            raw_ctype     = str(row.get("customer_type") or "renewal").strip().lower()
            customer_type = "new" if raw_ctype == "new" else "renewal"
 
            raw_vtype    = str(row.get("vehicle_type") or "Car").strip().title()
            valid_types  = {"Car", "Bike", "Commercial", "Auto", "Tractor"}
            vehicle_type = raw_vtype if raw_vtype in valid_types else "Car"
 
            customers_data.append({
                "name":           str(row.get("name") or "Customer").strip(),
                "phone":          phone,
                "customer_type":  customer_type,
                "vehicle_type":   vehicle_type,
                "vehicle_number": str(row.get("vehicle_number") or "").strip() or None,
                "vehicle_model":  str(row.get("vehicle_model") or "").strip() or None,
                "policy_type":    vehicle_type,
                "expiry_date":    _parse_expiry(row.get("policy_expiry")),
            })
 
    else:
        return Response({"error": f"Unsupported file type: {ext}. Please upload .xlsx"}, status=400)
 
    batch = UploadBatch.objects.create(name=file.name, customer_count=len(customers_data))
 
    for c in customers_data:
        customer, created = Customer.objects.get_or_create(
            phone=c["phone"],
            source="outbound",          # ← separate from inbound
            defaults={
                "name":           c["name"],
                "customer_type":  c["customer_type"],
                "vehicle_type":   c["vehicle_type"],
                "vehicle_number": c["vehicle_number"],
                "vehicle_model":  c["vehicle_model"],
                "policy_type":    c["policy_type"],
                "expiry_date":    c["expiry_date"],
            },
        )
        if not created:
            customer.name           = c["name"]
            customer.customer_type  = c["customer_type"]
            customer.vehicle_type   = c["vehicle_type"]
            customer.vehicle_number = c["vehicle_number"]
            customer.vehicle_model  = c["vehicle_model"]
            customer.policy_type    = c["policy_type"]
            customer.expiry_date    = c["expiry_date"]
 
        customer.conversation_state = "initial"   # outbound customers → initial
        customer.reminder_sent      = False
        customer.batch              = batch
        customer.save()
 
    from bot.services.renewal_service import (
        RENEWAL_TEMPLATE, NEW_INSURANCE_TEMPLATE, _send_and_log
    )
 
    renewal_customers = list(Customer.objects.filter(batch=batch, customer_type="renewal"))
    new_customers     = list(Customer.objects.filter(batch=batch, customer_type="new"))
 
    total      = len(renewal_customers) + len(new_customers)
    sent_count = 0
    _set_progress(sent=0, total=total, active=True)
 
    for c in renewal_customers:
        msg = RENEWAL_TEMPLATE.format(
            name=c.name,
            vehicle_type=c.vehicle_type,
            vehicle_number=c.vehicle_number or "N/A",
            expiry_date=c.expiry_date,
        )
        print(f"[upload] Renewal → {c.phone}")
        _send_and_log(c, msg)
        sent_count += 1
        _set_progress(sent=sent_count, total=total, active=True)
        time.sleep(2)
 
    for c in new_customers:
        msg = NEW_INSURANCE_TEMPLATE.format(
            name=c.name,
            vehicle_type=c.vehicle_type,
            vehicle_number=c.vehicle_number or "N/A",
        )
        print(f"[upload] New insurance → {c.phone}")
        _send_and_log(c, msg)
        sent_count += 1
        _set_progress(sent=sent_count, total=total, active=True)
        time.sleep(2)
 
    _set_progress(sent=total, total=total, active=False)
 
    return Response({
        "status":             "file processed & messages sent",
        "customers_found":    len(customers_data),
        "renewal_sent":       len(renewal_customers),
        "new_insurance_sent": len(new_customers),
    })
 
 
# ============================================================
#  UPLOAD PROGRESS
# ============================================================
 
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_upload_progress(request):
    progress = cache.get(UPLOAD_PROGRESS_KEY, {"sent": 0, "total": 0, "active": False})
    return Response(progress)
 
 
# ============================================================
#  CONVERSATION ENDPOINTS
# ============================================================
 
@api_view(["GET"])
def get_conversations(request):
    # Only return inbound (walk-in) customers
    customers = Customer.objects.filter(source="inbound").prefetch_related("chatmessage_set")
    data = []
    for c in customers:
        msgs = c.chatmessage_set.order_by("-timestamp")
        data.append({
            "id":                 c.id,
            "name":               c.name,
            "phone":              c.phone,
            "customer_type":      c.customer_type,
            "vehicle_type":       c.vehicle_type,
            "vehicle_number":     c.vehicle_number,
            "vehicle_model":      c.vehicle_model,
            "conversation_state": c.conversation_state,
            "source":             c.source,
            "batch_id":           c.batch_id,
            "last_message":       msgs.first().message if msgs.exists() else "",
        })
    return Response({"conversations": data})
 
 
@api_view(["GET"])
def get_messages(request, customer_id):
    messages = (
        ChatMessage.objects
        .filter(customer_id=customer_id)
        .order_by("timestamp")
        .values("message", "sender", "timestamp")
    )
    return Response({"messages": list(messages)})
 
 
@api_view(["POST"])
def send_message_dashboard(request):
    customer_id = request.data.get("customer_id")
    message     = request.data.get("message", "").strip()
 
    if not customer_id or not message:
        return Response({"error": "customer_id and message are required"}, status=400)
 
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
 
    send_whatsapp_message(customer.phone, message)
    _save_msg(customer, message, "bot")
    return Response({"status": "sent"})
 
 
# ============================================================
#  DASHBOARD
# ============================================================
 
@api_view(["GET"])
def dashboard_data(request):
    customers = Customer.objects.prefetch_related("chatmessage_set").all()
 
    outbound_count = customers.filter(source="outbound").count()
    inbound_count  = customers.filter(source="inbound").count()
 
    return Response({
        "total_customers":     customers.count(),
        "total_outbound":      outbound_count,
        "total_inbound":       inbound_count,
        "total_messages":      ChatMessage.objects.count(),
        "total_conversations": customers.count(),
    })
 
 
# ============================================================
#  BATCH ENDPOINTS
# ============================================================
 
@api_view(["GET"])
def get_batches(request):
    batches = UploadBatch.objects.order_by("-uploaded_at").values(
        "id", "name", "uploaded_at", "customer_count"
    )
    return Response({"batches": list(batches)})
 
 
@api_view(["GET"])
def get_batch_customers(request, batch_id):
    customers = Customer.objects.filter(batch_id=batch_id).prefetch_related("chatmessage_set")
    data = []
    for c in customers:
        msgs = c.chatmessage_set.order_by("-timestamp")
        data.append({
            "id":             c.id,
            "name":           c.name,
            "phone":          c.phone,
            "customer_type":  c.customer_type,
            "vehicle_type":   c.vehicle_type,
            "vehicle_number": c.vehicle_number,
            "vehicle_model":  c.vehicle_model,
            "last_message":   msgs.first().message if msgs.exists() else "",
        })
    return Response({"customers": data})
 
 
# ============================================================
#  TEMPLATE VIEWS
# ============================================================
 
def dashboard_view(request):
    return render(request, "dashboard.html")
 
 
def upload_page_view(request):
    return render(request, "upload.html")





















# # ============================================================
# #  bot/views.py
# # ============================================================

# from datetime import date
# import os
# import re
# import time

# import pandas as pd
# from django.core.cache import cache
# from django.shortcuts import render
# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response

# from bot.models import Customer, ChatMessage, UploadedFile, UploadBatch
# from bot.services.whatsapp_service import send_whatsapp_message
# from bot.services.renewal_service import run_renewal, run_new_insurance, run_all
# from bot.services.expiry_service import get_expiring_customers, get_new_insurance_customers


# # ============================================================
# #  CONSTANTS & CONFIG
# # ============================================================

# UPLOAD_PROGRESS_KEY = "upload_progress"

# CLOSING_KEYWORDS = {
#     "ok", "okay", "okk", "okkk",
#     "thank you", "thanks", "thankyou",
#     "bye", "bye bye", "goodbye", "thx", "ty",
# }

# POSITIVE_KEYWORDS = {
#     "yes", "yeah", "yup", "sure", "haan", "ha",
#     "renew", "please renew", "do it", "go ahead", "proceed",
# }

# NEGATIVE_KEYWORDS = {
#     "no", "nope", "not now", "later", "maybe later",
#     "don't", "do not", "not interested", "nahi", "na",
# }

# # ✅ NEW: greeting keywords to activate inbound bot
# GREETING_KEYWORDS = {
#     "hi", "hello", "hey", "hii", "helo", "hlw",
#     "hye", "start", "help", "namaskar", "namaste",
# }

# # ── Coverage options per vehicle type ──────────────────────
# COVERAGE_OPTIONS = {
#     "Car": [
#         ("Third Party",       2094),
#         ("Comprehensive",     8500),
#         ("Zero Depreciation", 12000),
#     ],
#     "Bike": [
#         ("Third Party",       714),
#         ("Comprehensive",     2500),
#         ("Long Term 2yr TP",  1200),
#         ("Long Term 3yr TP",  1600),
#     ],
#     "Commercial": [
#         ("Third Party",          4000),
#         ("Comprehensive",        15000),
#         ("Goods Carrying",       18000),
#         ("Passenger Carrying",   20000),
#     ],
#     "Auto": [
#         ("Third Party",    1500),
#         ("Comprehensive",  4500),
#     ],
#     "Tractor": [
#         ("Third Party Only",             1500),
#         ("Comprehensive + Farm Equip",   7000),
#         ("Fire & Theft Only",            3000),
#     ],
# }

# # ── Add-on options per vehicle type (name, extra premium) ──
# ADDON_OPTIONS = {
#     "Car": [
#         ("Zero Depreciation",  1500),
#         ("Roadside Assistance", 500),
#         ("Engine Protection",   800),
#         ("Return to Invoice",   700),
#         ("Key Replacement",     300),
#         ("Consumables Cover",   400),
#     ],
#     "Bike": [
#         ("Zero Depreciation",   500),
#         ("Roadside Assistance", 200),
#         ("Personal Accident",   300),
#     ],
#     "Commercial": [
#         ("Goods in Transit",  1500),
#         ("Driver PA Cover",    500),
#         ("Cleaner/Helper Cover", 300),
#     ],
#     "Auto": [
#         ("Passenger Cover (up to 3)", 400),
#         ("Driver PA Cover",           300),
#     ],
#     "Tractor": [
#         ("Driver PA Cover",          300),
#         ("Trolley/Attachment Cover", 600),
#     ],
# }

# PAYMENT_LINK = "https://your-payment-link.com"


# # ============================================================
# #  HELPERS
# # ============================================================

# def _set_progress(sent: int, total: int, active: bool) -> None:
#     cache.set(UPLOAD_PROGRESS_KEY, {"sent": sent, "total": total, "active": active}, timeout=3600)


# def _save_msg(customer: Customer, message: str, sender: str) -> None:
#     ChatMessage.objects.create(customer=customer, message=message, sender=sender)


# def _send_and_save(customer: Customer, reply: str) -> None:
#     send_whatsapp_message(customer.phone, reply)
#     _save_msg(customer, reply, "bot")


# def _has_any(text: str, keyword_set: set) -> bool:
#     return any(word in text for word in keyword_set)


# def _parse_expiry(raw) -> "date | None":
#     if pd.isnull(raw):
#         return None
#     try:
#         parsed = pd.to_datetime(raw, errors="coerce")
#         return parsed.date() if pd.notnull(parsed) else None
#     except Exception:
#         return None


# def _validate_vehicle_number(text: str) -> bool:
#     pattern = r'^[A-Z]{2}[\s\-]?\d{2}[\s\-]?[A-Z]{1,2}[\s\-]?\d{4}$'
#     return bool(re.match(pattern, text.upper().strip()))


# def _build_coverage_menu(vehicle_type: str) -> str:
#     options = COVERAGE_OPTIONS.get(vehicle_type, [])
#     lines = [f"{i+1}️⃣ {name}  (₹{price:,}/yr)" for i, (name, price) in enumerate(options)]
#     return "\n".join(lines)


# def _build_addon_menu(vehicle_type: str) -> str:
#     options = ADDON_OPTIONS.get(vehicle_type, [])
#     lines = [f"{i+1}️⃣ {name}  (+₹{price:,})" for i, (name, price) in enumerate(options)]
#     lines.append(f"{len(options)+1}️⃣ No add-ons")
#     return "\n".join(lines)


# def _calculate_premium(vehicle_type: str, coverage_index: int, addon_indices: list) -> tuple:
#     coverages = COVERAGE_OPTIONS.get(vehicle_type, [])
#     addons    = ADDON_OPTIONS.get(vehicle_type, [])

#     coverage_name, base_premium = coverages[coverage_index]

#     selected_addon_names = []
#     total_addon_premium  = 0

#     for idx in addon_indices:
#         if 0 <= idx < len(addons):
#             name, price = addons[idx]
#             selected_addon_names.append(name)
#             total_addon_premium += price

#     total     = base_premium + total_addon_premium
#     addon_str = ", ".join(selected_addon_names) if selected_addon_names else "None"

#     return coverage_name, addon_str, total


# # ============================================================
# #  WHATSAPP WEBHOOK — STATE MACHINE
# # ============================================================

# @api_view(["POST"])
# def whatsapp_webhook(request):
#     data = request.data

#     try:
#         if data.get("event") != "messages.received":
#             return Response({"status": "ignored"})

#         message_data = data.get("data", {}).get("messages", {})
#         phone        = message_data.get("key", {}).get("cleanedSenderPn")
#         raw_text     = message_data.get("messageBody", "")

#         if not phone or not raw_text:
#             return Response({"status": "no data"})

#         text = raw_text.lower().strip()
#         print(f"[webhook] phone={phone}  text={text!r}")

#         # ── Lookup customer — auto-create for inbound greetings ──
#         customer = Customer.objects.filter(phone=phone).first()

#         if not customer:
#             if _has_any(text, GREETING_KEYWORDS):
#                 # ✅ NEW: create a blank customer for inbound user
#                 customer = Customer.objects.create(
#                     phone=phone,
#                     name="User",
#                     conversation_state="inactive",
#                 )
#                 print(f"[webhook] New inbound customer created: {phone}")
#             else:
#                 return Response({"status": "user not found"})

#         _save_msg(customer, text, "user")

#         # ── Closing short-circuit ──────────────────────────────
#         if _has_any(text, CLOSING_KEYWORDS):
#             _send_and_save(customer, "You're welcome 😊 Say *Hi* anytime to start a new conversation 👋")
#             customer.conversation_state = "inactive"   # session reset
#             customer.save()
#             return Response({"status": "closed"})

#         state    = customer.conversation_state
#         positive = _has_any(text, POSITIVE_KEYWORDS)
#         negative = _has_any(text, NEGATIVE_KEYWORDS)
#         vtype    = customer.vehicle_type

#         # ══════════════════════════════════════════════════════
#         # ✅ NEW INBOUND STATES (added above existing flow)
#         # ══════════════════════════════════════════════════════

#         # ==================================================
#         # STATE: inactive
#         # User sends hi/hello → activate bot
#         # ==================================================
#         if state == "inactive":
#             if _has_any(text, GREETING_KEYWORDS):
#                 reply = (
#                     "Hello! 👋 Welcome to *Vehicle Insurance* 🚗🏍️\n\n"
#                     "I'm here to help you with insurance.\n\n"
#                     "What are you looking for?\n"
#                     "1️⃣ New Insurance\n"
#                     "2️⃣ Renewal"
#                 )
#                 customer.conversation_state = "ask_service_type"
#             else:
#                 reply = (
#                     "Hello! 👋 Please say *Hi* to get started 😊"
#                 )

#         # ==================================================
#         # STATE: ask_service_type
#         # User picks New Insurance (1) or Renewal (2)
#         # ==================================================
#         elif state == "ask_service_type":
#             if text == "1":
#                 customer.customer_type = "new"
#                 reply = (
#                     "Great! 😊 Let's get you insured.\n\n"
#                     "What type of vehicle do you have?\n"
#                     "1️⃣ Two Wheeler  (Bike / Scooter)\n"
#                     "2️⃣ Four Wheeler (Car / SUV / MUV)\n"
#                     "3️⃣ Other (Commercial / Auto / Tractor)"
#                 )
#                 customer.conversation_state = "ask_vehicle_category"

#             elif text == "2":
#                 customer.customer_type = "renewal"
#                 reply = (
#                     "Sure! Let's renew your policy 😊\n\n"
#                     "What type of vehicle do you have?\n"
#                     "1️⃣ Two Wheeler  (Bike / Scooter)\n"
#                     "2️⃣ Four Wheeler (Car / SUV / MUV)\n"
#                     "3️⃣ Other (Commercial / Auto / Tractor)"
#                 )
#                 customer.conversation_state = "ask_vehicle_category"

#             else:
#                 reply = (
#                     "Please reply with *1* or *2* 😊\n\n"
#                     "1️⃣ New Insurance\n"
#                     "2️⃣ Renewal"
#                 )

#         # ==================================================
#         # STATE: ask_vehicle_category
#         # 1 = Two Wheeler → Bike
#         # 2 = Four Wheeler → Car
#         # 3 = Other → ask sub-type
#         # ==================================================
#         elif state == "ask_vehicle_category":
#             if text == "1":
#                 customer.vehicle_type = "Bike"
#                 reply = (
#                     "Got it! 🏍️\n\n"
#                     "Please share your *vehicle registration number*:\n\n"
#                     "Example: *GJ05AB1234*"
#                 )
#                 customer.conversation_state = "ask_vehicle_details"

#             elif text == "2":
#                 customer.vehicle_type = "Car"
#                 reply = (
#                     "Got it! 🚗\n\n"
#                     "Please share your *vehicle registration number*:\n\n"
#                     "Example: *GJ01AB1234*"
#                 )
#                 customer.conversation_state = "ask_vehicle_details"

#             elif text == "3":
#                 reply = (
#                     "Please select your vehicle type:\n\n"
#                     "1️⃣ Commercial Vehicle (Truck / Bus / Tempo)\n"
#                     "2️⃣ Auto Rickshaw / E-Rickshaw\n"
#                     "3️⃣ Tractor / Farm Equipment"
#                 )
#                 customer.conversation_state = "ask_vehicle_other"

#             else:
#                 reply = (
#                     "Please reply with *1*, *2* or *3* 😊\n\n"
#                     "1️⃣ Two Wheeler\n"
#                     "2️⃣ Four Wheeler\n"
#                     "3️⃣ Other"
#                 )

#         # ==================================================
#         # STATE: ask_vehicle_other
#         # Sub-menu for Commercial / Auto / Tractor
#         # ==================================================
#         elif state == "ask_vehicle_other":
#             if text == "1":
#                 customer.vehicle_type = "Commercial"
#                 emoji = "🚛"
#             elif text == "2":
#                 customer.vehicle_type = "Auto"
#                 emoji = "🛺"
#             elif text == "3":
#                 customer.vehicle_type = "Tractor"
#                 emoji = "🚜"
#             else:
#                 reply = (
#                     "Please reply with *1*, *2* or *3* 😊\n\n"
#                     "1️⃣ Commercial Vehicle\n"
#                     "2️⃣ Auto Rickshaw / E-Rickshaw\n"
#                     "3️⃣ Tractor / Farm Equipment"
#                 )
#                 customer.save()
#                 _send_and_save(customer, reply)
#                 return Response({"status": "received"})

#             reply = (
#                 f"Got it! {emoji}\n\n"
#                 "Please share your *vehicle registration number*:\n\n"
#                 "Example: *GJ03AB1234*"
#             )
#             customer.conversation_state = "ask_vehicle_details"

#         # ==================================================
#         # STATE: ask_vehicle_details
#         # Step 1 — Ask vehicle number only
#         # ==================================================
#         elif state == "ask_vehicle_details":
#             vehicle_number = raw_text.strip().upper()

#             if _validate_vehicle_number(vehicle_number):
#                 customer.vehicle_number = vehicle_number
#                 customer.policy_type    = customer.vehicle_type  # backward compat

#                 reply = (
#                     f"Got it! ✅ *{vehicle_number}*\n\n"
#                     f"Now please share your *vehicle model*:\n\n"
#                     f"Example: *Honda Activa* / *Maruti Swift* / *Tata Ace*"
#                 )
#                 customer.conversation_state = "ask_vehicle_model"

#             else:
#                 reply = (
#                     "Please enter a valid vehicle registration number 😊\n\n"
#                     "Example: *GJ01AB1234*"
#                 )

#         # ==================================================
#         # STATE: ask_vehicle_model
#         # Step 2 — Ask vehicle model
#         # ==================================================
#         elif state == "ask_vehicle_model":
#             vehicle_model = raw_text.strip()

#             if len(vehicle_model) >= 2:
#                 customer.vehicle_model = vehicle_model

#                 vtype = customer.vehicle_type
#                 menu  = _build_coverage_menu(vtype)

#                 reply = (
#                     f"Perfect! 🚗\n\n"
#                     f"*Vehicle No* : {customer.vehicle_number}\n"
#                     f"*Model*      : {vehicle_model}\n"
#                     f"*Type*       : {vtype}\n\n"
#                     f"Now choose your coverage:\n\n"
#                     f"{menu}"
#                 )
#                 customer.conversation_state = "ask_coverage"

#             else:
#                 reply = (
#                     "Please enter your vehicle model 😊\n\n"
#                     "Example: *Honda Activa* / *Maruti Swift*"
#                 )

#         # ══════════════════════════════════════════════════════
#         # EXISTING OUTBOUND FLOW — UNCHANGED BELOW THIS LINE
#         # ══════════════════════════════════════════════════════

#         # ==================================================
#         # STATE: initial
#         # Outbound user replies to bot's first message
#         # ==================================================
#         elif state == "initial":
#             if positive:
#                 menu  = _build_coverage_menu(vtype)
#                 reply = (
#                     f"Great! Let's get started 😊\n\n"
#                     f"Choose your coverage for *{customer.vehicle_number or vtype}*:\n\n"
#                     f"{menu}"
#                 )
#                 customer.conversation_state = "ask_coverage"

#             elif negative:
#                 if customer.customer_type == "renewal":
#                     reply = (
#                         f"No worries 😊\n\n"
#                         f"Your policy expires on *{customer.expiry_date}*.\n"
#                         f"Should I remind you 3 days before expiry? (Yes / No)"
#                     )
#                 else:
#                     reply = (
#                         "No worries 😊\n\n"
#                         "But remember — driving uninsured is illegal ⚠️\n\n"
#                         "Should I follow up with you tomorrow? (Yes / No)"
#                     )
#                 customer.conversation_state = "ask_reminder"

#             else:
#                 if customer.customer_type == "renewal":
#                     reply = (
#                         f"I'm here to help 😊\n\n"
#                         f"Your *{vtype}* policy expires on *{customer.expiry_date}*.\n"
#                         f"Would you like to renew it? (Yes / No)"
#                     )
#                 else:
#                     reply = (
#                         f"I'm here to help 😊\n\n"
#                         f"Would you like to get insurance for your "
#                         f"*{vtype}* ({customer.vehicle_number})? (Yes / No)"
#                     )

#         # ==================================================
#         # STATE: ask_coverage
#         # ==================================================
#         elif state == "ask_coverage":
#             coverages = COVERAGE_OPTIONS.get(vtype, [])

#             if text.isdigit() and 1 <= int(text) <= len(coverages):
#                 idx = int(text) - 1
#                 customer.selected_coverage = str(idx)

#                 menu  = _build_addon_menu(vtype)
#                 reply = (
#                     f"Good choice! 👍\n\n"
#                     f"Now select add-ons for your *{vtype}*:\n"
#                     f"(Send numbers separated by space, e.g. *1 3*)\n\n"
#                     f"{menu}"
#                 )
#                 customer.conversation_state = "ask_addons"

#             else:
#                 menu  = _build_coverage_menu(vtype)
#                 reply = (
#                     f"Please reply with a number 1–{len(coverages)} 😊\n\n"
#                     f"{menu}"
#                 )

#         # ==================================================
#         # STATE: ask_addons
#         # ==================================================
#         elif state == "ask_addons":
#             addons     = ADDON_OPTIONS.get(vtype, [])
#             no_addon_n = len(addons) + 1
#             parts      = text.split()
#             valid      = True
#             addon_indices = []

#             for p in parts:
#                 if p.isdigit():
#                     n = int(p)
#                     if n == no_addon_n:
#                         addon_indices = []
#                         break
#                     elif 1 <= n <= len(addons):
#                         addon_indices.append(n - 1)
#                     else:
#                         valid = False
#                         break
#                 else:
#                     valid = False
#                     break

#             if not valid:
#                 menu  = _build_addon_menu(vtype)
#                 reply = (
#                     f"Please send valid numbers 😊\n\n"
#                     f"{menu}"
#                 )
#             else:
#                 cov_idx = int(customer.selected_coverage or "0")
#                 coverage_name, addon_str, total = _calculate_premium(vtype, cov_idx, addon_indices)

#                 customer.selected_addons = addon_str
#                 customer.quoted_premium  = total

#                 action = "renew" if customer.customer_type == "renewal" else "get insured"

#                 reply = (
#                     f"Here's your quote 📋\n"
#                     f"──────────────────────────\n"
#                     f"Name       : {customer.name}\n"
#                     f"Vehicle    : {customer.vehicle_number or 'N/A'}\n"
#                     f"Model      : {customer.vehicle_model or 'N/A'}\n"
#                     f"Type       : {vtype}\n"
#                     f"Coverage   : {coverage_name}\n"
#                     f"Add-ons    : {addon_str}\n"
#                     f"Premium    : ₹{total:,}/year\n"
#                     f"──────────────────────────\n\n"
#                     f"Shall I proceed to {action}? (Yes / No)"
#                 )
#                 customer.conversation_state = "show_quote"

#         # ==================================================
#         # STATE: show_quote
#         # ==================================================
#         elif state == "show_quote":
#             if positive:
#                 reply = (
#                     f"Perfect! 🎉\n\n"
#                     f"Click below to pay securely:\n"
#                     f"🔗 {PAYMENT_LINK}\n\n"
#                     f"Your policy will be issued within minutes "
#                     f"after payment ✅\n\n"
#                     f"Please reply *Done* once payment is complete."
#                 )
#                 customer.conversation_state = "payment_sent"

#             elif negative:
#                 menu  = _build_coverage_menu(vtype)
#                 reply = (
#                     f"No problem 😊 Let's pick again.\n\n"
#                     f"Choose your coverage for *{customer.vehicle_number or vtype}*:\n\n"
#                     f"{menu}"
#                 )
#                 customer.conversation_state = "ask_coverage"

#             else:
#                 reply = "Please reply *Yes* to proceed or *No* to change your plan 😊"

#         # ==================================================
#         # STATE: payment_sent
#         # ==================================================
#         elif state == "payment_sent":
#             payment_done = any(w in text for w in [
#                 "done", "paid", "payment done", "completed",
#                 "complete", "yes", "sent"
#             ])

#             if payment_done:
#                 if customer.customer_type == "renewal":
#                     action_msg = f"Your *{vtype}* insurance has been *renewed* ✅"
#                 else:
#                     action_msg = f"Your *{vtype}* is now *insured* ✅"

#                 reply = (
#                     f"🎉 Congratulations *{customer.name}*!\n\n"
#                     f"{action_msg}\n\n"
#                     f"Policy document will be sent to your "
#                     f"registered email/WhatsApp shortly 📧\n\n"
#                     f"Thank you for choosing us! 😊\n\n"
#                     f"Say *Hi* anytime if you need help again 👋"
#                 )
#                 customer.conversation_state = "inactive"   # session reset

#             else:
#                 reply = (
#                     f"Please complete the payment here:\n"
#                     f"🔗 {PAYMENT_LINK}\n\n"
#                     f"Reply *Done* once payment is complete 😊"
#                 )

#         # ==================================================
#         # STATE: ask_reminder
#         # ==================================================
#         elif state == "ask_reminder":
#             if positive:
#                 if customer.customer_type == "renewal":
#                     reply = (
#                         f"Done! ✅ I'll remind you 3 days before "
#                         f"your policy expires on *{customer.expiry_date}* 😊"
#                     )
#                 else:
#                     reply = (
#                         "Done! ✅ I'll follow up with you tomorrow 😊\n\n"
#                         "Remember — getting insured takes just 2 minutes! ⚡"
#                     )
#                 customer.conversation_state = "inactive"   # session reset

#             elif negative:
#                 reply = (
#                     "Alright 😊\n\n"
#                     "Feel free to reach out whenever you're ready.\n\n"
#                     "Say *Hi* anytime to start again! 👋"
#                 )
#                 customer.conversation_state = "inactive"   # session reset

#             else:
#                 reply = "Please reply *Yes* or *No* 😊"

#         # ==================================================
#         # STATE: policy_issued / done / closed — fallback
#         # ==================================================
#         else:
#             reply = (
#                 "I'm here if you need any help 😊\n\n"
#                 "You can always reach out for insurance queries!"
#             )

#         customer.save()
#         _send_and_save(customer, reply)

#     except Exception as e:
#         print(f"[webhook] ERROR: {e}")
#         import traceback; traceback.print_exc()

#     return Response({"status": "received"})


# # ============================================================
# #  TEST / TRIGGER ENDPOINTS
# # ============================================================

# @api_view(["GET"])
# def test_send_message(request):
#     phone   = "919104142402"
#     message = "Hello 👋 This is a test message from Django bot"
#     result  = send_whatsapp_message(phone, message)
#     return Response({"status": "message sent", "response": result})


# @api_view(["GET"])
# def run_renewal_api(request):
#     run_renewal()
#     return Response({"status": "renewal messages sent"})


# @api_view(["GET"])
# def run_new_insurance_api(request):
#     run_new_insurance()
#     return Response({"status": "new insurance messages sent"})


# @api_view(["GET"])
# def run_all_campaigns_api(request):
#     run_all()
#     return Response({"status": "all campaigns triggered"})


# # ============================================================
# #  FILE UPLOAD
# # ============================================================

# @api_view(["POST"])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def upload_file(request):
#     file = request.FILES.get("file")
#     if not file:
#         return Response({"error": "No file uploaded"}, status=400)

#     obj       = UploadedFile.objects.create(file=file)
#     file_path = obj.file.path
#     ext       = os.path.splitext(file_path)[1].lower()

#     customers_data = []

#     if ext in (".xlsx", ".xls"):
#         df = pd.read_excel(file_path)
#         print("[upload] Columns:", df.columns.tolist())

#         for _, row in df.iterrows():
#             phone = str(row.get("phone") or "").strip()
#             if not phone:
#                 continue

#             raw_ctype     = str(row.get("customer_type") or "renewal").strip().lower()
#             customer_type = "new" if raw_ctype == "new" else "renewal"

#             raw_vtype    = str(row.get("vehicle_type") or "Car").strip().title()
#             valid_types  = {"Car", "Bike", "Commercial", "Auto", "Tractor"}
#             vehicle_type = raw_vtype if raw_vtype in valid_types else "Car"

#             customers_data.append({
#                 "name":           str(row.get("name") or "Customer").strip(),
#                 "phone":          phone,
#                 "customer_type":  customer_type,
#                 "vehicle_type":   vehicle_type,
#                 "vehicle_number": str(row.get("vehicle_number") or "").strip() or None,
#                 "vehicle_model":  str(row.get("vehicle_model") or "").strip() or None,
#                 "policy_type":    vehicle_type,
#                 "expiry_date":    _parse_expiry(row.get("policy_expiry")),
#             })

#     else:
#         return Response({"error": f"Unsupported file type: {ext}. Please upload .xlsx"}, status=400)

#     batch = UploadBatch.objects.create(name=file.name, customer_count=len(customers_data))

#     for c in customers_data:
#         customer, created = Customer.objects.get_or_create(
#             phone=c["phone"],
#             defaults={
#                 "name":           c["name"],
#                 "customer_type":  c["customer_type"],
#                 "vehicle_type":   c["vehicle_type"],
#                 "vehicle_number": c["vehicle_number"],
#                 "vehicle_model":  c["vehicle_model"],
#                 "policy_type":    c["policy_type"],
#                 "expiry_date":    c["expiry_date"],
#             },
#         )
#         if not created:
#             customer.name           = c["name"]
#             customer.customer_type  = c["customer_type"]
#             customer.vehicle_type   = c["vehicle_type"]
#             customer.vehicle_number = c["vehicle_number"]
#             customer.vehicle_model  = c["vehicle_model"]
#             customer.policy_type    = c["policy_type"]
#             customer.expiry_date    = c["expiry_date"]

#         customer.conversation_state = "initial"   # outbound customers → initial
#         customer.reminder_sent      = False
#         customer.batch              = batch
#         customer.save()

#     from bot.services.renewal_service import (
#         RENEWAL_TEMPLATE, NEW_INSURANCE_TEMPLATE, _send_and_log
#     )

#     renewal_customers = list(Customer.objects.filter(batch=batch, customer_type="renewal"))
#     new_customers     = list(Customer.objects.filter(batch=batch, customer_type="new"))

#     total      = len(renewal_customers) + len(new_customers)
#     sent_count = 0
#     _set_progress(sent=0, total=total, active=True)

#     for c in renewal_customers:
#         msg = RENEWAL_TEMPLATE.format(
#             name=c.name,
#             vehicle_type=c.vehicle_type,
#             vehicle_number=c.vehicle_number or "N/A",
#             expiry_date=c.expiry_date,
#         )
#         print(f"[upload] Renewal → {c.phone}")
#         _send_and_log(c, msg)
#         sent_count += 1
#         _set_progress(sent=sent_count, total=total, active=True)
#         time.sleep(2)

#     for c in new_customers:
#         msg = NEW_INSURANCE_TEMPLATE.format(
#             name=c.name,
#             vehicle_type=c.vehicle_type,
#             vehicle_number=c.vehicle_number or "N/A",
#         )
#         print(f"[upload] New insurance → {c.phone}")
#         _send_and_log(c, msg)
#         sent_count += 1
#         _set_progress(sent=sent_count, total=total, active=True)
#         time.sleep(2)

#     _set_progress(sent=total, total=total, active=False)

#     return Response({
#         "status":             "file processed & messages sent",
#         "customers_found":    len(customers_data),
#         "renewal_sent":       len(renewal_customers),
#         "new_insurance_sent": len(new_customers),
#     })


# # ============================================================
# #  UPLOAD PROGRESS
# # ============================================================

# @api_view(["GET"])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def get_upload_progress(request):
#     progress = cache.get(UPLOAD_PROGRESS_KEY, {"sent": 0, "total": 0, "active": False})
#     return Response(progress)


# # ============================================================
# #  CONVERSATION ENDPOINTS
# # ============================================================

# @api_view(["GET"])
# def get_conversations(request):
#     customers = Customer.objects.prefetch_related("chatmessage_set").all()
#     data = []
#     for c in customers:
#         msgs = c.chatmessage_set.order_by("-timestamp")
#         data.append({
#             "id":             c.id,
#             "name":           c.name,
#             "phone":          c.phone,
#             "customer_type":  c.customer_type,
#             "vehicle_type":   c.vehicle_type,
#             "vehicle_number": c.vehicle_number,
#             "vehicle_model":  c.vehicle_model,
#             "last_message":   msgs.first().message if msgs.exists() else "",
#         })
#     return Response({"conversations": data})


# @api_view(["GET"])
# def get_messages(request, customer_id):
#     messages = (
#         ChatMessage.objects
#         .filter(customer_id=customer_id)
#         .order_by("timestamp")
#         .values("message", "sender", "timestamp")
#     )
#     return Response({"messages": list(messages)})


# @api_view(["POST"])
# def send_message_dashboard(request):
#     customer_id = request.data.get("customer_id")
#     message     = request.data.get("message", "").strip()

#     if not customer_id or not message:
#         return Response({"error": "customer_id and message are required"}, status=400)

#     try:
#         customer = Customer.objects.get(id=customer_id)
#     except Customer.DoesNotExist:
#         return Response({"error": "Customer not found"}, status=404)

#     send_whatsapp_message(customer.phone, message)
#     _save_msg(customer, message, "bot")
#     return Response({"status": "sent"})


# # ============================================================
# #  DASHBOARD
# # ============================================================

# @api_view(["GET"])
# def dashboard_data(request):
#     customers = Customer.objects.prefetch_related("chatmessage_set").all()
#     table_data = []

#     for c in customers:
#         msgs      = c.chatmessage_set.order_by("timestamp")
#         first_msg = msgs.first()
#         last_msg  = msgs.last()

#         table_data.append({
#             "id":             c.id,
#             "phone":          c.phone,
#             "name":           c.name,
#             "customer_type":  c.customer_type,
#             "vehicle_type":   c.vehicle_type,
#             "vehicle_number": c.vehicle_number,
#             "vehicle_model":  c.vehicle_model,
#             "expiry_date":    c.expiry_date,
#             "first_contact":  first_msg.timestamp if first_msg else None,
#             "last_contact":   last_msg.timestamp  if last_msg  else None,
#         })

#     return Response({
#         "total_customers":     customers.count(),
#         "total_renewal":       customers.filter(customer_type="renewal").count(),
#         "total_new":           customers.filter(customer_type="new").count(),
#         "total_messages":      ChatMessage.objects.count(),
#         "total_conversations": customers.count(),
#         "customers":           table_data,
#     })


# # ============================================================
# #  BATCH ENDPOINTS
# # ============================================================

# @api_view(["GET"])
# def get_batches(request):
#     batches = UploadBatch.objects.order_by("-uploaded_at").values(
#         "id", "name", "uploaded_at", "customer_count"
#     )
#     return Response({"batches": list(batches)})


# @api_view(["GET"])
# def get_batch_customers(request, batch_id):
#     customers = Customer.objects.filter(batch_id=batch_id).prefetch_related("chatmessage_set")
#     data = []
#     for c in customers:
#         msgs = c.chatmessage_set.order_by("-timestamp")
#         data.append({
#             "id":             c.id,
#             "name":           c.name,
#             "phone":          c.phone,
#             "customer_type":  c.customer_type,
#             "vehicle_type":   c.vehicle_type,
#             "vehicle_number": c.vehicle_number,
#             "vehicle_model":  c.vehicle_model,
#             "last_message":   msgs.first().message if msgs.exists() else "",
#         })
#     return Response({"customers": data})


# # ============================================================
# #  TEMPLATE VIEWS
# # ============================================================

# def dashboard_view(request):
#     return render(request, "dashboard.html")


# def upload_page_view(request):
#     return render(request, "upload.html")
