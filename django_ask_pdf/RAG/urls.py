from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:file_id>', views.chatbot, name='chatbot'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('chat', views.chat, name='chat'),
    path('pdf/<str:filename>/', views.pdf_view, name='pdf_view'),
    path('upload', views.upload_file, name='upload_file'),
    path('delete/<int:file_id>', views.delete, name='delete'),
]

# # This part allows Django to serve media files during development.
# from django.conf import settings
# from django.conf.urls.static import static

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)