from django import forms

class PrivacyConsentForm(forms.Form):
    accept_privacy_policy = forms.BooleanField(required=True, label="I accept the Privacy Policy")
