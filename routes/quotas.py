from flask_admin import BaseView, expose
from flask import request, redirect, url_for, flash
from flask_login import current_user
from db.quotas import get_quotas, get_quota_by_id, create_quota, update_quota, delete_quota

class QuotasView(BaseView):
    def is_accessible(self): return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs): return redirect(url_for("admin.login_view"))

    @expose("/")
    def index(self):
        page = request.args.get("page", 1, type=int)
        search = request.args.get("username", "").strip()
        banned_str = request.args.get("banned")
        banned = int(banned_str) if banned_str in ("0", "1") else None
        rows, _, total_pages = get_quotas(page=page, search=search, banned=banned)
        return self.render("admin/quotas/list.html", rows=rows, page=page, total_pages=total_pages,
                           filter_banned=banned_str, filter_username=search)

    @expose("/add", methods=["GET", "POST"])
    def add(self):
        if request.method == "POST":
            try:
                data = {k: request.form.get(k, 0) for k in ['user_id','is_unlimited','is_banned','free_used','free_limit','paid_credits','paid_used']}
                if not data['user_id']: raise ValueError("User ID обязателен")
                create_quota(data)
                flash("✅ Квота добавлена", "success")
                return redirect(url_for(".index"))
            except Exception as e: flash(f"❌ {e}", "danger")
        return self.render("admin/quotas/form.html", action="add", record=None)

    @expose("/edit/<int:quota_id>", methods=["GET", "POST"])
    def edit(self, quota_id):
        record = get_quota_by_id(quota_id)
        if not record: flash("❌ Не найдено", "danger"); return redirect(url_for(".index"))
        if request.method == "POST":
            try:
                data = {k: request.form.get(k, 0) for k in ['user_id','is_unlimited','is_banned','free_used','free_limit','paid_credits','paid_used']}
                if not data['user_id']: raise ValueError("User ID обязателен")
                update_quota(quota_id, data)
                flash("✅ Обновлено", "success")
                return redirect(url_for(".index"))
            except Exception as e: flash(f"❌ {e}", "danger")
        return self.render("admin/quotas/form.html", action="edit", record=record)

    @expose("/delete/<int:quota_id>", methods=["POST"])
    def delete(self, quota_id):
        try: delete_quota(quota_id); flash("✅ Удалено", "success")
        except Exception as e: flash(f"❌ {e}", "danger")
        return redirect(url_for(".index"))