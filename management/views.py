from django.shortcuts import render, redirect
from django.http import HttpResponse


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
# Create your views here.


@login_required
def home(request):
    return render(request, 'management/home.html')


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'management/register.html', {'form': form})
