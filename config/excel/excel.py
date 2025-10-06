from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import os

from user.models import ExportedFile


@login_required(login_url='/login')
def excel_files_list(request):
    import os
    if request.method == "POST":
        r = request.POST
        if r["action"] == "DELETE":
            file = ExportedFile.objects.filter(id=r['file_id'], user=request.user).first()
            if not file:
                messages.success(request, "File topilmadi")
                return redirect("excel_files_list")
            file.delete()
            messages.success(request, "Fayl o'chirildi")
            return redirect("excel_files_list")
    files = ExportedFile.objects.filter(user=request.user)
    if request.user.type == '6':
        return render(request, 'seller_app/excel/list.html', {'files': files})
    else:
        return render(request, 'excel/list.html', {'files': files})
