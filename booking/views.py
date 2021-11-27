from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from booking.models import Order, Package
from .forms import OrderForm
from .serializers import OrderSerializer
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.

def booking_homepage(request):
    return render(request,'index.html', context={})
    # return HttpResponse("Hello, world. You're at the index.")

@login_required()
def create_order(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = OrderForm(request.POST)
        # print(request.POST)
        
        if form.is_valid():
            order_obj = form.save(commit=False)

            # Add User field
            order_obj.user = request.user

            # Add order_price field by calculating total amount
            # package_obj = order_obj.package
            # order_obj.order_price = order_obj.no_of_people * package_obj.baseprice
            
            order_obj.order_price = calculate_price(order_obj.no_of_people,order_obj.package.baseprice)

            order_obj.save()
            order_id = order_obj.id
            messages.success(request, 'Order Successfully created! Order ID = {}'.format(order_id))
            return render(request, "index.html", {})
        else:
 
            messages.error(request, form.errors)
            return render(request, "index.html", {})

    else:
        form = OrderForm()
        return render(request,'create-order.html', {'form': form})
    

@login_required()
def order_details(request):
    if request.method == 'GET' and request.GET:
        order_id = request.GET.get('order_id')
        order_obj = get_order_object(order_id)
        
        if order_obj is None:
            messages.error(request, 'Invalid Order ID. Please check again!')
            return render(request, "index.html", {})
                  
        # Users can only view their orders 
        if validate_user_order(request,order_obj) == False:
            messages.error(request, 'Invalid Order ID. Users can only view their ORDERS!')
            return render(request, "index.html", {})
        
      
        context={
            "order":order_obj
        }
        return render(request, "order-details-result.html", context)

                
        
    else:
        return render(request, "order-details-view.html", {"operation":"Fetch"})

@login_required()
def update_order(request):
    print("in update")

    if request.method == "GET" and request.GET:
        order_id = request.GET.get('order_id', None)
        if order_id is None:
            messages.error(request, 'Order Id passed is None. Please submit Order id through form.')
            return render(request, "index.html", {})
        # print(order_id)
        order_obj = get_order_object(order_id)
        if order_obj is None:
            messages.error(request, 'Invalid Order ID. Kindly submit correct Order Id.')
            return render(request, "index.html", {})
        
    
        # Users can only view their orders 
        if validate_user_order(request,order_obj) == False:
            messages.error(request, 'Invalid Order ID. Users can only view their ORDERS!')
            return render(request, "index.html", {})

        data = {'package':order_obj.package,'no_of_people':order_obj.no_of_people,
                'travel_date' : order_obj.travel_date
                }
        print(data)
        form = OrderForm(data)
        print("is bound ",form.is_bound)
        # form.fields['Order'].queryset = Order.objects.filter(id=order_id)
        # form.fields['user'].widget = form.HiddenInput()
        # context = 
        return render(request,"order-modify.html",{"form":form})
       
            
     
            
    elif request.method == "POST":
        order_id = request.GET.get('order_id', None)
        order_obj = get_order_object(order_id)
        
        if order_obj is None:
            messages.error(request, 'Invalid Order ID. Kindly submit correct Order Id.')
            return render(request, "index.html", {})
        
        # Users can only view their orders 
        if validate_user_order(request,order_obj) == False:
            messages.error(request, 'Invalid Order ID. Users can only view their ORDERS!')
            return render(request, "index.html", {})

        form = OrderForm(data = request.POST or None, instance=order_obj)

        if form.is_valid():
            
            order_obj = form.save(commit=False)
            order_obj.user = request.user

            order_obj.order_price = calculate_price(order_obj.no_of_people,order_obj.package.baseprice)

            order_obj.save()
            messages.success(request, 'Order Successfully Updated! Order ID = {}'.format(order_obj.id))
            return render(request, "index.html", {})
    else:
        return render (request,"order-details-view.html", {"operation":"Update"})


def calculate_price(no_of_people,baseprice):
    
    # Add order_price field by calculating total amount
    return no_of_people * baseprice

def get_order_object(orderid):
    
    # Add order_price field by calculating total amount
    try:
        order_obj = Order.objects.get(id=orderid)
    except ObjectDoesNotExist:
        order_obj = None
    return order_obj

def validate_user_order(request,order_obj):
    return request.user.id == order_obj.user.id