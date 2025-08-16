from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
# Create your models here.

class AuthPassword(models.Model):
    password = models.CharField(max_length=100)  # Gunakan field khusus seperti PasswordField di production
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Password Terdaftar"

class Warga(models.Model):
    nama = models.CharField(max_length=100)
    alamat = models.TextField()
    rt = models.CharField(max_length=16)
    rw = models.CharField(max_length=30)
    foto = models.ImageField(upload_to='warga/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama