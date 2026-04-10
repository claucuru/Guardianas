from django import forms

class LoginForm(forms.Form):
    nombreUsuario = forms.CharField()
    contrasena = forms.CharField(widget=forms.PasswordInput)
    
