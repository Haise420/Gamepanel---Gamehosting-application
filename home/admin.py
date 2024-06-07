from django.contrib import admin
from .models import *
from .models import Mod

# Register your models here.
admin.site.register(Customer)
admin.site.register(Machine)
admin.site.register(Game)
admin.site.register(Mod)
admin.site.register(Server)
admin.site.register(FTP_User)
admin.site.register(Plugin)
admin.site.register(RconResult)

class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 1  # Postavite na željeni broj prikazanih polja za unos TicketMessage
    readonly_fields = ['content']  # Dodajte ovo polje kako biste ga prikazali kao samo za čitanje

class TicketConversationAdmin(admin.ModelAdmin):
    inlines = [TicketMessageInline]

admin.site.register(Ticket)
admin.site.register(TicketMessage)
admin.site.register(TicketConversation, TicketConversationAdmin)