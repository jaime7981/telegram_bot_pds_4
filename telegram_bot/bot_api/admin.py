from django.contrib import admin
from bot_api.models import Player, Chat, Stats, NumberGame

# Register your models here.
admin.site.register(Player)
admin.site.register(Chat)
admin.site.register(Stats)
admin.site.register(NumberGame)