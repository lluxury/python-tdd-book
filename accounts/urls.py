from django.urls import path
from accounts import views

urlpatterns = [
    path('auth/', views.supabase_auth, name='supabase_auth'),
    path('logout/', views.supabase_logout, name='supabase_logout'),
]
