from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .exercise_tests import parse_private_tests
from .models import Exercise


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)


class ExerciseAdminForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = '__all__'

    def clean_private_tests(self):
        value = self.cleaned_data['private_tests']
        # Draft exercises can be saved without tests; evaluation requires them.
        if value:
            try:
                parse_private_tests(value)
            except ValueError as exc:
                raise forms.ValidationError(str(exc)) from exc
        return value
