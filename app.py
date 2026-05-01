# admin/app.py
from flask import Flask, redirect, url_for, flash, request
from flask_admin import Admin, AdminIndexView, expose
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import config
from routes.quotas import QuotasView
# from routes.generations import GenerationsView  # ← так будешь подключать новые модули

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
            return redirect(url_for("quotas_view.index"))  # ← дефолтная страница
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

    # 2️⃣ Возвращаем стандартные Peewee-таблицы
    from models import UserSettings, UserPreset, GenerationRequest, StarPayment, AdCampaign, AdImpressionLog, Migration
    from flask_admin.contrib.peewee import ModelView

    class SafeModelView(ModelView):
        def is_accessible(self): return current_user.is_authenticated

        def inaccessible_callback(self, name, **kwargs): return redirect(url_for("admin.login_view"))

    admin.add_view(SafeModelView(UserSettings, name="👤 Пользователи", endpoint="usersettings_view"))
    admin.add_view(SafeModelView(UserPreset, name="⚙️ Пресеты", endpoint="userpreset_view"))
    admin.add_view(SafeModelView(GenerationRequest, name="🔄 Запросы", endpoint="generationrequest_view"))
    admin.add_view(SafeModelView(StarPayment, name="💰 Платежи", endpoint="starpayment_view"))
    admin.add_view(SafeModelView(AdCampaign, name="📢 Реклама", endpoint="adcampaign_view"))
    admin.add_view(SafeModelView(AdImpressionLog, name="📈 Лог показов", endpoint="adimpression_view"))
    admin.add_view(SafeModelView(Migration, name="🔧 Миграции", endpoint="migration_view"))

    return app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5001, debug=True)