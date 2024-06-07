from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
import paramiko


from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager

class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class Customer(models.Model):
    XP_CHOICES = [
        ('1', '1 Level'),
        ('2', '2 Level'),
        ('3', '3 Level'),
        ('4', '4 Level'),
        ('5', '5 Level'),
    ]

    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True)
    balance = models.IntegerField(null=True, blank=True, default=0)
    xp = models.IntegerField(default=0, null=True, blank=True)
    level = models.CharField(max_length=2, choices=XP_CHOICES, default='1')
    img = models.ImageField(upload_to='customer-profile-pictures/', blank=True, default='user.png')

    objects = CustomerManager()

    def save(self, *args, **kwargs):
        # Ensure the User instance is created or updated
        if not self.user:
            self.user = User(email=self.email)
        self.user.save()

        # Set the user field of Customer to the User instance
        self.user.customer = self
        self.user.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def __len__(self):
        return len(self.name)

    def add_xp(self, amount):
        self.xp += amount
        if self.xp >= 420:
            self.xp = 420  # Limit XP to 420
            self.level_up()

    def level_up(self):
        if self.level == '1' and self.xp >= 420:
            self.level = '2'

    
class Machine(models.Model):
    name = models.CharField(max_length=200)
    owner = models.CharField(max_length=200)
    os = models.CharField(max_length=200)
    machine_address = models.GenericIPAddressField(null=True, unique=True)
    ssh_username = models.CharField(max_length=200)
    ssh_password = models.CharField(max_length=200)
    ssh_port = models.PositiveBigIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False,null=True, blank=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    img = models.ImageField(blank=True)

    def establish_ssh_connection(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_client.connect(
                self.ip_address,
                port=self.ssh_port,
                username=self.ssh_username,
                password=self.ssh_password
            )
            # Ovde možete izvršavati različite komande na serveru preko ssh_client.exec_command() ili raditi druge SSH radnje.
            return ssh_client
        except Exception as e:
            print(f'Greška pri SSH konekciji za {self.name}: {e}')
            return None

    def close_ssh_connection(self, ssh_client):
        if ssh_client:
            ssh_client.close()
            
    def __str__(self):
        return self.machine_address
            
class Game(models.Model):
    name = models.CharField(max_length=300)
    img = models.ImageField(blank=True)
    

    
    def __str__(self):
        return self.name
    
    
class Mod(models.Model):
    MOD_CHOICES = [
            ('clanwar', 'clanwar'),
            ('zombieplague', 'zombieplague'),
            ('surf', 'surf'),
            ('deathrun', 'deathrun'),
            ('knifearena', 'knifearena'),
            ('gungame', 'gungame'),
            ('deathmatch', 'deathmatch'),
            ('fy_snow', 'fy_snow'),
            ('public', 'public'),
        ]

    name = models.CharField(max_length=30, choices=MOD_CHOICES, blank=True, null=True)
    label = models.CharField(max_length=30, blank=True, null=True)
    img = models.ImageField(upload_to='mods/', blank=True)

    version = models.CharField(max_length=30, blank=True, null=True)
    
    def __str__(self):
        return self.get_name_display()

    
class FTP_User(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    username = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)

    
    def random_password():
        random_str = get_random_string(length=14, allowed_chars='abcdeifgjlmnoprtqwzx0123456789')
        return str(random_str)
    
    password = models.CharField(max_length=50, default=random_password)

    password_label = models.CharField(max_length=150, blank=True, null=True)
    
    def __str__(self):
        return self.name
     
    
class Server(models.Model):
    name = models.CharField(max_length=300)
    label = models.CharField(max_length=300, blank=True, null=True)
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    mod = models.ForeignKey(Mod, null=True, blank=True, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='servers', null=True, blank=True)
    port = models.CharField(max_length=15, blank=True)
    ip_address = models.ForeignKey(Machine, to_field='machine_address', null=True, on_delete=models.CASCADE)
    ftp_user = models.ForeignKey(FTP_User, null=True, blank=True, on_delete=models.CASCADE, related_name='server')
    startup_line = models.CharField(max_length=300, null=True, blank=True)
    max_players = models.CharField(max_length=300, null=True, blank=True)
    map = models.CharField(max_length=300, null=True, blank=True)
    
    rcon_password = models.CharField(max_length=300, null=True, blank=True)
    
    
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ] 

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='offline')
    
    
    is_active = models.BooleanField(default=False,null=True, blank=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    date_over = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class RconResult(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.CASCADE)
    result = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return self.user

class Plugin(models.Model):
    PLUGIN_CHOICES = [
            ('clanwar', 'clanwar'),
            ('zombieplague', 'zombieplague'),
            ('surf', 'surf'),
            ('deathrun', 'deathrun'),
            ('knifearena', 'knifearena'),
            ('gungame', 'gungame'),
            ('deathmatch', 'deathmatch'),
            ('fy_snow', 'fy_snow'),
            ('public', 'public'),
        ]


    name = models.CharField(max_length=300, null=True, blank=True)
    label = models.CharField(max_length=300, null=True, blank=True)
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.CASCADE)
    version = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(max_length=2500, null=True, blank=True)

    category = models.CharField(max_length=300, choices=PLUGIN_CHOICES, null=True, blank=True)

    img = models.ImageField(upload_to='plugins/', blank=True)

    def __str__(self):
        return self.name




class Ticket(models.Model):
    LABEL_CHOICES = (
        ('Uplata', 'Uplata'),
        ('Pitanje', 'Pitanje'),
        ('Pomoc', 'Pomoc'),
        ('Hitna pomoc!', 'Hitna pomoc!'),
    )

    STATUS_CHOICES = (
        ('Novi', 'Novi'),
        ('Odgovoren', 'Odgovoren'),
        ('Zakljucan', 'Zakljucan'),
    )

    SEEN_CHOICES = (
        ('unseen', 'Unseen'),
        ('seen', 'Seen'),
    )

    GAME_CHOICES = [
        ('Counter-Strike 1.6', 'Counter-Strike 1.6'),
        ('CS2', 'CS2'),
        ('SA:MP', 'SA:MP'),
        ('Minecraft', 'Minecraft'),
    ]

    subject = models.CharField(max_length=255)
    description = models.TextField()
    label = models.CharField(max_length=20, choices=LABEL_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Novi')
    seen = models.CharField(max_length=10, choices=SEEN_CHOICES, default='unseen')
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='tickets_created')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tickets_assigned')
    game = models.CharField(max_length=50 ,choices=GAME_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.status


    def save(self, *args, **kwargs):
        super(Ticket, self).save(*args, **kwargs)

        # Prilikom kreiranja tiketa, automatski kreirajte pripadajuću konverzaciju
        if not hasattr(self, 'ticket_conversation'):
            conversation = TicketConversation.objects.create(ticket=self)
            self.ticket_conversation = conversation
            self.save()


class TicketConversation(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='ticket_conversation')
    messages = models.ManyToManyField('TicketMessage', related_name='ticket_messages')

    def __str__(self):
        return f"Konverzacija za tiket: {self.ticket.subject}"


class TicketMessage(models.Model):
    conversation = models.ForeignKey(TicketConversation, on_delete=models.CASCADE, related_name='ticket_messages', null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='ticket_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.conversation} "