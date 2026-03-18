from django.urls import path
from .views import dashboard_data, dashboard_view, test_send_message,run_renewal_api, upload_file,whatsapp_webhook,get_conversations, get_messages, send_message_dashboard, upload_page_view


urlpatterns = [
    path("test-send/", test_send_message),
    path("run-renewal/", run_renewal_api),   # ✅ ADD THIS
    path("webhook/", whatsapp_webhook),
    path("dashboard/", dashboard_view),
    path("dashboard/conversations/", get_conversations),
    path("dashboard/messages/<int:customer_id>/", get_messages),
    path("dashboard/data/", dashboard_data),
    path("dashboard/send/", send_message_dashboard),
    path("upload/", upload_file),
    path("upload-page/", upload_page_view),
]
