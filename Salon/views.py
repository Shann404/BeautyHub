from django.shortcuts import render,get_object_or_404,redirect
from .models import Salon,Portfolio,Inspiration,Profile,Booking,Style,Stylist,Appointment,Waitlist,Service
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

    services = salon.services.all()
    print(services)

    portfolio = salon.portfolio_items.filter(
        is_approved=True
    )

    return render(request, "salon_detail.html", {
        "salon": salon,
        "services": services,
        "portfolio": portfolio,
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

    salon = get_object_or_404(
        Salon,
        owner=request.user
    )

    Portfolio.objects.create(
        salon=salon,
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

@login_required
def book_appointment(request):

    stylists = Stylist.objects.filter(
        is_available=True
    )

    styles = Style.objects.filter(
        is_active=True
    )

    if request.method == "POST":

        stylist_id = request.POST.get("stylist")

        style_id = request.POST.get("style")

        phone_number = request.POST.get("phone")

        date = request.POST.get("date")

        start_time = request.POST.get("time")

        if not start_time:
            return render(request, "book.html", {
                "stylists": stylists,
                "styles": styles,
                "error": "Please select a time slot"
            })

        inspo = request.FILES.get("inspo")

        if not stylist_id or not style_id:

            context = {
                "stylists": stylists,
                "styles": styles,
                "error": "Please select both stylist and style"
            }

            return render(
                request,
                "book.html",
                context
            )

        stylist = Stylist.objects.get(
            id=int(stylist_id)
        )

        style = Style.objects.get(
            id=int(style_id)
        )

            # -----------------------------
            # Convert selected start time
            # -----------------------------

        start_datetime = datetime.strptime(
            start_time,
            "%I:%M %p"
        )

        duration = style.duration

        end_datetime = (
            start_datetime + duration
        )

        # -----------------------------
        # Create booking
        # -----------------------------

        existing_booking = Booking.objects.filter(

    stylist=stylist,

    date=date,

    start_time=start_datetime.time(),

        ).exclude(
            status="cancelled"
        ).exists()

        if existing_booking:

            context = {
                "stylists": stylists,
                "styles": styles,
                "error": "This time slot is already booked."
            }

            return render(
                request,
                "book.html",
                context
            )

        Booking.objects.create(

            customer=request.user,

            stylist=stylist,

            style=style,

            inspo=inspo,

            phone_number=phone_number,

            date=date,

            start_time=start_datetime.time(),

            end_time=end_datetime.time(),

            duration=duration,

            price=style.price
        )

        return redirect("success_page")

    context = {

        "stylists": stylists,

        "styles": styles
    }

    return render(
        request,
        "book.html",
        context
    )

def get_style_details(request):

    style_id = request.GET.get("style")

    style = Style.objects.get(
        id=style_id
    )

    duration_hours = (
        style.duration.total_seconds() / 3600
    )

    return JsonResponse({

        "price": str(style.price),

        "duration": f"{duration_hours:.0f} Hours"
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

    style_id = request.GET.get("style")

    selected_date = request.GET.get("date")

    stylist = Stylist.objects.get(
        id=stylist_id
    )

    style = Style.objects.get(
        id=style_id
    )

    duration = style.duration

    # -----------------------------------
    # Stylist working hours
    # -----------------------------------

    work_start = datetime.combine(
        datetime.today(),
        stylist.work_start
    )

    work_end = datetime.combine(
        datetime.today(),
        stylist.work_end
    )

    # -----------------------------------
    # Existing bookings
    # -----------------------------------

    existing_bookings = Booking.objects.filter(
        stylist=stylist,
        date=selected_date
    )

    slots = []

    current_slot = work_start

    while current_slot + duration <= work_end:

        proposed_start = current_slot

        proposed_end = (
            current_slot + duration
        )

        overlap = False

        # -----------------------------------
        # Prevent overlaps
        # -----------------------------------

        for booking in existing_bookings:

            existing_start = datetime.combine(
                datetime.today(),
                booking.start_time
            )

            existing_end = datetime.combine(
                datetime.today(),
                booking.end_time
            )

            if (
                proposed_start < existing_end
                and
                proposed_end > existing_start
            ):

                overlap = True

                break

        if not overlap:

            slots.append(
                current_slot.strftime(
                    "%I:%M %p"
                )
            )

        # -----------------------------------
        # Move to next slot
        # -----------------------------------

        current_slot += timedelta(
            minutes=30
        )

    return JsonResponse({

        "slots": slots
    })

def success_page(request):
    return render(request, "success.html")

@login_required
def booking_list(request):

    bookings = Booking.objects.select_related(
        "customer",
        "stylist",
        "style"
    ).order_by("-created_at")

    context = {
        "bookings": bookings
    }

    return render(
        request,
        "booking_list.html",
        context
    )
    