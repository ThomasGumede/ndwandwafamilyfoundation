from accounts.forms.profile_forms import RelativeForm, RelativeUpdateForm
from accounts.models import RelativeModel, CustomUserModel
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from accounts.utils import RelationShip
from django.http import HttpResponseForbidden, JsonResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
# from rest_framework import serializers


def relatives_api(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        search = request.GET.get("search_value", None)
        if search:
            relatives_data = RelativeModel.objects.filter(full_name__icontains=search).select_related("relative")
            relatives_ser = serializers.serialize('json', relatives_data, use_natural_foreign_keys=True, use_natural_primary_keys=True)
            return JsonResponse({"success": True, "data": relatives_ser})
        else:
            return JsonResponse({"success": False})
    else:
        return JsonResponse({"success": False, 'message': 'Bad request'}, status=500)


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
    relative_id = clean.get("relative_id", None)
    if relative_id:
        relative = request.user.relatives.filter(id=relative_id).exists()
    else:
        relative = request.user.relatives.filter(title=title, full_name = name, surname = last_name, maiden_name = other_surname, gender=gender).exists()

    return relative

@login_required
def create_relative(request):
    template = "accounts/relative/create.html"
    if request.method == 'POST':
        form = RelativeForm(request.POST, request.FILES)
        if form.is_valid() and form.is_multipart():
            clean = form.cleaned_data
            if validate_relative(clean, request):
                messages.error(request, "A relative with the same details already exists.")
                return render(request, template, {"form": form})

            relative = form.save(commit=False)
            relative.relative = request.user
            relative.save()
            messages.success(request, "Your relative was added successfully.")
            return redirect("accounts:relatives")
        else:
            messages.error(request, "Invalid form submission.")
    else:
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
