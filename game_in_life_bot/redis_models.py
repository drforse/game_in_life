from rom import *


class Theft(Model):
    chat_id = Integer(required=True, index=True)
    criminal_id = Integer(required=True, index=True)
    victim_id = Integer(required=True, index=True)
    stolen_money = Float(default=0.0)
    stolen_items = Json(default="{}")
    created_at = DateTime(required=True, index=True)
    success = Boolean(default=True)
    is_completed = Boolean(default=False)
