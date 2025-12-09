from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

def user_is_employer(function):

    def wrap(request, *args, **kwargs):   

        if request.user.role == 'employer':
            return function(request, *args, **kwargs)
        else:
            messages.error(request, 'This action is only available for employers.')
            return redirect('account:login')

    return wrap



def user_is_employee(function):

    def wrap(request, *args, **kwargs):    

        if request.user.role == 'employee':
            return function(request, *args, **kwargs)
        else:
            messages.error(request, 'This action is only available for employees.')
            return redirect('account:login')

    return wrap