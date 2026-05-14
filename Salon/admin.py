from django.contrib import admin
from .models import Salon, Service,Portfolio,Inspiration,Stylist,Bookings,WorkingHours,Appointment,Waitlist

# Register your models here.
admin.site.register(Salon)
admin.site.register(Service)
admin.site.register(Portfolio)
admin.site.register(Inspiration)
@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name'
    )

    search_fields = (
        'name',
    )


@admin.register(Bookings)
class BookingsAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'duration',
        'price'
    )

    search_fields = (
        'name',
    )


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'stylist',
        'day',
        'start_time',
        'end_time',
        'is_off_day'
    )

    list_filter = (
        'day',
        'is_off_day'
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'client',
        'stylist',
        'service',
        'date',
        'start_time',
        'end_time',
        'status'
    )

    list_filter = (
        'status',
        'date'
    )

    search_fields = (
        'client__username',
        'stylist__name'
    )


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'client',
        'service',
        'preferred_date',
        'preferred_time'
    )

    list_filter = (
        'preferred_date',
    )

                    
