# routes/user_settings.py
from flask_admin import BaseView, expose
from flask import request, redirect, url_for, flash
from flask_login import current_user

from db.base import get_db_connection
from db.user_settings import (
    get_user_settings, get_user_setting_by_id,
    create_user_setting, update_user_setting, delete_user_setting, get_user_setting_by_user_id
)


class UserSettingsView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.login_view"))

    @expose("/")
    def index(self):
        page = request.args.get("page", 1, type=int)
        search = request.args.get("search", "").strip()
        model_filter = request.args.get("model", "").strip()

        rows, total, total_pages = get_user_settings(
            page=page, search=search, model_filter=model_filter
        )

        # Уникальные модели для фильтра
        with get_db_connection() as conn:
            models = [r[0] for r in conn.execute(
                "SELECT DISTINCT model FROM user_settings WHERE model IS NOT NULL"
            ).fetchall()]

        return self.render("admin/user_settings/list.html",
                           rows=rows, page=page, total_pages=total_pages,
                           filter_search=search, filter_model=model_filter,
                           available_models=models)

    @expose("/add", methods=["GET", "POST"])
    def add(self):
        if request.method == "POST":
            try:
                data = {
                    'user_id': request.form.get('user_id', type=int),
                    'username': request.form.get('username', '').strip(),
                    'model': request.form.get('model'),
                    'preset': request.form.get('preset'),
                    'requests_count': request.form.get('requests_count', 0, type=int),
                    'last_request_at': request.form.get('last_request_at') or None,
                    'vae': request.form.get('vae'),
                    'lora_string': request.form.get('lora_string')
                }
                if not data['user_id']:
                    raise ValueError("⚠️ User ID обязателен")

                # Проверка на дубликат
                existing = get_user_setting_by_user_id(data['user_id'])
                if existing:
                    raise ValueError(f"⚠️ Пользователь {data['user_id']} уже есть в базе")

                create_user_setting(data)
                flash("✅ Пользователь добавлен", "success")
                return redirect(url_for(".index"))

            except Exception as e:
                flash(str(e), "danger")

        return self.render("admin/user_settings/form.html", action="add", record=None)

    @expose("/edit/<int:setting_id>", methods=["GET", "POST"])
    def edit(self, setting_id):
        record = get_user_setting_by_id(setting_id)
        if not record:
            flash("⚠️ Запись не найдена", "warning")
            return redirect(url_for(".index"))

        if request.method == "POST":
            try:
                data = {
                    'username': request.form.get('username', '').strip(),
                    'model': request.form.get('model'),
                    'preset': request.form.get('preset'),
                    'requests_count': request.form.get('requests_count', 0, type=int),
                    'last_request_at': request.form.get('last_request_at') or None,
                    'vae': request.form.get('vae'),
                    'lora_string': request.form.get('lora_string')
                }
                update_user_setting(setting_id, data)
                flash("✅ Изменения сохранены", "success")
                return redirect(url_for(".index"))
            except Exception as e:
                flash(f"⚠️ {e}", "danger")

        return self.render("admin/user_settings/form.html", action="edit", record=record)

    @expose("/delete/<int:setting_id>", methods=["POST"])
    def delete(self, setting_id):
        try:
            delete_user_setting(setting_id)
            flash("🗑️ Запись удалена", "success")
        except Exception as e:
            flash(f"⚠️ Ошибка: {e}", "danger")
        return redirect(url_for(".index"))