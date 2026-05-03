# admin/app.py
from flask import Flask, redirect, url_for, flash, request
from flask_admin import Admin, AdminIndexView, expose
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import config
from routes.quotas import QuotasView
from routes.system_monitor import SystemMonitorView
from routes.user_settings import UserSettingsView
from views import GenerationRequestView, UserPresetView, StarPaymentView
from views import (
     UserPresetView, StarPaymentView,
    GenerationRequestView,
    AdCampaignView, AdImpressionLogView, MigrationView)
from routes.dashboard import DashboardView


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.ADMIN_SECRET

    # 🔐 Auth
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "admin.login_view"

    class AdminUser(UserMixin):
        def __init__(self, username): self.id = username
    @login_manager.user_loader
    def load_user(user_id): return AdminUser(user_id) if user_id == config.ADMIN_USER else None

    # 🎛️ Admin
    class MyAdminIndexView(AdminIndexView):
        @expose("/")
        def index(self):
            if not current_user.is_authenticated: return redirect(url_for(".login_view"))
            return redirect(url_for("dashboard_view.index"))  # ← дефолтная страница
        @expose("/login/", methods=["GET", "POST"])
        def login_view(self):
            if request.method == "POST":
                if request.form.get("username") == config.ADMIN_USER and request.form.get("password") == config.ADMIN_PASS:
                    login_user(AdminUser(request.form["username"]))
                    return redirect(url_for(".index"))
                flash("Неверный логин или пароль", "error")
            return self.render("admin/login.html")
        @expose("/logout/")
        def logout_view(self):
            logout_user()
            return redirect(url_for(".login_view"))

    admin = Admin(app, name="🎨 AnimeGen Admin", index_view=MyAdminIndexView(), template_mode="bootstrap4")

    # 1️⃣ Кастомный модуль (Raw SQL)
    admin.add_view(QuotasView(name="📊 Квоты", endpoint="quotas_view"))
    admin.add_view(UserSettingsView(name="👥 Пользователи", endpoint="usersettings_custom"))

    # 2️⃣ Возвращаем стандартные Peewee-таблицы
    from models import UserSettings, UserPreset, GenerationRequest, StarPayment, AdCampaign, AdImpressionLog, Migration
    from flask_admin.contrib.peewee import ModelView

    class SafeModelView(ModelView):
        def is_accessible(self): return current_user.is_authenticated

        def inaccessible_callback(self, name, **kwargs): return redirect(url_for("admin.login_view"))

    admin.add_view(AdCampaignView(AdCampaign, name="📢 Реклама", endpoint="adcampaign_view"))
    admin.add_view(AdImpressionLogView(AdImpressionLog, name="📋 Лог показов", endpoint="adimpression_view"))
    admin.add_view(StarPaymentView(StarPayment, name="💰 Платежи", endpoint="payment_view"))
    # 🎨 Пресеты
    admin.add_view(UserPresetView(UserPreset, name="🎨 Пресеты", endpoint="userpreset_view"))
    # 📈 Запросы
    admin.add_view(GenerationRequestView(GenerationRequest, name="📈 Запросы", endpoint="generation_view"))
    # 👥 Пользователи (стандартная вьюха, если нужна)
    #admin.add_view(UserSettingsView(UserSettings, name="👥 Пользователи (станд.)", endpoint="usersettings_std"))
    # 🗂️ Миграции
    admin.add_view(MigrationView(Migration, name="🗂️ Миграции", endpoint="migration_view"))
    admin.add_view(DashboardView(name="🌌 Дашборд", endpoint="dashboard_view"))
    admin.add_view(SystemMonitorView(name="🖥️ Мониторинг", endpoint="system_monitor"))

    return app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5001, debug=True)