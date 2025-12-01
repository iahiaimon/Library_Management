from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter
def get_modal_color(message_text):
    """Determine color based on message content"""
    if 'rejected' in str(message_text).lower():
        return 'danger'  # Red
    elif 'pending' in str(message_text).lower():
        return 'warning'  # Orange/Yellow
    return 'info'  # Blue

@register.filter
def get_modal_icon(message_text):
    """Determine icon based on message content"""
    if 'rejected' in str(message_text).lower():
        return '❌'
    elif 'pending' in str(message_text).lower():
        return '⏳'
    return 'ℹ️'
