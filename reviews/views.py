from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import *
# Create your views here.

def get_proposal(request,pk):
    proposal=get_object_or_404(Proposal,pk=pk)
    creator=get_object_or_404(Creator,pk=pk)
    brand=get_object_or_404(Brand,pk=pk)
    context = {
        'proposal': proposal,
        'creator': proposal.Creator,
        'brand': proposal.Brand
    }
    return render(request,'proposal_details.html',proposal)
def get_creator_details(request,pk):
    creator = get_object_or_404(Creator, pk=pk)
    context = {'creator': creator}
    return render(request,'proposal.html',creator)

def get_brand_detail(request,pk):
    brand=get_object_or_404(Brand,pk=pk)

    context = {'brand': brand}
    return render(request, 'proposal.html', brand)


