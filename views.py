# admin/views.py
from flask_admin.contrib.peewee import ModelView
from flask import redirect, url_for
from flask_login import current_user


class BaseSafeModelView(ModelView):
    """Базовый класс с авторизацией — наследуем все от него"""

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.login_view"))

    # 🎨 Общие настройки
    column_display_pk = True
    page_size = 20
    can_view_details = True

    # 🕒 Форматирование дат
    column_formatters = {
        'created_at': lambda v, c, m, n: m.created_at.strftime('%Y-%m-%d %H:%M') if m.created_at else '—',
        'updated_at': lambda v, c, m, n: m.updated_at.strftime('%Y-%m-%d %H:%M') if m.updated_at else '—',
        'last_request_at': lambda v, c, m, n: m.last_request_at.strftime(
            '%Y-%m-%d %H:%M') if m.last_request_at else '—',
        'shown_at': lambda v, c, m, n: m.shown_at.strftime('%Y-%m-%d %H:%M') if m.shown_at else '—',
    }

    column_labels = {
        'created_at': 'Создан',
        'updated_at': 'Обновлён',
        'user_id': 'User ID',
        'payment_id': 'ID платежа',
    }


# 👥 Пользователи (user_settings) — для кастомной вьюхи (со статистикой)
# (этот класс для стандартной Peewee-вьюхи, если нужна)
class UserSettingsView(BaseSafeModelView):
    column_searchable_list = ['username']  # ✅ только текст
    column_filters = ['user_id', 'model', 'preset', 'requests_count', 'created_at']
    column_list = ['id', 'user_id', 'username', 'model', 'preset', 'requests_count', 'created_at']
    column_default_sort = ('id', True)


# 🎨 Пресеты (user_preset)
class UserPresetView(BaseSafeModelView):
    column_searchable_list = ['name', 'preset_key']  # ✅ TEXT/VARCHAR
    column_filters = ['user_id', 'is_safe_for_business', 'is_premium', 'created_at']
    column_list = ['id', 'name', 'preset_key', 'user_id', 'width', 'height', 'steps', 'is_premium', 'created_at']
    column_default_sort = ('created_at', True)


# 💰 Платежи (star_payments) — ИСПРАВЛЕНО!
class StarPaymentView(BaseSafeModelView):
    column_searchable_list = ['payment_id']  # ✅ TEXT, было transaction_id — ошибка!
    column_filters = ['user_id', 'stars_amount', 'credits_granted', 'currency', 'created_at']
    column_list = ['id', 'user_id', 'payment_id', 'stars_amount', 'credits_granted', 'currency', 'created_at']
    column_default_sort = ('created_at', True)

    # 🔒 Запрет редактирования (платежи — только просмотр)
    can_create = False
    can_edit = False
    can_delete = False


# 📈 Запросы генерации (generation_requests)
class GenerationRequestView(BaseSafeModelView):
    column_searchable_list = ['user', 'prompt']  # ✅ user — VARCHAR(20), prompt — TEXT
    column_filters = ['user', 'model_used', 'preset_used', 'status', 'created_at']
    column_list = ['id', 'user', 'model_used', 'prompt', 'preset_used', 'status', 'generation_time_sec', 'created_at']
    column_default_sort = ('created_at', True)

    can_create = False
    can_edit = False
    # can_delete = True  # если нужно чистить логи


# 📊 Квоты (user_quota) — если переведёшь на Peewee модель
class UserQuotaView(BaseSafeModelView):
    column_searchable_list = []  # user_id — BIGINT, нельзя искать
    column_filters = ['user_id', 'is_banned', 'is_unlimited', 'paid_credits', 'free_limit']
    column_list = ['id', 'user_id', 'paid_credits', 'paid_used', 'free_used', 'free_limit', 'is_banned', 'is_unlimited']
    column_default_sort = ('id', True)


# 📢 Рекламные кампании (ad_campaigns) — 🔥 НОВОЕ!
class AdCampaignView(BaseSafeModelView):
    column_searchable_list = ['title', 'content', 'target_link', 'btn_text']  # ✅ все TEXT
    column_filters = ['ad_type', 'is_active', 'remaining', 'created_at']

    column_list = [
        'id', 'title', 'ad_type', 'remaining', 'total_sold',
        'shown_count', 'is_active', 'created_at'
    ]
    column_default_sort = ('created_at', True)

    # 🎨 Форматирование: показывать прогресс показов
    column_formatters = {
        **BaseSafeModelView.column_formatters,
        'remaining': lambda v, c, m, n: f'🟢 {m.remaining}' if m.remaining > 10 else
        f'🟡 {m.remaining}' if m.remaining > 0 else '🔴 0',
        'is_active': lambda v, c, m, n: '✅' if m.is_active else '❌',
        'content': lambda v, c, m, n: (m.content[:50] + '...') if m.content and len(m.content) > 50 else m.content,
    }

    # 🛠️ Форма создания/редактирования
    form_columns = [
        'title', 'ad_type', 'content', 'target_link', 'btn_text',
        'remaining', 'total_sold', 'is_active'
    ]

    form_args = {
        'ad_type': {
            'choices': [
                ('photo', '🖼️ Фото (прямая ссылка на картинку)'),
                ('text', '📝 Текст (обычное сообщение)')
            ],
            'description': 'Для фото бот покажет изображение с кнопкой. Для текста — только сообщение.'
        },
        'content': {
            'render_kw': {'rows': 3, 'placeholder': 'https://... или текст объявления'}
        }
    }

    form_widget_args = {
        'content': {'rows': 4, 'placeholder': 'Ссылка на изображение (для photo) или текст объявления'},
        'target_link': {'placeholder': 'https://t.me/... или https://ozon.ru/...'},
        'btn_text': {'placeholder': '🛍️ Перейти'},
    }


# 📋 Лог показов рекламы (ad_impressions_log) — только просмотр
class AdImpressionLogView(BaseSafeModelView):
    column_searchable_list = []

    # ✅ Только безопасные типы для фильтров
    column_filters = ['shown_at']

    column_list = ['id', 'ad_id', 'generation_id', 'shown_at']
    column_default_sort = ('shown_at', True)

    can_create = False
    can_edit = False
    can_delete = True

    column_labels = {
        'ad_id': 'Кампания',
        'generation_id': 'Запрос',
        'shown_at': 'Показан',
    }


# 🗂️ Миграции (_migrations) — только просмотр
class MigrationView(BaseSafeModelView):
    can_create = False
    can_edit = False
    can_delete = False

    column_list = ['version', 'applied_at']
    column_default_sort = ('applied_at', True)