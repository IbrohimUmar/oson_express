from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import os


@login_required(login_url='/login')
def excel_files_list(request):
    import os

    if request.method == "POST":
        r = request.POST
        if r["action"] == "DELETE":
            excel_file = r["file_name"]
            if os.path.exists(excel_file):
                os.remove(excel_file)
                messages.success(request, "O'chirildi")
                print(f"{excel_file} silindi.")
                return redirect("excel_files_list")
            else:

                messages.success(request, "File topilmadi")
                return redirect("excel_files_list")



    excel_folder = "static/excel/"

    excel_files = [f for f in os.listdir(excel_folder) if f.endswith('.xlsx') or f.endswith('.xls')]
    # excel_files = sorted(excel_files, key=os.path.getctime, reverse=True)
    for file_name in excel_files:
        print(f"Excel dosyası: {file_name}")
    return render(request, 'excel/list.html', {'excel_files': excel_files})
