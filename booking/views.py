from functools import partial
from re import T
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, response
import rest_framework

from booking.models import Order, Package
from .forms import OrderForm
from .serializers import OrderSerializer,PackageSerializer
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework.response import Response
from rest_framework.views import APIView

from booking import serializers
from django.contrib.auth.models import User
from django.db import connection

import sqlite3,json
import concurrent.futures
from threading import Lock
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

class api_order(APIView):
    print("in API view class")
    def get(self,request,pk=None):
        if pk:
            print(pk)
            order_obj = Order.objects.filter(id=pk)
        else:
            order_obj = Order.objects.all()
        serializer = OrderSerializer(order_obj,many=True)
        return Response({"order":serializer.data})

    def post(self,request):
        order = request.data.get('order')
        
        # lets create new order from provided data
        serializer = OrderSerializer(data=order)
        print(serializer)
        if serializer.is_valid(raise_exception=True):
            order_saved= serializer.save()
            print('order_saved ',order_saved.id)
            context =  {"success": "Order '{}' created successfully.".format(order_saved.id)}
        return Response(context)

    def put(self,request,pk):
        
        saved_order = get_object_or_404(Order.objects.all(),pk=pk)
        print(saved_order)
        data = request.data.get('order')
        print(data.get('user_email'),data.get('package'))
        
        user_obj = User.objects.get(email = data.get('user_email'))
        print(user_obj)
        
        package_obj = Package.objects.get(package_name=data.get('package'))
        print(package_obj.baseprice)
        
        saved_order.order_price = calculate_price(saved_order.no_of_people,package_obj.baseprice)
        saved_order.no_of_people = data.get('no_of_people')
        saved_order.travel_date = data.get('travel_date')
        saved_order.package = package_obj
        saved_order.user = user_obj
        
        saved_order.save()
        context =  {"success": "Order '{}' updated successfully.".format(saved_order.id)}
        return Response(context)
        
    def delete(self,request,pk):
        print(pk)
        order_obj = get_object_or_404(Order.objects.all(),pk=pk)
        order_obj.delete()
        context =  {"success": "Order '{}' deleted successfully.".format(pk)}
        return Response(context)


# API using RAW/Custom queries
class raw_api_order(APIView):
    print("in Raw API view class")
    def get(self,request,pk=None):
        if pk:
            print(pk)
            # order_obj = Order.objects.filter(id=pk)
            order_obj = Order.objects.raw('SELECT * FROM booking_order where id = %s',[pk])  
        else:
            order_obj = Order.objects.raw('SELECT * FROM booking_order')
    
        serializer = OrderSerializer(order_obj,many=True)
        return Response({"order":serializer.data})
 
 
class Database():
    
    def singleQuery(self,query,params,indicator,output=False):
        print("single query"+query,params,indicator,output)
     
        with connection.cursor() as cursor:
            # print("cursor started ",query)
            cursor.execute(query)
            # print("executed")
            if output:
                row = cursor.fetchall()
                # print(row, indicator)
                return self.formJson(row,indicator)
    def formJson(self,resultSet,indicator):

        recData = []
        for rec in resultSet:
            # print(rec,indicator)
            if indicator == "orderData":
                recData.append({"Order_price":rec[0]})
            if indicator == "packageData":
                recData.append({"Package_name":rec[0]})
            if indicator == "userData":
                recData.append({"User_name":rec[0]})
            
        print("json is here\n",recData)
        return recData
                
        
        
           

# API using RAW/Custom queries in parallel
def parallel_api_order(request):
    if request.method == 'GET':
        print("in get")

        input = [
                {"query": """SELECT order_price FROM booking_order""",
                 "parameters":[],
                 "indicator" : "orderData"
                 }
                ,
                 {"query": """SELECT package_name FROM booking_package""",
                 "parameters":[],
                 "indicator" : "packageData"
                 },
                 {"query": """SELECT username FROM auth_user as USER""",
                 "parameters":[],
                 "indicator" : "userData"
                 }
                ]

        db = Database()
        
        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Start the load operations and mark each future with its URL
            futures = []
            # for query in queries:
            for i in input:
                futures.append(executor.submit(db.singleQuery, i["query"],None,i["indicator"],True))
            
            op = []             
            for future in concurrent.futures.as_completed(futures):
                try:
                    print("in future result")
                    # print(future)
                    data = future.result()
                    print(data)
                    op.append(data)
                except Exception as exc:
                    print('generated an exception: %s' % (exc))
            
            # print(op)
            # print(json.dumps(op, indent=4))
            jsonData = json.dumps({"ViewDetails":op} )
            print("FINAL OP")
            print(jsonData)
            return HttpResponse(jsonData)
      
        