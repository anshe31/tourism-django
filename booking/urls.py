from django.urls import path, re_path
from booking import views

urlpatterns=[
    # re_path("^$",views.booking_homepage,name="booking_homepage")
    path("order/", views.create_order, name="create_order"),
    path("details/", views.order_details, name="order_details"),
    path("modify/", views.update_order, name="update_order")
   
]