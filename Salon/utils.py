from datetime import datetime, timedelta

from .models import (
    Appointment,
    WorkingHours
)


def generate_available_slots(
    stylist,
    service,
    date
):

    weekday = date.weekday()

    try:
        working_hours = WorkingHours.objects.get(
            stylist=stylist,
            day=weekday
        )

        if working_hours.is_off_day:
            return []

    except WorkingHours.DoesNotExist:
        return []

    slots = []

    service_duration = (
        service.duration +
        service.buffer_time
    )

    current_time = datetime.combine(
        date,
        working_hours.start_time
    )

    end_day_time = datetime.combine(
        date,
        working_hours.end_time
    )

    appointments = Appointment.objects.filter(
        stylist=stylist,
        date=date,
        status__in=['pending', 'confirmed']
    )

    while current_time + service_duration <= end_day_time:

        slot_end = current_time + service_duration

        overlapping = appointments.filter(
            start_time__lt=slot_end.time(),
            end_time__gt=current_time.time()
        ).exists()

        if not overlapping:

            slots.append({
                'start': current_time.time(),
                'end': slot_end.time()
            })

        current_time += timedelta(minutes=30)

    return slots