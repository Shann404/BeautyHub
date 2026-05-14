from django.shortcuts import render,get_object_or_404,redirect
from .models import Salon,Service,Portfolio,Inspiration,Profile,Stylist,Bookings,Appointment,Waitlist
from django.db.models import Q
from .ai import find_similar_image
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.contrib import messages
from .utils import generate_available_slots
from django.http import JsonResponse








# Create your views here.
def home(request):
    return render(request, 'index.html')

# def salon_detail(request, id):
#     salon = get_object_or_404(Salon, id=id)

#     return render(request, 'salon_detail.html', {
#         'salon': salon
#     })


def search(request):

    query = request.GET.get('q')

    results = []

    if query:
        results = Salon.objects.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'search_results.html', {
        'query': query,
        'results': results
    })

def salon_detail(request, slug):

    salon = get_object_or_404(Salon, slug=slug)
    services = Service.objects.all()
    portfolio = Portfolio.objects.filter(is_approved=True)


    return render(request, 'salon_detail.html', {
        'salon': salon,
        'services': services,
       'portfolio': portfolio,
    })

# def portfolio_view(request):
#     portfolio = Portfolio.objects.all()
#     return render(request, 'portfolio.html', {'portfolio': portfolio})

def upload_inspiration(request):
    if request.method == "POST":
        image = request.FILES['image']
        note = request.POST['note']

        Inspiration.objects.create(
            user=request.user,
            image=image,
            note=note
        )

    return redirect('portfolio')

@login_required
def upload_portfolio(request):
    if request.method == "POST":
        title = request.POST['title']
        category = request.POST['category']
        image = request.FILES['image']

        Portfolio.objects.create(
            title=title,
            category=category,
            image=image
        )

    
    return redirect('portfolio')

def portfolio_view(request):
    print("Portfolio view accessed")
    salon = Salon.objects.first()
    portfolio = Portfolio.objects.filter(is_approved=True)

    return render(request, 'salon_detail.html', {
        'salon': salon,
        'portfolio': portfolio
    })

def client_portfolio(request):
    return render(request, 'upload_portfolio.html')


def inspiration_view(request):

    inspiration = None

    matched = None

    if request.method == 'POST':

        uploaded_image = request.FILES.get('image')

        inspiration = Inspiration.objects.create(
            image=uploaded_image
        )

        portfolios = Portfolio.objects.filter(is_approved=True)

        matched = find_similar_image(
            inspiration.image.path,
            portfolios
        )

    return render(request, 'index.html', {

        'inspiration': inspiration,

        'matched': matched

    })



def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("upload_portfolio_page")

        return render(request, "login.html", {
            "error": "Invalid credentials"
        })

    return render(request, "login.html")


def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        is_business = request.POST.get("is_business")

        # validation
        if password != confirm_password:
            return render(request, "register.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already exists"
            })

        # create user
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # save profile
        user.profile.is_business = True if is_business else False
        user.profile.save()

        login(request, user)

        return redirect("login")

    return render(request, "register.html")

def book_appointment(request):

    stylists = Stylist.objects.all()

    bookings = Bookings.objects.all()

    if request.method == "POST":

        stylist_id = request.POST.get("stylist")

        service_id = request.POST.get("service")

        date = request.POST.get("date")

        time = request.POST.get("time")

        stylist = get_object_or_404(
            Stylist,
            id=stylist_id
        )

        bookings = get_object_or_404(
            Bookings,
            id=service_id
        )

        appointment_date = datetime.strptime(
            date,
            "%Y-%m-%d"
        ).date()

        start_time = datetime.strptime(
            time,
            "%H:%M"
        ).time()

        start_datetime = datetime.combine(
            appointment_date,
            start_time
        )

        end_datetime = (
            start_datetime +
            bookings.duration +
            bookings.buffer_time
        )

        overlap = Appointment.objects.filter(
            stylist=stylist,
            date=appointment_date,
            start_time__lt=end_datetime.time(),
            end_time__gt=start_time,
            status__in=['pending', 'confirmed']
        ).exists()

        if overlap:

            messages.error(
                request,
                "Time slot unavailable"
            )

            return redirect('book_appointment')

        Appointment.objects.create(
            client=request.user,
            stylist=stylist,
            bookings=bookings,
            date=appointment_date,
            start_time=start_time,
            end_time=end_datetime.time(),
            status='confirmed'
        )

        messages.success(
            request,
            "Appointment booked successfully"
        )

        return redirect('book_appointment')

    return render(request, "book.html", {
        "stylists": stylists,
        "bookings": bookings
    })

def notify_waitlist(service, date):

    users = Waitlist.objects.filter(
        service=service,
        preferred_date=date
    )

    for user in users:

        print(
            f"Notify {user.client.username}"
        )

def get_slots(request):

    stylist_id = request.GET.get("stylist")

    service_id = request.GET.get("service")

    date = request.GET.get("date")

    stylist = Stylist.objects.get(id=stylist_id)

    service = Service.objects.get(id=service_id)

    booking_date = datetime.strptime(
        date,
        "%Y-%m-%d"
    ).date()

    slots = generate_available_slots(
        stylist,
        service,
        booking_date
    )

    formatted_slots = []

    for slot in slots:

        formatted_slots.append(
            slot['start'].strftime("%H:%M")
        )

    return JsonResponse({
        "slots": formatted_slots
    })
