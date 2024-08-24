from django import forms
from .models import InstagramAccountDashBoard , BrandProposal

account_choices = (
    ("creator" , "Creator"),
    ("brand" , "Brand")
)


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
        model = BrandProposal
        fields = ('description' , 'timeline', 'content_type' , 'proposed_amount' , 'item_link' )


class EmailVerificationForm(forms.Form):
    email_code = forms.CharField(max_length=200 ,
                                 min_length=4, 
                                 required=True , 
                                 widget=forms.TextInput(attrs={'placeholder':"Enter 4 Digit Verification Code"}), 
                                 help_text="Enter 4 digit Code Sent to Your Email"
                                 )