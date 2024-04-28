from accounts.models import QualificationModel
from accounts.forms.profile_forms import QualificationForm, QualificationUpdateForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

def validate_qualification(clean, request):
    name = clean.get("title", None)
    last_name = clean.get("institution", None)
    other_surname = clean.get("year", None)
    qual_type = clean.get("qualification_type", None)
    qualification = request.user.qualifications.filter(title = name, institution = last_name, year = other_surname, qualification_type= qual_type).exists()
    return qualification

def qualifications(request):
    template = "accounts/qualification/list.html"
    queryset = QualificationModel.objects.filter(owner = request.user)

    return render(request, template, {"qualifications": queryset})

def create_qualification(request):
    template = "accounts/qualification/create.html"
    if request.method == 'POST':
        form = QualificationForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            qualification_found = validate_qualification(clean, request)
            if qualification_found:
                messages.error(request, "Qualification with following details already exists")
                return render(request, template, {"form": form})
            
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
