from django import forms
from .models import InstagramAccountDashBoard , BrandDeal , TiktokDashboard 

account_choices = (
    ("creator" , "Creator"),
    ("brand" , "Brand")
)



#account-selection
class AccountTypeForm(forms.Form):
    account_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=account_choices,
        required=True , 
        label="Select Account"
    )
class DashboardImageForm(forms.Form):
    dashboard_img = forms.FileField(
        widget= forms.FileInput(
            attrs = {
                'accept':'image/*'
            }
        )
    )

class AccountIntegrationForm(forms.ModelForm):
    class Meta:
        model = InstagramAccountDashBoard
        fields = ('username' , 'tags' ,'followers' , 'reach' , 'profile_link_clicks' ,'engagement' , 'audience_country' , 'story_rates' , 'reel_rates' ,)

class BrandProposalForm(forms.ModelForm):
    class Meta:
        model = BrandDeal
        fields = ('description' , 'timeline', 'content_type' , 'proposed_amount' , 'product_link' )

class TiktokBrandProposalForm(forms.ModelForm):
    class Meta:
        model = BrandDeal
        fields = ('description' , 'timeline', 'proposed_amount' , 'product_link' )


from django import forms

class EmailVerificationForm(forms.Form):
    verification_code = forms.CharField(max_length=6, required=True, label='Verification Code')
class BrandSubscriptionForm(forms.Form):
    # ChoiceField to restrict user to 3, 6, or 12 months
    MONTH_CHOICES = [
        (3, '3 Months - $15'),
        (6, '6 Months - $30'),
        (12, '12 Months - $60'),
    ]

    months = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label='Subscription Duration',
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'subscription-options'})
    )
    
    