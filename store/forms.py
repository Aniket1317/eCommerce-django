from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Contact

class SignUpForm(UserCreationForm):
	first_name = forms.CharField(max_length=100, required=True)
	last_name = forms.CharField(max_length=100, required=True)
	email = forms.EmailField(max_length=150, help_text='eg. youremail@gmail.com')

	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'username', 'password1', 'password2', 'email']

class ContactForm(forms.Form):
	full_name = forms.CharField(max_length=500)
	subject = forms.CharField(max_length=250)
	email = forms.EmailField()
	content = forms.CharField(widget= forms.Textarea)

class ContactModelForm(forms.ModelForm):
	class Meta:
		model = Contact
		fields = ['full_name','subject', 'email', 'content']

