from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import FoodgramUser


class UserCreationForm(UserCreationForm):

    class Meta:

        model = FoodgramUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password')


class UserChangeForm(UserChangeForm):

    class Meta:

        model = FoodgramUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password')
