from django.forms import ModelForm
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Profile

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'displayname', 'email', 'location', 'info', ]
        labels = {
            'displayname': 'Full name'
        }
        widgets = {
            'image': forms.FileInput(),
            'displayname' : forms.TextInput(attrs={'placeholder': 'Add display name'}),
            'email' : forms.TextInput(attrs={'placeholder': 'Enter email address'}),
            'location' : forms.TextInput(attrs={'placeholder': 'Enter your location'}),
            'info' : forms.Textarea(attrs={'rows':3, 'placeholder': 'Add information'})
        }
        

class ProfileDeactivationForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'required': True
        }),
        label='Current Password',
        help_text='Please confirm your password to deactivate your account.'
    )
    
    confirmation = forms.BooleanField(
        required=True,
        label='I understand that deactivating my account will:',
        help_text='• Log me out immediately • Disable my account • Hide my profile from other users'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Verify the password is correct
            if not self.user.check_password(password):
                raise ValidationError('Incorrect password. Please try again.')
        return password
    

class ProfileReactivationForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'required': True
        }),
        label='Current Password',
        help_text='Please confirm your password to reactivate your account.' 
    )
    
    confirmation = forms.BooleanField(
        required=True,
        label='I consent to the reactivation of my account. I agree to the terms and conditions of Lanuelgram.'
    )
    
    def __init__(self, user=None, *args, **kwargs):  # Made user optional with default None
        self.user = user
        super().__init__(*args, **kwargs)
        
        # If no user is provided, disable the form
        if not self.user:
            for field in self.fields.values():
                field.disabled = True
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Verify the password is correct
            if not self.user.check_password(password):
                raise ValidationError('Incorrect password. Please try again.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Add form-level validation if no user is available
        if not self.user:
            raise ValidationError('Invalid reactivation request. Please use a valid reactivation link.')
        
        return cleaned_data
    
                
class EmailForm(ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']


class UsernameForm(ModelForm):
    class Meta:
        model = User
        fields = ['username']
