from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Option, Poll


User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)


class Meta:
    model = User
    fields = (User.USERNAME_FIELD, 'email', 'password1', 'password2')


class VoteForm(forms.Form):
    option = forms.ChoiceField(widget=forms.RadioSelect)


    def __init__(self, *args, **kwargs):
        options_queryset = kwargs.pop('options_queryset')
        super().__init__(*args, **kwargs)
        self.fields['option'].choices = [(str(o.id), o.text) for o in options_queryset]

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    
    
class PollForm(forms.ModelForm):
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text='Leave blank for no expiry'
    )
    
    class Meta:
        model = Poll
        fields = ['question', 'expires_at', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your poll question...',
                'required': True
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter option text...',
                'required': True
            })
        }