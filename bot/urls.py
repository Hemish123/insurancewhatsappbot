# from django.urls import path
# from .views import dashboard_data, dashboard_view, test_send_message,run_renewal_api, upload_file,whatsapp_webhook,get_conversations, get_messages, send_message_dashboard, upload_page_view, get_batches, get_batch_customers, get_upload_progress


# urlpatterns = [
#     path("test-send/", test_send_message),
#     path("run-renewal/", run_renewal_api),   # ✅ ADD THIS
#     path("webhook/", whatsapp_webhook),
#     path("dashboard/", dashboard_view),
#     path("dashboard/conversations/", get_conversations),
#     path("dashboard/messages/<int:customer_id>/", get_messages),
#     path("dashboard/data/", dashboard_data),
#     path("dashboard/send/", send_message_dashboard),
#     path("dashboard/batches/", get_batches),
#     path("dashboard/batches/<int:batch_id>/customers/", get_batch_customers),
#     path("upload/", upload_file),
#     path("upload/progress/", get_upload_progress),
#     path("upload-page/", upload_page_view),
# ]
















# ============================================================
#  bot/urls.py
# ============================================================

from django.urls import path
from .views import (
    # test / triggers
    test_send_message,
    run_renewal_api,
    run_new_insurance_api,
    run_all_campaigns_api,

    # webhook
    whatsapp_webhook,

    # upload
    upload_file,
    get_upload_progress,
    upload_page_view,

    # conversations
    get_conversations,
    get_messages,
    send_message_dashboard,

    # dashboard
    dashboard_view,
    dashboard_data,

    # batches
    get_batches,
    get_batch_customers,
)

urlpatterns = [

    # ── Test & manual triggers ──────────────────────────────
    path("test-send/",          test_send_message),
    path("run-renewal/",        run_renewal_api),
    path("run-new-insurance/",  run_new_insurance_api),   # NEW
    path("run-all-campaigns/",  run_all_campaigns_api),   # NEW

    # ── WhatsApp webhook ────────────────────────────────────
    path("webhook/",            whatsapp_webhook),

    # ── File upload ─────────────────────────────────────────
    path("upload/",             upload_file),
    path("upload/progress/",    get_upload_progress),
    path("upload-page/",        upload_page_view),

    # ── Dashboard ───────────────────────────────────────────
    path("dashboard/",                                  dashboard_view),
    path("dashboard/data/",                             dashboard_data),
    path("dashboard/conversations/",                    get_conversations),
    path("dashboard/messages/<int:customer_id>/",       get_messages),
    path("dashboard/send/",                             send_message_dashboard),
    path("dashboard/batches/",                          get_batches),
    path("dashboard/batches/<int:batch_id>/customers/", get_batch_customers),
]
