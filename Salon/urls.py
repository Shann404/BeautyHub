from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
path('',views.home, name='home'),
    # path('salon/<int:id>/', views.salon_detail, name='salon_detail'),
path('search/', views.search, name='search'),
path('salon/<slug:slug>/',views.salon_detail,name='salon_detail'),
path('upload_portfolio/', views.client_portfolio, name="upload_portfolio_page"),
path('portfolio/upload/', views.upload_portfolio, name='upload_portfolio'),
path('portfolio/', views.portfolio_view, name='portfolio'),
# path('upload_inspiration/', views.upload_inspiration, name='inspiration'),
path('inspiration/', views.inspiration_view, name='inspiration'),
path('login/', views.login_view, name='login'),
path('register/', views.register_view, name='register'),
path('book/',views.book_appointment,name='book_appointments'),
path('get-slots/',views.get_slots,name='get_slots'),
path("",views.book_appointment,name="book_appointment"),
path("get-slots/",views.get_slots,name="get_slots"),
path("get-style-details/",views.get_style_details,name="get_style_details"),
path("success/", views.success_page, name="success_page"),
path("bookings/",views.booking_list,name="booking_list"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)