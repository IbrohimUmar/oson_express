from django.contrib import messages
from django.shortcuts import redirect


def is_driver(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_active:
            messages.success(request, "Sizga kirish uchun ruxsat yo'q")
            return redirect('login')
        if request.user.type == '2' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.success(request, "hech biur shartga tushmadu")
        return redirect('home')
    return wrapper