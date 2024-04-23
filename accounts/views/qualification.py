from accounts.models import QualificationModel
from accounts.forms.profile_forms import QualificationForm, QualificationUpdateForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


def qualifications(request):
    template = "accounts/qualification/list.html"
    queryset = QualificationModel.objects.filter(owner = request.user)

    return render(request, template, {"qualifications": queryset})

def create_qualification(request):
    template = "accounts/qualification/create.html"
    if request.method == 'POST':
        form = QualificationForm(request.POST)
        if form.is_valid():
            qualification = form.save(commit=False)
            qualification.owner = request.user
            qualification.save()
            messages.success(request, "Your qualification was added successfully")
            return redirect("accounts:qualifications")
        else:
            return render(request, template, {"form": form})
    
    form = QualificationForm()
    return render(request, template, {"form": form})

def update_qualification(request, id):
    template = "accounts/qualification/update.html"
    model = get_object_or_404(QualificationModel, owner=request.user, id=id)
    if request.method == 'POST':
        form = QualificationUpdateForm(instance=model, data=request.POST)
        if form.is_valid():
            qualification = form.save(commit=False)
            qualification.save()
            messages.success(request, "Your qualification was added successfully")
            return redirect("accounts:qualifications")
        else:
            return render(request, template, {"form": form})
    
    form = QualificationUpdateForm(instance=model)
    return render(request, template, {"form": form})

def delete_qualification(request, id):
    model = get_object_or_404(QualificationModel, owner=request.user, id=id)
    model.delete()
    return redirect("accounts:qualifications")
