# admin/models.py
from peewee import *
from datetime import datetime
import os
import config

# Путь к БД — относительный от папки admin/


db = SqliteDatabase(
    str(config.DB_PATH),
    pragmas={
        'journal_mode': 'wal',      # WAL-режим для лучшей параллельности
        'busy_timeout': 10000,      # Ждать блокировку до 10 секунд
        'synchronous': 'NORMAL',
    }
)

class BaseModel(Model):
    class Meta:
        database = db
        legacy_table_names = False  # чтобы имена таблиц совпадали точно

# === Твои таблицы (точно как в схеме) ===

class Migration(BaseModel):
    version = CharField(primary_key=True)
    applied_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = '_migrations'

class UserSettings(BaseModel):
    id = AutoField()
    user_id = BigIntegerField(unique=True, index=True)
    username = CharField(max_length=100, null=True)
    model = TextField(null=True)
    preset = CharField(max_length=50, null=True)
    requests_count = IntegerField(default=0)
    last_request_at = DateTimeField(null=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()
    vae = TextField(null=True)
    lora_string = TextField(null=True)

    class Meta:
        table_name = 'user_settings'

class UserQuota(BaseModel):
    id = AutoField()
    user_id = BigIntegerField(index=True)
    user_settings = ForeignKeyField(
        UserSettings,
        field='user_id',  # На какое поле ссылаемся в UserSettings
        column_name='user_id',  # Как называется колонка в таблице user_quota
        backref='quotas',
        null=True
    )

    is_unlimited = IntegerField(default=0)
    is_banned = IntegerField(default=0)
    free_used = IntegerField(default=0)
    free_limit = IntegerField(default=0)
    last_reset = DateTimeField(null=True)
    paid_credits = IntegerField(default=0)
    paid_used = IntegerField(default=0)

    class Meta:
        table_name = 'user_quota'

class UserPreset(BaseModel):
    id = AutoField()
    user_id = BigIntegerField(index=True)
    preset_key = CharField(max_length=50)
    name = CharField(max_length=50)
    prompt_suffix = TextField(default='')
    negative_suffix = TextField(default='')
    width = IntegerField(default=512)
    height = IntegerField(default=512)
    steps = IntegerField(default=20)
    is_safe_for_business = IntegerField(default=1)
    is_premium = IntegerField(default=0)
    created_at = DateTimeField()
    cfg_scale = FloatField(default=7.0)
    sampler = CharField(default='DPM++ 2M Karras')
    scheduler = CharField(default='Automatic')
    prompt_prefix = TextField(default='')

    class Meta:
        table_name = 'user_preset'

class GenerationRequest(BaseModel):
    id = AutoField()
    user = CharField(max_length=20, index=True)  # user_id как строка
    prompt = TextField()
    model_used = TextField(null=True)
    preset_used = CharField(max_length=50, null=True)
    status = CharField(max_length=20, default='pending')
    error_message = TextField(null=True)
    queue_position = IntegerField(null=True)
    generation_time_sec = FloatField(null=True)
    created_at = DateTimeField()

    class Meta:
        table_name = 'generation_requests'

class StarPayment(BaseModel):
    id = AutoField()
    user_id = BigIntegerField(index=True)
    payment_id = CharField(unique=True)
    stars_amount = IntegerField()
    credits_granted = IntegerField()
    currency = CharField(default='XTR')
    created_at = DateTimeField(null=True)

    class Meta:
        table_name = 'star_payments'

class AdCampaign(BaseModel):
    id = AutoField()
    title = CharField()
    ad_type = CharField(default='photo')
    content = TextField()
    target_link = CharField()
    btn_text = CharField(default='?? Перейти')
    remaining = IntegerField(constraints=[Check('remaining >= 0')])
    total_sold = IntegerField(default=0)
    is_active = IntegerField(default=1)
    created_at = DateTimeField(null=True)
    shown_count = IntegerField(default=0)

    class Meta:
        table_name = 'ad_campaigns'

class AdImpressionLog(BaseModel):
    id = AutoField()
    ad_id = ForeignKeyField(AdCampaign, backref='impressions')
    generation_id = ForeignKeyField(GenerationRequest, backref='impressions')
    shown_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'ad_impressions_log'