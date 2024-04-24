import mongoengine as me


class Quote(me.Document):
    not_full = me.ListField(field=me.StringField())