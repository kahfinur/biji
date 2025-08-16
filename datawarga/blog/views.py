from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import PostForm, WargaForm
from django.db.models import Q
from .models import AuthPassword, Warga



def home(request):
    return render(request, 'blog/home.html')

def halaman1(request):
    return render(request, 'blog/halaman1.html')



# Create your views here.

def home(request):
    error_message = None
    
    if request.method == 'POST':
        input_password = request.POST.get('password')
        # Cek apakah password ada di database
        if AuthPassword.objects.filter(password=input_password).exists():
            return redirect('halaman1')
        else:
            error_message = "Password salah!"
    
    return render(request, 'blog/home.html', {'error_message': error_message})

def halaman1(request):
    if request.method == 'POST':
        form = WargaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = WargaForm()
    
    return render(request, 'blog/halaman1.html', {'form': form})

def halaman2(request):
    #semua_warga = Warga.objects.all().order_by('-created_at')  # Urutkan dari yang terbaru
    #return render(request, 'blog/halaman2.html', {'daftar_warga': semua_warga})
    query = request.GET.get('q', '')
    if query:
        daftar_warga = Warga.objects.filter(
            Q(nama__icontains=query) | Q(alamat__icontains=query) | Q(rt__icontains=query) | Q(rw__icontains=query)
        ).order_by('-created_at')
    else:
        daftar_warga = Warga.objects.all().order_by('-created_at')
    return render(request, 'blog/halaman2.html', {'daftar_warga': daftar_warga, 'query': query})

def detail_warga(request, id):
    warga = get_object_or_404(Warga, pk=id)
    return render(request, 'blog/detail_warga.html', {'warga': warga})
