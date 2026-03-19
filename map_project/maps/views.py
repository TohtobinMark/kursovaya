# maps/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Location
from .forms import LocationForm


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def home(request):
    if request.user.is_authenticated:
        locations = Location.objects.filter(user=request.user)
    else:
        locations = Location.objects.none()  # Пустой queryset для неавторизованных

    context = {
        'locations': locations,
        'YANDEX_MAPS_API_KEY': getattr(settings, 'YANDEX_MAPS_API_KEY', ''),
    }
    return render(request, 'maps/home.html', context)


# maps/views.py - обновляем функции add_location и edit_location
@login_required
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.user = request.user
            location.save()
            messages.success(request, 'Местоположение успешно добавлено!')
            # Редирект на детальную страницу нового маркера
            return redirect('location_detail', pk=location.id)

@login_required
def edit_location(request, pk):
    location = get_object_or_404(Location, pk=pk, user=request.user)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, 'Местоположение успешно обновлено!')
            # Редирект на детальную страницу
            return redirect('location_detail', pk=location.id)
    # ... остальной код без изменений

@login_required
def delete_location(request, pk):
    location = get_object_or_404(Location, pk=pk, user=request.user)
    if request.method == 'POST':
        location.delete()
        messages.success(request, 'Местоположение удалено!')
        return redirect('home')
    return render(request, 'maps/confirm_delete.html', {'location': location})

@login_required
def home(request):
    locations = Location.objects.filter(user=request.user)
    context = {
        'locations': locations,
        'YANDEX_MAPS_API_KEY': settings.YANDEX_MAPS_API_KEY,
    }
    return render(request, 'maps/home.html', context)

@login_required
def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk, user=request.user)
    return render(request, 'maps/location_detail.html', {'location': location})