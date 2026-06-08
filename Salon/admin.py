from django.contrib import admin
from .models import Salon, Service,Booking,Portfolio,Inspiration,Style,Stylist,WorkingHours,Appointment,Waitlist

# Register your models here.
admin.site.register(Salon)
admin.site.register(Service)
admin.site.register(Portfolio)
admin.site.register(Inspiration)
@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "phone",
        "is_available",
        "work_start",
        "work_end"
    )

    list_filter = (
        "is_available",
    )

    search_fields = (
        "name",
        "phone"
    )


@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "stylist",
        "price",
        "duration",
        "is_active",
        "created_at"
    )

    list_filter = (
        "is_active",
        "stylist"
    )

    search_fields = (
        "name",
        "stylist__name"
    )

    list_editable = (
        "price",
        "is_active"
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "stylist",
        "style",
        "date",
        "start_time",
        "end_time",
        "price",
        "status",
        "created_at"
    )

    list_filter = (
        "status",
        "date",
        "stylist"
    )

    search_fields = (
        "customer__username",
        "stylist__name",
        "style__name"
    )

    readonly_fields = (
        "created_at",
    )

    list_editable = (
        "status",
    )

    date_hierarchy = "date"



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

                    
