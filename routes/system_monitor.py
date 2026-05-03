# routes/system_monitor.py
from flask_admin import BaseView, expose
from flask import jsonify
from flask_login import current_user
from utils.system_metrics import get_system_metrics


class SystemMonitorView(BaseView):
    """Страница мониторинга системы (CPU/RAM/GPU)"""

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        from flask import redirect, url_for
        return redirect(url_for("admin.login_view"))

    @expose("/")
    def index(self):
        """Рендер страницы мониторинга"""
        return self.render("admin/system_monitor/index.html")

    @expose("/api/metrics")
    def api_metrics(self):
        """JSON-эндпоинт для автообновления метрик"""
        return jsonify(get_system_metrics())