from django.urls import path
from .views import FormApiView , Formcreate
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Your existing URL patterns
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/forms/create/', Formcreate.as_view(), name='form-create'),
    path('forms/<str:username>/<int:pk>/', FormApiView.as_view(), name='form-api-view'),
]