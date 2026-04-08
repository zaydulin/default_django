# admin_site.py
from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)

        # Оставляем только auth.user
        filtered = []
        for app in app_list:
            models = [
                m for m in app["models"]
                if m["object_name"].lower() == "user"
            ]
            if models:
                app["models"] = models
                filtered.append(app)

        return filtered