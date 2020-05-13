from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    """Форма для регистрации пользователя"""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'username')
