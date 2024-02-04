from django.contrib import admin
from .models import Message, Answer


class MessageAdmin(admin.ModelAdmin):
    list_display = ['contents', 'created_at']


class AnswerAdmin(admin.ModelAdmin):
    list_display = ['departure', 'destination','stay','created_at']


admin.site.register(Message, MessageAdmin)

admin.site.register(Answer, AnswerAdmin)

# Register your models here.
