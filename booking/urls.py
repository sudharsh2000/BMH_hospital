from booking.views import DepartmentView, DoctorViewset, TakeAppoinmentViewSet, PrescriptionViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include
router=DefaultRouter()
router.register('doctor',DoctorViewset,basename='doctor')
router.register('take-appoinment',TakeAppoinmentViewSet,basename='take-appinment')
router.register('prescription',PrescriptionViewSet,basename='prescription')
urlpatterns=[
    path('departments/',DepartmentView.as_view(),name='departments'),
    path('api/',include(router.urls)),

    
]