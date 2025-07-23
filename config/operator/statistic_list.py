from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from user.models import User
from django.db.models import Q
from django.core.paginator import Paginator


@login_required(login_url='/login')
@permission_required('admin.operator_statistic_list', login_url="/home")
def operator_statistic_list(request):
    operator = User.objects.filter(type=3)
    if request.GET.get("search", None):
        query = request.GET["search"]
        operator = operator.filter(
            Q(username__contains=query) | Q(first_name__contains=query) | Q(last_name__contains=query) | Q(
                operator_id__contains=query))

    paginator = Paginator(operator, 10)
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    return render(request, 'operator/statistic_list.html',
                  {'page_obj': queryset, 'count': operator.count()})
