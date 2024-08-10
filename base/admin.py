from django.contrib import admin
from .models import CreatorProfile , BrandProfile , BrandProposal , InstagramAccountDashBoard , Content_Approval_Images
# Register your models here.

admin.site.register(CreatorProfile)
admin.site.register(BrandProfile)
admin.site.register(BrandProposal)
admin.site.register(InstagramAccountDashBoard)
admin.site.register(Content_Approval_Images)
