# from django.contrib import admin

# # Register your models here.
# from django.contrib import admin
# from .models import Customer

# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ("name", "phone", "policy_type", "expiry_date", "reminder_sent")
#     search_fields = ("name", "phone")
#     list_filter = ("policy_type", "reminder_sent")

from django.contrib import admin
from .models import Customer, ChatMessage, UploadedFile


# ✅ INLINE CHAT (THIS IS KEY)
class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    ordering = ['timestamp']
    readonly_fields = ("message", "sender", "timestamp")
    can_delete = False


# ✅ CUSTOMER ADMIN (MAIN VIEW)
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "policy_type", "expiry_date")
    inlines = [ChatMessageInline]   # 🔥 THIS GROUPS MESSAGES

admin.site.register(UploadedFile)