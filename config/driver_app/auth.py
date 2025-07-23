from random import random, randint

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
# from ...user.models import Token, User
from user.models import Token, User, Regions, Districts
from config.send import send_sms_driver
from django.contrib.auth import authenticate, login

def send_sms_phone(phone, otp_code):
    print(phone, otp_code)
    # send_sms_driver(phone, "Eltuchi bot - birmartalik kod:"+str(otp_code))



def driver_login(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:

                login(request, user)
                messages.success(request, 'Xush kelibsiz')
                return redirect('home')
        else:
            return render(request, 'admin_login/login.html',
                      {"login": request.POST['login'], 'password': request.POST['password'] , 'messages_error':"Login yoki parol not'g'ri"})
    return render(request, 'admin_login/login.html')

def driver_logins(request):
    if request.method == "POST":
        print(request.POST)
        user = User.objects.filter(username=int(request.POST["phone"]), is_active=False).first()
        if user:
            return render(request, "driver_app/auth/wait_active.html", {
                "message": "Sizning ma'lumotlaringiz hali tasdiqlanmadi."})
        token = Token.objects.create(phone=int(request.POST["phone"]), token=randint(111111, 999999))
        request.session['phone'] = token.phone
        send_sms_phone(token.phone, token.token)
        if User.objects.filter(username=str(token.phone)):
            return redirect('check_code')
        else:

            old_user = User.objects.filter(username=request.POST["phone"])
            if old_user:
                messages.error(request, "Bunday raqamli foydalanuvchi mavjud")
            else:
                return redirect('sign_up')
    return render(request, 'driver_app/auth/login.html')


def check_code(request):
    phone = request.session.get('phone', None)
    if phone is not None:
        if request.method == 'POST':
            otp = str(request.POST['token']).find('_')
            if otp == -1:
                last_token = int(Token.objects.filter(phone=int(phone)).last().token)
                if int(request.POST['token']) == last_token:
                    user = User.objects.filter(username=phone).first()
                    login(request, user)
                    return redirect(driver_info)
                else:
                    messages.warning(request, "Kod noto'g'ri")
            else:
                messages.warning(request, "Kodni to'liq kiriting")
        return render(request, 'driver_app/auth/check_code.html', {"p":phone})
    else:
        messages.warning(request, "Oldin sms jo'nating")
        return redirect('driver_app')

def generate_my_unique_cod():
    old_unique_cod = [u.my_unique_code for u in User.objects.all()]
    for r in range(0, 1000):
        new_code = randint(1111111111111111111, 9999999999999999999)
        if new_code in old_unique_cod:
            print('is unique')
        else:
            return new_code


def sign_up(request):
    phone = request.session.get('phone', None)
    if phone is not None:
        if request.method == "POST":
            print(request.POST)
            if int(request.POST['token']) == int(Token.objects.filter(phone=phone).last().token):
                r = request.POST
                user = User.objects.create(username=phone, first_name=r['first_name'],
                                                   last_name=r['last_name'],
                                                   birthday=r['birthday'], password='ii6433278',
                                                   my_unique_code=generate_my_unique_cod(),
                                                   region_id=r["region"], district_id=r['districts'], street=r['street'], is_active=False)
                login(request, user)
                return render(request, "driver_app/auth/wait_active.html", {
                    "message": "Sizning ma'lumotlaringiz hali tasdiqlanmadi."})
            else:
                messages.error(request, "Sms kod noto'g'ri")
                return render(request, 'driver_app/auth/sign_up.html', {"r": Regions.objects.all(), 'd': Districts.objects.all(), 'p': phone, 're':request.POST})
        return render(request, 'driver_app/sign_up.html',{"r": Regions.objects.all(), 'd':  Districts.objects.all(), 'p': phone})
    else:
        messages.warning(request, "Oldin sms jo'nating")
        return redirect('driver_app')



