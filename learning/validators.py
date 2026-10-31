from django.contrib.auth.password_validation import MinimumLengthValidator
from django.utils.translation import get_language


class LocalizedMinimumLengthValidator(MinimumLengthValidator):
    """Supply the missing Portuguese plural translation in Django's catalog."""

    def get_error_message(self):
        if (get_language() or '').startswith('pt'):
            return f'Esta palavra-passe é demasiado curta. Deve conter pelo menos {self.min_length} caracteres.'
        return super().get_error_message()
