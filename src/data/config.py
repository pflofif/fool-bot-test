import mongoengine as me


class Config(me.Document):
    secretary_user_name = me.StringField(default="cristina_sodzak")