

# Create your models here.
from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    policy_type = models.CharField(max_length=100)
    expiry_date = models.DateField()
    reminder_sent = models.BooleanField(default=False)

    conversation_state = models.CharField(
        max_length=50,
        default="initial")

    def __str__(self):
        return self.name
    
# 🔥 NEW MODEL
class ChatMessage(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    message = models.TextField()
    sender = models.CharField(max_length=10)  # "user" or "bot"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.sender}"
    
class UploadedFile(models.Model):
    file = models.FileField(upload_to="uploads/")
    file_type = models.CharField(max_length=20, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name