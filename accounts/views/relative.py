from accounts.forms.profile_forms import RelativeForm, RelativeUpdateForm
from accounts.models import RelativeModel
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


def relatives(request):
    template = "accounts/relative/list.html"
    queryset = RelativeModel.objects.filter(relative = request.user)

    return render(request, template, {"relatives": queryset})

def relative(request, id):
    relative = get_object_or_404(RelativeModel, id=id)
    return render(request, "accounts/relative/details.html", {"relative": relative})

def create_relative(request):
    template = "accounts/relative/create.html"
    if request.method == 'POST':
        form = RelativeForm(request.POST, request.FILES)
        if form.is_valid() and form.is_multipart():
            relative = form.save(commit=False)
            relative.relative = request.user
            print(form)
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
        print(form)
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
