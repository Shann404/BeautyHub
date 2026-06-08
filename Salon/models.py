from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from datetime import timedelta



class Salon(models.Model):

    BUSINESS_TYPES = (
        ('salon', 'Salon'),
        ('barber', 'Barbershop'),
        ('spa', 'Spa'),
        ('nails', 'Nail Studio'),
        ('makeup', 'Makeup Artist'),
    )


    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    business_type = models.CharField(
        max_length=20,
        choices=BUSINESS_TYPES
    )

    specialty = models.CharField(max_length=255)
    experience = models.CharField(max_length=100)
    vibe = models.CharField(max_length=100)
    target_audience = models.CharField(max_length=150)

    description = models.TextField()
    about_subtitle = models.CharField(max_length=255, blank=True, default="")

    location = models.CharField(max_length=255)

    phone = models.CharField(max_length=20)

    email = models.EmailField(blank=True, null=True)

    image = models.ImageField(
        upload_to='salons/',
        blank=True,
        null=True
    )

    about_picture = models.ImageField(
        upload_to='salons/about/',
        blank=True,
        null=True
    )

   

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Service(models.Model):

    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name="services",
        blank=True,
        null=True
    )

    service_title = models.CharField(max_length=100)

    service_subtitle = models.CharField(max_length=100)

    service_description = models.TextField()

    service_icon = models.CharField(
        max_length=100,
        default="bi bi-star"
    )

    def __str__(self):
        return self.service_title
    

class Portfolio(models.Model):

    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name="portfolio_items",
        null=True,
        blank=True
    )

    title = models.CharField(max_length=100)

    image = models.ImageField(upload_to='portfolio/')

    category = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Inspiration(models.Model):
    image = models.ImageField(upload_to='inspirations/')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inspiration by {self.user.username}"
    
class InspirationMatch(models.Model):
    inspiration = models.ForeignKey(Inspiration, on_delete=models.CASCADE)
    portfolio_item = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    similarity_score = models.FloatField(default=0.0)  # future AI/manual match

    def __str__(self):
        return "Match"
    



class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    is_business = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.user.username





class Stylist(models.Model):


    name = models.CharField(max_length=200)

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to="stylists/",
        blank=True,
        null=True
    )

    is_available = models.BooleanField(default=True)

    work_start = models.TimeField(default="09:00")

    work_end = models.TimeField(default="18:00")

    def __str__(self):
        return self.name
    
class Style(models.Model):

    stylist = models.ForeignKey(
        Stylist,
        on_delete=models.CASCADE,
        related_name="styles"
    )

    name = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    duration = models.DurationField(
        default=timedelta(hours=1)
    )

    style_image = models.ImageField(
        upload_to="styles/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.name} - {self.stylist.name}"
  


class Booking(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    stylist = models.ForeignKey(
        Stylist,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    style = models.ForeignKey(
        Style,
        on_delete=models.CASCADE,
        related_name="bookings"
    )


    inspo = models.ImageField(
        upload_to="inspo/",
        blank=True,
        null=True
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    duration = models.DurationField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    phone_number = models.CharField(
    max_length=15
)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.customer.username} - "
            f"{self.style.name} - "
            f"{self.date}"
        )


class WorkingHours(models.Model):

    DAYS = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    stylist = models.ForeignKey(
        Stylist,
        on_delete=models.CASCADE
    )

    day = models.IntegerField(choices=DAYS)

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_off_day = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.stylist.name} - {self.get_day_display()}"


class Appointment(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('missed', 'Missed'),
    )

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    stylist = models.ForeignKey(
        Stylist,
        on_delete=models.CASCADE
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.username} - {self.service.name}"


class Waitlist(models.Model):

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )

    preferred_date = models.DateField()

    preferred_time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client.username
    




