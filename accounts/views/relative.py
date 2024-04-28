from accounts.forms.profile_forms import RelativeForm, RelativeUpdateForm
from accounts.models import RelativeModel
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from accounts.utils import RelationShip


def relatives(request):
    template = "accounts/relative/list.html"
    queryset = RelativeModel.objects.filter(relative = request.user)
    query = request.GET.get("query", None)
    if query:
        queryset = queryset.filter(Q(full_name__icontains=query) | Q(maiden_name__icontains=query) | Q(surname__icontains=query))

    return render(request, template, {"relatives": queryset, "query": query})

def relative(request, id):
    relative = get_object_or_404(RelativeModel, id=id)
    return render(request, "accounts/relative/details.html", {"relative": relative})

def validate_relative(clean, request):
    name = clean.get("full_name", None)
    last_name = clean.get("surname", None)
    other_surname = clean.get("maiden_name", None)
    title = clean.get("title", None)
    gender = clean.get("gender", None)
    relative = request.user.relatives.filter(title=title, full_name = name, surname = last_name, maiden_name = other_surname, gender=gender).exists()

    return relative

def create_relative(request):
    template = "accounts/relative/create.html"
    if request.method == 'POST':
        form = RelativeForm(request.POST, request.FILES)
        if form.is_valid() and form.is_multipart():
            clean = form.cleaned_data
            relative = validate_relative(clean, request)
            if relative:
                messages.error(request,f"Relative with following details already exists")
                return render(request, template, {"form": form})
            
            relative = form.save(commit=False)
            relative.relative = request.user
            relative.save()
            messages.success(request, "Your relative was added successfully")
            return redirect("accounts:relatives")
        else:
            return render(request, template, {"form": form})
    
    form = RelativeForm()
    return render(request, template, {"form": form})

def update_relative(request, id):
    template = "accounts/relative/update.html"
    model = get_object_or_404(RelativeModel, relative=request.user, id=id)
    if request.method == 'POST':
        form = RelativeUpdateForm(instance=model,data=request.POST, files=request.FILES)
        if form.is_valid() and form.is_multipart():
            relative = form.save(commit=False)
            relative.save()
            messages.success(request, "Your relative was updated successfully")
            return redirect("accounts:relatives")
        else:
            return render(request, template, {"form": form})
    
    form = RelativeUpdateForm(instance=model)
    return render(request, template, {"form": form})

def delete_relative(request, id):
    model = get_object_or_404(RelativeModel, relative=request.user, id=id)
    model.delete()
    return redirect("accounts:relatives")
