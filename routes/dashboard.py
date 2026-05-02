# routes/dashboard.py
from flask_admin import BaseView, expose
from flask import request, redirect, url_for
from flask_login import current_user
from db.dashboard import get_dashboard_stats

class DashboardView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.login_view"))

    @expose("/")
    def index(self):
        days = request.args.get("days", 30, type=int)
        if days not in [7, 30, 90]:
            days = 30
        stats = get_dashboard_stats(days=days)
        return self.render("admin/dashboard/index.html", stats=stats, selected_days=days)