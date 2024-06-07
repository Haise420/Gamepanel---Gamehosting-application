from django.shortcuts import render, get_object_or_404, redirect
from .models import Machine, Server, Game, Customer, Mod, RconResult, Plugin, Ticket, TicketMessage
from ftplib import FTP, error_perm

from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import render_to_string


import concurrent.futures
import socket
import a2s


from api.views import server_info as api_server_info
from api.views import startCS16Server as api_start_server
from api.views import stopCS16Server as api_stop_server
from api.views import rcon_connection_view as api_status_server
from api.views import delete_cs16__server as api_delete_server
from api.views import create_cs16_server as api_create_server
from api.views import install_plugin_cs16 as api_install_plugin
from api.views import factoryreset_cs16_server as api_restart_server
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

from django.contrib.auth.hashers import make_password

import requests
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from urllib.parse import unquote
from builtins import FileNotFoundError
from paramiko import SSHClient, AutoAddPolicy
from django.http import HttpRequest
from paramiko.ssh_exception import AuthenticationException, SSHException
import io
import json
import re


api_install_plugin

@login_required(login_url=settings.LOGIN_URL_GAMEPANEL)
def gamepanel(request):
    customer_name = request.user.customer.name
    customer = request.user.customer 
    context = {'customer_name': customer_name, 'customer': customer}

    return render(request, 'gamepanel/home.html', context)

def gp_login(request):
    if request.method == 'POST':
        if 'demo' in request.POST:
            # Ako je pritisnuto Demo dugme, postavi vrednosti za korisničko ime i lozinku na "demo"
            username = 'demo'
            password = 'demonic420'
        else:
            # Inače, preuzmi vrednosti iz POST podataka
            username = request.POST['username']
            password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('gamepanel')  # Redirektuj na željenu stranicu nakon uspešnog prijavljivanja
        else:
            messages.error(request, 'Pogrešno korisničko ime ili lozinka.')

    return render(request, 'gamepanel/gp-login.html')


def user_logout(request):
    logout(request)
    return redirect('gamepanel')
    
def gp_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if any required field is missing
        if not name or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'gamepanel/gp-register.html')

        try:
            # Check if the user already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'User with this email already exists.')
                return render(request, 'gamepanel/gp-register.html')

            # Create a new user
            user = get_user_model().objects.create_user(email=email, password=password, username=name)
            user.first_name = name
            user.save()

            customer = Customer.objects.create(user=user, name=name, email=email)

            
            # Log in the user
            login(request, user)

            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('gamepanel')  # Redirect to the desired page after successful registration

        except Exception as e:
            # Handle any other unexpected errors
            messages.error(request, f'Error during registration: {str(e)}')
            return render(request, 'gamepanel/gp-register.html')

    return render(request, 'gamepanel/gp-register.html')


@login_required(login_url=settings.LOGIN_URL_GAMEPANEL)
def gp_servers(request):
    # Dohvati sve servere povezane sa trenutnim korisnikom
    customer_servers = Server.objects.filter(user=request.user.customer)
    customer_name = request.user.customer.name
    customer = request.user.customer  

    context = {'servers': customer_servers, 'customer_name': customer_name, 'customer': customer}
    
    return render(request, 'gamepanel/gp-servers.html', context)

