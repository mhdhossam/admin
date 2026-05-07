"""
Root URL configuration.
All API routes are versioned under /api/v1/.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import AdminTokenObtainPairView, AdminTokenVerifyView, AdminLogoutView
 
urlpatterns = [
    # Django native admin (kept as fallback/superuser tool)
    path("django-admin/", admin.site.urls),
 
    # ── Auth endpoints ─────────────────────────────────────────────────────
    path("api/auth/login/",   AdminTokenObtainPairView.as_view(),  name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(),          name="token_refresh"),
    path("api/auth/verify/",  AdminTokenVerifyView.as_view(),       name="token_verify"),
    path("api/auth/logout/",  AdminLogoutView.as_view(),            name="token_logout"),
 
    # ── Resource APIs ──────────────────────────────────────────────────────
    path("api/", include("apps.products.urls")),
    path("api/", include("apps.users.urls")),
 
    # ── Schema registry API ────────────────────────────────────────────────
    path("api/schema/", include("apps.schema.urls")),
]

# from django.contrib import admin
# from django.urls import path, include
# urlpatterns = [
#   path("django-admin/", admin.site.urls),
#   ]