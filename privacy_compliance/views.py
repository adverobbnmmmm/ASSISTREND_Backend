from django.shortcuts import render

def privacy_policy_consent_view(request):
    return render(request, 'privacy_compliance/privacy_consent.html')
def privacy_policy_view(request):
    return render(request, 'privacy_compliance/privacy_policy.html')
