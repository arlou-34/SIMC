from django import forms
from .models import PersonRecord

class VehicularAccidentForm(forms.ModelForm):
    class Meta:
        model = PersonRecord
        fields = ['age', 'gender', 'vehicle_type','patient_type',
                  'v_referred', 'v_facility', 'v_status']

class InjuryForm(forms.ModelForm):
    class Meta:
        model = PersonRecord
        fields = ['age', 'gender', 'injury_mechanism', 
                  'i_referred', 'i_facility', 'i_status']

class SuicideForm(forms.ModelForm):
    class Meta:
        model = PersonRecord
        fields = ['age', 'gender', 'suicide_mechanism',
                  's_referred', 's_facility', 's_status']


from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