@login_required(login_url=settings.LOGIN_URL_GAMEPANEL)
def gp_support(request):
    customer = request.user.customer
    customer_name = customer.name 
    user_tickets = Ticket.objects.filter(created_by=request.user)
    label_choices = Ticket.LABEL_CHOICES
    game_choices = Ticket.GAME_CHOICES

    ticket_messages = {}
    for ticket in user_tickets:
        last_message = TicketMessage.objects.filter(ticket=ticket).order_by('-created_at').first()
        ticket_messages[ticket.id] = last_message

    context = {'customer_name': customer_name, 'customer': customer, 'user_tickets': user_tickets, 'label_choices':label_choices, 'game_choices': game_choices, 'ticket_messages': ticket_messages}

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            subject = data.get('subject')
            description = data.get('description')
            label = data.get('label')
            game_name = data.get('game')

            # Pronađi odgovarajuću instancu igre
            game_instance = None
            for game_choice in game_choices:
                if game_choice[0] == game_name:
                    game_instance = game_choice[0]
                    break

            # Dodajte logiku za rukovanje podacima i kreiranje tiketa
            new_ticket = Ticket.objects.create(
                subject=subject,
                description=description,
                label=label,
                game=game_instance,
                created_by=request.user,
            )

            # Dodajte logiku za slanje odgovora u JSON formatu
            return JsonResponse({'success': True, 'message': 'Ticket created successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})


    return render(request, 'gamepanel/gp-support.html', context)

@login_required(login_url=settings.LOGIN_URL_GAMEPANEL)
def ticket_details(request, ticket_id):
    customer = request.user.customer
    ticket = Ticket.objects.get(id=ticket_id) 
    user_tickets = Ticket.objects.filter(created_by=request.user)
    label_choices = Ticket.LABEL_CHOICES
    game_choices = Ticket.GAME_CHOICES

    ticket_subject = ticket.subject
    ticket_status = ticket.status
    ticket_description = ticket.description

    # Prikupi sve poruke za odabrani tiket
    ticket_messages = TicketMessage.objects.filter(ticket=ticket).order_by('created_at')

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            content = data.get('content')

            # Dodajte logiku za kreiranje nove poruke
            TicketMessage.objects.create(
                conversation = ticket.ticket_conversation,
                ticket=ticket,
                sender=request.user,
                content=content
            )

            return JsonResponse({'success': True, 'message': 'Message created successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})


    context = {
        'customer': customer,
        'user_tickets': user_tickets,
        'label_choices': label_choices,
        'game_choices': game_choices,
        'ticket_messages': ticket_messages,
        'ticket': ticket,
        'ticket_subject': ticket_subject,
        'ticket_status': ticket_status,
        'ticket_description': ticket_description,
    }
    return render(request, 'gamepanel/ticket_details.html', context)


@login_required(login_url=settings.LOGIN_URL_GAMEPANEL)
@csrf_exempt
def gp_user(request):
    if request.user.is_authenticated:
        customer = request.user.customer

        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            field = request.POST.get('field')
            value = request.POST.get('value')

            print(customer)
            demo = "demo"
            print(demo)

            # Check if the customer is a "demo" user
            if str(customer) == demo:
                response_data = {'status': 'error', 'message': 'Cannot modify demo user.'}
                print(response_data)
                return JsonResponse(response_data)

            if field == 'email':
                customer.email = value
            elif field == 'password':
                # Check if the customer is a "demo" user
                if str(customer) != demo:
                    # Use set_password to hash and set the new password
                    customer.user.set_password(value)
                else:
                    response_data = {'status': 'error', 'message': 'Cannot modify password for demo user.'}
                    return JsonResponse(response_data)

            # Validate and save the changes
            customer.save()

            response_data = {'status': 'success', 'field': field, 'value': value}
            return JsonResponse(response_data)
        else:
            context = {'customer': customer}
            return render(request, 'gamepanel/gp-user.html', context)
    else:
        return redirect('login')

@login_required  
def agp_home(request):

    return render(request, 'gamepanel/agp-home.html')

@login_required    
def agp_servers(request):

    return render(request, 'gamepanel/agp-servers.html')

@login_required    
def agp_clients(request):

    return render(request, 'gamepanel/agp-clients.html')

@login_required    
def agp_machines(request):
    machines = Machine.objects.all()
    return render(request, 'gamepanel/agp-machines.html', {'machines': machines})

def check_ssh_connection(request, machine_id):
    try:
        machine = Machine.objects.get(pk=machine_id)
        ssh_client = machine.establish_ssh_connection()
        if ssh_client:
            # Proverite status konekcije
            if ssh_client.get_transport() is not None and ssh_client.get_transport().is_active():
                return HttpResponse("SSH konekcija je uspostavljena.")
            else:
                return HttpResponse("SSH konekcija nije uspostavljena.")
    except Machine.DoesNotExist:
        return HttpResponse("Machine not found.")
    except Exception as e:
        return HttpResponse(f"Error: {e}")

    return HttpResponse("An error occurred.")
    
def agp_support(request):

    return render(request, 'gamepanel/agp-support.html')
    
def agp_webftp(request):
    

   
        return render(request, 'gamepanel/agp-webftp.html')


@login_required
def cs_configure(request, server_id):
    try:
        server = get_object_or_404(Server, id=server_id)
        customer = server.user

        ftp_address = "ftp.soldiergang.com"
        ftp_port = 21

        with FTP() as ftp:
            ftp.connect(ftp_address, ftp_port)
            ftp.login(str(server.ftp_user), server.ftp_user.password)

            file_name = 'server.cfg'  # Adjust based on the actual file name
            full_file_path = f"/{server.port}/cstrike/{file_name}"

            buffer = []
            ftp.retrbinary(f'RETR {full_file_path}', buffer.append)

            content = b''.join(buffer).decode('utf-8')

        # Extract specific information from the server.cfg content using regular expressions
        hostname_match = re.search(r'hostname "(.*?)"', content)
        sv_downloadurl_match = re.search(r'sv_downloadurl "(.*?)"', content)
        rcon_password_match = re.search(r'rcon_password "(.*?)"', content)

        hostname = hostname_match.group(1) if hostname_match else ''
        sv_downloadurl = sv_downloadurl_match.group(1) if sv_downloadurl_match else ''
        rcon_password = rcon_password_match.group(1) if rcon_password_match else ''

        server.label = hostname
        server.rcon_password = rcon_password

        server.save()

        context = {
            'hostname': hostname,
            'sv_downloadurl': sv_downloadurl,
            'rcon_password': rcon_password,
            'server': server,
            'customer': customer,
        }

        if request.method == 'POST':
            try:
                if request.user.username == "demo":
                    # Korisniku "demo" šaljemo poruku direktno kroz kontekst
                    context['json_response'] = json.dumps({'status': 'Error', 'error': 'Demo korisnik ne moze vrsiti azuriranja.'})
                else:
                    # Nastavite sa procesuiranjem kao ranije
                    name = request.POST.get('name')
                    startup_line = request.POST.get('startup_line')
                    sv_downloadurl = request.POST.get('sv_downloadurl')
                    rcon_password = request.POST.get('rcon_password')

                    print(sv_downloadurl)

                    if hostname_match:
                        content = re.sub(r'hostname "(.*?)"', f'hostname "{name}"', content)
                    if sv_downloadurl_match:
                        content = re.sub(r'sv_downloadurl "(.*?)"', f'sv_downloadurl "{sv_downloadurl}"', content)
                    if rcon_password_match:
                        content = re.sub(r'rcon_password "(.*?)"', f'rcon_password "{rcon_password}"', content)

                    with FTP() as ftp:
                        ftp.connect(ftp_address, ftp_port)
                        ftp.login(str(server.ftp_user), server.ftp_user.password)

                        full_file_path = f"/{server.port}/cstrike/{file_name}"

                        with io.BytesIO(content.encode('utf-8')) as file_buffer:
                            ftp.storbinary(f'STOR {full_file_path}', file_buffer)

                    server.label = name
                    server.rcon_password = rcon_password
                    server.save()

                    # Dodajte poruku o uspehu u kontekst
                    context['json_response'] = json.dumps({'status': 'Success'})
                
            except Exception as e:
                # Dodajte poruku o grešci u kontekst
                context['json_response'] = json.dumps({'status': 'Error', 'error': str(e)})

        return render(request, 'gamepanel/cs-configure.html', context)

    except Exception as e:
        # Ako dođe do greške, vratite poruku o grešci u kontekstu
        return render(request, 'gamepanel/cs-configure.html', {'json_response': json.dumps({'status': 'Error', 'error': str(e)})})


    
@login_required
def cs_webftp(request, server_id, current_dir="/"):
    customer = request.user.customer 
    server = Server.objects.get(id=server_id)
    if request.user != server.user.user:
        return HttpResponseForbidden("Nemate pristup ovom serveru.")

    prethodna_stranica = request.COOKIES.get('prethodna_stranica', '/')

    try:
        

        # Fiksne vrednosti za adresu FTP servera i port
        ftp_address = "ftp.soldiergang.com"
        ftp_port = 21

        # Povezivanje na FTP server
        with FTP() as ftp:
            ftp.connect(ftp_address, ftp_port)
            ftp.login(str(server.ftp_user), server.ftp_user.password)

            # Promeni trenutni radni direktorijum na FTP serveru
            ftp.cwd(current_dir)

            # Dohvati listu fajlova na serveru u trenutnom direktorijumu
            file_list = ftp.nlst()

        context = {'server': server, 'file_list': file_list, 'current_dir': current_dir, 'prethodna_stranica': prethodna_stranica, 'customer': customer}

        return render(request, 'gamepanel/cs-webftp.html', context)
    except Exception as e:
        # Handle errors and return an error response
        return HttpResponse(f'Error: {e}', status=500)
        

@login_required
def fetch_file_content(request, server_id, file_path):
    try:
        server = get_object_or_404(Server, id=server_id)

        ftp_address = "ftp.soldiergang.com"
        ftp_port = 21

        # Povezivanje na FTP server
        with FTP() as ftp:
            ftp.connect(ftp_address, ftp_port)
            ftp.login(str(server.ftp_user), server.ftp_user.password)

            # Kreiraj pun put do fajla
            full_file_path = '/' + file_path  # Ovde možete prilagoditi prema vašoj strukturi

            # Dohvati sadržaj fajla
            buffer = []
            ftp.retrbinary(f'RETR {full_file_path}', buffer.append)

            # Spoji binarne podatke u string
            content = b''.join(buffer).decode('utf-8')

        return HttpResponse(content, content_type='text/plain')

    except Exception as e:
        # Handle errors and return an error response
        return HttpResponse(f'Error: {e}', status=500)


@login_required
def edit_file(request, server_id, file_path):
    try:
        server = get_object_or_404(Server, id=server_id)

        # Use settings or environment variables for configuration
        ftp_address = "ftp.soldiergang.com"
        ftp_port = 21

        # Decode the URL-encoded file path


        # Connect to FTP server
        with FTP() as ftp:
            ftp.connect(ftp_address, ftp_port)
            ftp.login(str(server.ftp_user), server.ftp_user.password)

            # Construct full file path using currentPath
            current_path = request.POST.get('current_path', '')  # Retrieve currentPath from POST data
            full_file_path = current_path + "/" + file_path  # Adjust based on FTP server structure
            
            # Retrieve file content
            buffer = []
            ftp.retrbinary(f'RETR {full_file_path}', buffer.append)

            # Convert binary data to string
            content = b''.join(buffer).decode('utf-8')

        if request.method == 'POST':
            # If the form is submitted, update the file content
            new_content = request.POST.get('file_content', '')

            # Save the updated content back to the file on the FTP server
            with FTP() as ftp:
                ftp.connect(ftp_address, ftp_port)
                ftp.login(str(server.ftp_user), server.ftp_user.password)

                # Store the new content in the file
                ftp.storbinary(f'STOR {full_file_path}', io.BytesIO(new_content.encode('utf-8')))

            return JsonResponse({'message': 'File updated successfully!'})

        # Render the form with the current file content
        return HttpResponse(content)

    except socket.error as e:
        return JsonResponse({'status': 'error', 'message': f'Error connecting to FTP server: {e}'}, status=500)

    except Exception as e:
        # Log the error for further investigation
        print(f'Unhandled error: {e}')
        return JsonResponse({'status': 'error', 'message': f'Error: {e}'}, status=500)




@login_required
def get_admins_info(users_ini_content):
    admins_info = []

    # Primer: analiza teksta pomoću regularnih izraza
    admin_pattern = re.compile(r'\s*"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"\s*')

    for line in users_ini_content.splitlines():
        match = admin_pattern.match(line)
        if match:
            admins_info.append({
                'name': match.group(1),
                'password': match.group(2),
                'flags': match.group(3),
                'accFlags': match.group(4)
            })

    return admins_info

@login_required
def edit_files(request, server_id, file_path):
    server = get_object_or_404(Server, id=server_id)
    customer = request.user.customer 

    if request.user != server.user.user:
        return HttpResponseForbidden("Nemate pristup ovom serveru.")
    try:


        ftp_address = "ftp.soldiergang.com"
        ftp_port = 21

        # Decode the URL-encoded file path

        # Connect to FTP server
        with FTP() as ftp:
            ftp.connect(ftp_address, ftp_port)
            ftp.login(str(server.ftp_user), server.ftp_user.password)

            # Construct full file path using currentPath
            current_path = request.POST.get('current_path', '')  # Retrieve currentPath from POST data
            print("Current path:", current_path)
            full_file_path = current_path + "/" + file_path  # Adjust based on FTP server structure
            print("FULL path:", full_file_path)
            # Retrieve file content
            buffer = []
            ftp.retrbinary(f'RETR {full_file_path}', buffer.append)

            # Convert binary data to string
            content = b''.join(buffer).decode('utf-8')

        if request.method == 'POST':
            # If the form is submitted, update the file content
            new_content = request.POST.get('file_content', '')

            # Save the updated content back to the file on the FTP server
            with FTP() as ftp:
                ftp.connect(ftp_address, ftp_port)
                ftp.login(str(server.ftp_user), server.ftp_user.password)

                # Store the new content in the file
                ftp.storbinary(f'STOR {full_file_path}', io.BytesIO(new_content.encode('utf-8')))
                messages.success(request, 'File updated successfully!')

            return redirect('edit_files', server_id=server.id, file_path=file_path)

        # Render the form with the current file content
        return render(request, 'gamepanel/edit_admins.html', {'file_content': content, 'current_path': current_path, 'server': server, 'customer': customer})

    except socket.error as e:
        return JsonResponse({'status': 'error', 'message': f'Error connecting to FTP server: {e}'}, status=500)

    except Exception as e:
        # Log the error for further investigation
        print(f'Unhandled error: {e}')
        return JsonResponse({'status': 'error', 'message': f'Error: {e}'}, status=500)


def edit_admins(request, server_id, file_path):
    server = get_object_or_404(Server, id=server_id)
    customer = request.user.customer 

    if request.user != server.user.user:
        return HttpResponseForbidden("Nemate pristup ovom serveru.")
    
    try:
        ftp_address = "ftp.soldiergang.com"
        ftp_port = 21

        # Decode the URL-encoded file path

        # Connect to FTP server
        with FTP() as ftp:
            ftp.connect(ftp_address, ftp_port)
            ftp.login(str(server.ftp_user), server.ftp_user.password)

            # Construct full file path using currentPath
            current_path = request.POST.get('current_path', '')  # Retrieve currentPath from POST data
            print("Current path:", current_path)
            full_file_path = f"/{server.port}//cstrike/addons/amxmodx/configs/users.ini"  # Adjust based on FTP server structure
            print("FULL path:", full_file_path)
            
            # Retrieve file content
            buffer = []
            ftp.retrbinary(f'RETR {full_file_path}', buffer.append)

            # Convert binary data to string
            content = b''.join(buffer).decode('utf-8')

        if request.method == 'POST':
            # If the form is submitted, update the file content
            new_content = request.POST.get('file_content', '')

            # Save the updated content back to the file on the FTP server
            with FTP() as ftp:
                ftp.connect(ftp_address, ftp_port)
                ftp.login(str(server.ftp_user), server.ftp_user.password)

                # Store the new content in the file
                ftp.storbinary(f'STOR {full_file_path}', io.BytesIO(new_content.encode('utf-8')))
                messages.success(request, 'File updated successfully!')

            # Redirect to the same page, or provide a JsonResponse
            if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'File updated successfully!'})
            else:
                return redirect('edit_admins', server_id=server.id, file_path=file_path)

        # Render the form with the current file content for GET requests
        return render(request, 'gamepanel/edit_admins.html', {'file_content': content, 'current_path': current_path, 'server': server, 'customer': customer})

    except socket.error as e:
        return JsonResponse({'status': 'error', 'message': f'Error connecting to FTP server: {e}'}, status=500)

    except Exception as e:
        # Log the error for further investigation
        print(f'Unhandled error: {e}')
        return JsonResponse({'status': 'error', 'message': f'Error: {e}'}, status=500)

def edit_plugins(request, server_id, file_path):
    server = get_object_or_404(Server, id=server_id)
    customer = request.user.customer 

    if request.user != server.user.user:
        return HttpResponseForbidden("Nemate pristup ovom serveru.")
    
    try:
        ftp_address = "ftp.soldiergang.com"
        ftp_port = 21

        # Decode the URL-encoded file path

        # Connect to FTP server
        with FTP() as ftp:
            ftp.connect(ftp_address, ftp_port)
            ftp.login(str(server.ftp_user), server.ftp_user.password)

            # Construct full file path using currentPath
            current_path = request.POST.get('current_path', '')  # Retrieve currentPath from POST data
            print("Current path:", current_path)
            full_file_path = f"/{server.port}//cstrike/addons/amxmodx/configs/plugins.ini"  # Adjust based on FTP server structure
            print("FULL path:", full_file_path)
            
            # Retrieve file content
            buffer = []
            ftp.retrbinary(f'RETR {full_file_path}', buffer.append)

            # Convert binary data to string
            content = b''.join(buffer).decode('utf-8')

        if request.method == 'POST':
            # If the form is submitted, update the file content
            new_content = request.POST.get('file_content', '')

            # Save the updated content back to the file on the FTP server
            with FTP() as ftp:
                ftp.connect(ftp_address, ftp_port)
                ftp.login(str(server.ftp_user), server.ftp_user.password)

                # Store the new content in the file
                ftp.storbinary(f'STOR {full_file_path}', io.BytesIO(new_content.encode('utf-8')))
                messages.success(request, 'File updated successfully!')

            # Redirect to the same page, or provide a JsonResponse
            if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'File updated successfully!'})
            else:
                return redirect('edit_admins', server_id=server.id, file_path=file_path)

        # Render the form with the current file content for GET requests
        return render(request, 'gamepanel/edit_admins.html', {'file_content': content, 'current_path': current_path, 'server': server, 'customer': customer})

    except socket.error as e:
        return JsonResponse({'status': 'error', 'message': f'Error connecting to FTP server: {e}'}, status=500)

    except Exception as e:
        # Log the error for further investigation
        print(f'Unhandled error: {e}')
        return JsonResponse({'status': 'error', 'message': f'Error: {e}'}, status=500)



