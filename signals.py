# learning_modules/signals.py
from django.dispatch import Signal

module_downloaded = Signal(providing_args=["module", "user"])
