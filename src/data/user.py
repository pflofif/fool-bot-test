import mongoengine as me


class User(me.Document):
    chat_id = me.IntField(required=True, unique=True)
    name = me.StringField(required=True)
    surname = me.StringField(required=True)
    username = me.StringField(required=True)
    registration_date = me.DateTimeField(required=True)
    last_update_date = me.DateTimeField(required=True)
    last_interaction_date = me.DateTimeField(required=True)
    full_status = me.BooleanField(default=False)
    full_status_start_date = me.DateTimeField(default=None)
    full_status_end_date = me.DateTimeField(default=None)
    polls_participated = me.IntField(default=0)
    secretary_status = me.BooleanField(default=False)
    is_blocked = me.BooleanField(default=False)

    def set_secretary_status(self):
        if self.secretary_status is False:
            self.secretary_status = True
            self.save()
            print(f"@{self.username} is now a Secretary!")

    def check_secretary_status(self):
        if self.secretary_status:
            self.secretary_status = False
            self.save()
            print(f"@{self.username} is not a Secretary anymore!")

    @staticmethod
    def get_fullmembers_list():
        return [user for user in User.objects.filter(full_status=True)]