@csrf_exempt
@login_required
def cs_console(request, server_id):
    server = Server.objects.get(id=server_id)
    customer = request.user.customer 
    rcon_results = RconResult.objects.filter(user=request.user).order_by('-timestamp')
    if request.user != server.user.user:
        return HttpResponseForbidden("Nemate pristup ovom serveru.")
    context = {'server': server, 'rcon_results': rcon_results, 'customer': customer}
    return render(request, 'gamepanel/cs-console.html', context)

@login_required
def cs_admins(request, server_id):
    customer = request.user.customer 
    server = Server.objects.get(id=server_id)

    context = {'server': server, 'customer': customer}
    return render(request, 'gamepanel/cs-admins.html', context)



@ensure_csrf_cookie
@login_required
def cs_mods(request, server_id):
    customer = request.user.customer 
    server = Server.objects.get(id=server_id)
    mods = Mod.objects.all()
    if request.user != server.user.user:
        return HttpResponseForbidden("Nemate pristup ovom serveru.")

    context = {'server': server, 'mods': mods, 'customer': customer}
    return render(request, 'gamepanel/cs-mods.html', context)

@csrf_exempt 
def update_server_mod(request, server_id):
    customer = request.user.customer 
    if request.method == 'GET': 
        mod_name = request.GET.get('mod_name') 

        try:
            mod_instance = Mod.objects.get(name=mod_name)
        except Mod.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mod with specified name does not exist'})

        server = Server.objects.get(id=server_id)
        server.mod = mod_instance
        server.save()


        first_response = api_stop_server(request, server_id)
        second_response = api_delete_server(request, server_id)
        third_response = api_create_server(request, server_id)



        if (
            first_response.status_code != 200 or
            second_response.status_code != 200 or
            third_response.status_code != 200
        ):
            return JsonResponse({'status': 'error', 'message': 'Failed to update server'})
        



        return JsonResponse({'status': 'success', 'message': 'Server updated successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def cs_plugins(request, server_id):
    customer = request.user.customer 
    server = Server.objects.get(id=server_id)
    plugins = Plugin.objects.all()
    if request.user != server.user.user:
        return HttpResponseForbidden("Nemate pristup ovom serveru.")

    

    context = {'server': server, 'plugins': plugins, 'customer': customer}
    return render(request, 'gamepanel/cs-plugins.html', context)

@login_required
def cs_backup(request, server_id):
    customer = request.user.customer 
    server = Server.objects.get(id=server_id)
    if request.user != server.user.user:
        return HttpResponseForbidden("Nemate pristup ovom serveru.")

    context = {'server': server, 'customer': customer}
    return render(request, 'gamepanel/cs-backup.html', context)

@login_required
def cs_boost(request, server_id):
    customer = request.user.customer 
    server = Server.objects.get(id=server_id)

    if request.user != server.user.user:
        return HttpResponseForbidden("Nemate pristup ovom serveru.")

    context = {'server': server, 'customer': customer}
    return render(request, 'gamepanel/cs-boost.html', context)

@login_required
def agp_machines_detail(request, machine_id):
    machine = Machine.objects.get(pk=machine_id)
    ssh_connected = False


    try:
        ssh_client = machine.establish_ssh_connection()
        if ssh_client:
            ssh_client.close()
            ssh_connected = True
    except Exception:
        pass
    
    return render(request, 'gamepanel/machine-overview.html', {'machine': machine, 'ssh_connected': ssh_connected})


def get_server_info(request, ip_port):
    server_arg = ip_port.strip()

    if not server_arg:
        return render(request, "gamepanel/query.html", {"status": "Empty"})

    if ":" in server_arg:
        ip, port_str = server_arg.split(":", 1)
    elif " " in server_arg:
        ip, port_str = server_arg.split(None, 1)  # Split on whitespace
    else:
        ip, port_str = server_arg, "27015"

    try:
        port = int(port_str)
    except ValueError:
        return render(request, "gamepanel/query.html", {"status": "Error", "error": "Port is not a number.", "server": server_arg}, status=400)

    if not 0 < port < 65536:
        return render(request, "gamepanel/query.html", {"status": "Error", "error": "Port has to be between 0 and 65535.", "server": server_arg}, status=400)

    try:
        socket.getaddrinfo(ip, port_str)
    except socket.gaierror:
        return render(request, "gamepanel/query.html", {"status": "Error", "error": "Invalid server address.", "server": server_arg}, status=400)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        info_future = pool.submit(a2s.info, (ip, port), timeout=3)
        players_future = pool.submit(a2s.players, (ip, port), timeout=3)

    concurrent.futures.wait((info_future, players_future))

    info_except = info_future.exception()
    players_except = players_future.exception()

    if isinstance(info_except, socket.timeout):
        return render(request, "gamepanel/query.html", {"status": "Error", "error": "Server did not respond.", "server": server_arg}, status=200)
    elif isinstance(info_except, a2s.BrokenMessageError):
        return render(request, "gamepanel/query.html", {"status": "Error", "error": "Server sent a broken response.", "server": server_arg}, status=200)
    elif info_except is not None:
        raise info_except

    info_res = info_future.result()

    if isinstance(players_except, socket.timeout):
        return render(request, "gamepanel/query.html", {"status": "InfoOnly", "info": info_res, "error": "Server did not respond.", "server": server_arg}, status=200)
    elif isinstance(players_except, a2s.BrokenMessageError):
        return render(request, "gamepanel/query.html", {"status": "InfoOnly", "info": info_res, "error": "Server sent a broken response.", "server": server_arg}, status=200)
    elif players_except is not None:
        raise players_except

    players_res = players_future.result()

    ping = round(info_res.ping * 1000, 2)
    
    info_data = {
        "server_name": info_res.server_name,
        "max_players": info_res.max_players,
        "player_count": info_res.player_count,
        "map_name": info_res.map_name,
    }

    players_data = [
    {
        "name": player.name,
        "score": player.score,
        "duration_minutes": int(player.duration // 60),
        "duration_seconds": round(player.duration % 60),
    }
    for player in players_res
]

    response_data = {
        "status": "Success",
        "info": info_data,
        "players": players_data,
        "server": server_arg,
        "ping": round(info_res.ping * 1000, 2),
    }

    return JsonResponse(response_data)

@login_required
def cs_overview(request, server_id):
    customer = request.user.customer 
    server = get_object_or_404(Server, id=server_id)
    
    if request.user != server.user.user:
        return HttpResponseForbidden("Nemate pristup ovom serveru.")

    ftp_user = server.ftp_user
    demo = 'demo'

    # Konvertuj ftp_user u string koristeći atribut username
    ftp_user_string = str(ftp_user.username)

    # Uporedi vrednost ftp_user_string sa stringom 'demo'
    is_demo_user = ftp_user_string == demo

    # Postavljanje vrednosti ftp_user_password u zavisnosti od is_demo_user
    if is_demo_user:
        ftp_user_password = ftp_user.password_label
    else:
        ftp_user_password = ftp_user.password

    ip_port = f"{server.ip_address}:{server.port}"
    
    try:
        server_info_data = get_server_info(request, ip_port)
        json_data = json.loads(server_info_data.content.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        # Dodaj default vrednosti u context kada ne možete dekodirati JSON
        context = {
            'server_name': 'N/A',
            'max_players': 'N/A',
            'player_count': '0',
            'current_map': 'N/A',
            'players': [],
            'server': server,
            'status': 'Offline',
            'ftp_user': ftp_user,
            'ftp_user_password': ftp_user_password,
            'machines': Machine.objects.all(),
            'customer': customer,
        }
        return render(request, 'gamepanel/cs-overview.html', context)

    # Dodaj json_data u context
    context = {
        'server_name': json_data['info']['server_name'],
        'max_players': json_data['info']['max_players'],
        'player_count': json_data['info']['player_count'],
        'current_map': json_data['info']['map_name'],
        'players': json_data['players'],
        'server': server,
        'status': 'Online',
        'ftp_user': ftp_user,
        'ftp_user_password': ftp_user_password,
        'machines': Machine.objects.all(),
        'customer': customer,
    }

    return render(request, 'gamepanel/cs-overview.html', context)

    
    
@login_required  
@csrf_exempt 
def pokreni_server(request, server_id):
    try:
        # Pozovi logiku iz startCS16Server API view-a
        response = api_start_server(request, server_id)

        # Proveri odgovor i dodaj logiku po potrebi

        # Nema preusmeravanja, korisnik ostaje na istoj stranici
        return HttpResponse('Server je pokrenut.')

    except Exception as e:
        # Tvoj kod za rukovanje greškom
        return HttpResponse(f'Greška: {str(e)}', status=500)

@login_required 
@csrf_exempt 
def stopiraj_server(request, server_id):
    try:
        # Pozovi logiku iz startCS16Server API view-a
        response = api_stop_server(request, server_id)

        # Proveri odgovor i dodaj logiku po potrebi

        # Nema preusmeravanja, korisnik ostaje na istoj stranici
        return HttpResponse('Server je pokrenut.')

    except Exception as e:
        # Tvoj kod za rukovanje greškom
        return HttpResponse(f'Greška: {str(e)}', status=500)

@login_required 
@csrf_exempt 
def restartuj_server(request, server_id):
    try:
        # Pozovi logiku iz startCS16Server API view-a
        stopiraj_server(request, server_id)

        # Pozovi logiku iz pokreni_server API view-a
        pokreni_server(request, server_id)

        # Proveri odgovor i dodaj logiku po potrebi

        # Nema preusmeravanja, korisnik ostaje na istoj stranici
        return HttpResponse('Server je restartovan.')

    except Exception as e:
        # Tvoj kod za rukovanje greškom
        return HttpResponse(f'Greška: {str(e)}', status=500)
    
@login_required 
@csrf_exempt 
def instaliraj_plugin(request, server_id, plugin_id):
    try:
        # Pozovi logiku iz startCS16Server API view-a
        response = api_install_plugin(request, server_id, plugin_id)

        # Proveri odgovor i dodaj logiku po potrebi

        # Nema preusmeravanja, korisnik ostaje na istoj stranici
        return HttpResponse('Plugin je instaliran.')

    except Exception as e:
        # Tvoj kod za rukovanje greškom
        return HttpResponse(f'Greška: {str(e)}', status=500)
        


@login_required 
@csrf_exempt 
def factory_restart_server(request, server_id):
    try:
        # Pozovi logiku iz startCS16Server API view-a
        response = api_restart_server(request, server_id)

        # Proveri odgovor i dodaj logiku po potrebi

        # Nema preusmeravanja, korisnik ostaje na istoj stranici
        return HttpResponse('Server vracen na fabricka podesavanja moda.')

    except Exception as e:
        # Tvoj kod za rukovanje greškom
        return HttpResponse(f'Greška: {str(e)}', status=500)

