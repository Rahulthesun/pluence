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


