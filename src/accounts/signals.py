from django.dispatch import Signal

user_logged_in = Signal(['instance', 'request'])