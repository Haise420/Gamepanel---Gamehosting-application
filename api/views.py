
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import paramiko
import re
import socket
import struct
import time
from a2squery import A2SQuery
import a2s
from django.contrib.auth import authenticate, login, logout
from django.conf import settings


from django.contrib.auth.decorators import login_required, user_passes_test
import asyncio
from .console import *
from home.models import *
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt



def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser)
@api_view(['GET'])
def delete_cs16__server(request, server_id):
    try:
        
        server = Server.objects.get(id=server_id)
        
        ftp_user = server.ftp_user
        game = Game.objects.get()
        mod = server.mod
        
        
        
        # Pronalaženje odgovarajuće mašine (machine) za ovaj server
        machine = Machine.objects.get()  # Pretpostavljamo da polje "name" u Server modelu odgovara polju "name" u Machine modelu

        # Uspostavljanje SSH konekcije
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine.machine_address, port=22, username=machine.ssh_username, password=machine.ssh_password)

        delete_command = f"rm -r /home/{ftp_user}/{server.port}"
        clarify_delete_command = f"rm -r /home/{ftp_user}/{server.mod}"

        
        stdin, stdout, stderr = ssh.exec_command(delete_command)
        ssh.close()

        stdin, stdout, stderr = ssh.exec_command(clarify_delete_command)
        ssh.close()
        
        if not stderr.read():
            return Response({'message': f'CS 1.6 server je uspešno obrisan korisniku {ftp_user}'})
        else:
            return Response({'error': 'Došlo je do greške prilikom brisanja servera.'}, status=500)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@user_passes_test(is_superuser)
@api_view(['GET'])
def create_cs16_server(request, server_id):
    try:
        
        server = Server.objects.get(id=server_id)
        
        ftp_user = server.ftp_user
        game = Game.objects.get()
        mod = server.mod
        
        
        
        # Pronalaženje odgovarajuće mašine (machine) za ovaj server
        machine = Machine.objects.get()  # Pretpostavljamo da polje "name" u Server modelu odgovara polju "name" u Machine modelu

        # Uspostavljanje SSH konekcije
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine.machine_address, port=22, username=machine.ssh_username, password=machine.ssh_password)

        
        command = f"cp -r /home/gamefiles/{game.name}/{mod} /home/{ftp_user}"
        rename_command = f"mv /home/{ftp_user}/{mod} /home/{ftp_user}/{server.port}"
        set_permission_command = f"chmod -R 777 /home/{ftp_user}/{server.port}"
        
        
        stdin, stdout, stderr = ssh.exec_command(command)
        time.sleep(170)
        
        stdin, stdout, stderr = ssh.exec_command(rename_command)

        stdin, stdout, stderr = ssh.exec_command(set_permission_command)
        ssh.close()
        
        if not stderr.read():
            return Response({'message': f'CS 1.6 server je uspešno kreiran korisniku {ftp_user}'})
        else:
            return Response({'error': 'Došlo je do greške prilikom pravljenja servera.'}, status=500)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def startCS16Server(request, server_id):
    try:

        server = Server.objects.get(id=server_id)
        machine = Machine.objects.get()
        game = Game.objects.get()
        
        ftp_username = server.ftp_user
        startup_line = server.startup_line
        
        



        # Uspostavljanje SSH konekcije
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine.machine_address, port=22, username=machine.ssh_username, password=machine.ssh_password)
        
        # Ovde možete izvršavati različite komande na serveru preko ssh.exec_command() ili raditi druge SSH radnje.
        # Na primer, izvršite komandu za pokretanje CS 1.6 servera:
        command = f"screen -dmS {ftp_username}_server{server.port} bash -c 'cd /home/{ftp_username}/{server.name} && {startup_line} -port {server.port} +map {server.map} +maxplayers {server.max_players} -pingboost 1'"
        stdin, stdout, stderr = ssh.exec_command(command)

        # Provera da li je komanda uspešno izvršena
        if not stderr.read():
            server.status = 'online'
            server.save()
            return Response({'message': 'CS 1.6 server je uspešno pokrenut.'})
        else:
            return Response({'error': 'Došlo je do greške prilikom pokretanja servera.'}, status=500)
    except Server.DoesNotExist:
        return Response({'error': 'Server nije pronađen.'}, status=404)
    except Machine.DoesNotExist:
        return Response({'error': 'Mašina nije pronađena.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    

@api_view(['GET'])
def stopCS16Server(request, server_id):
    try:
        # Pronalaženje odgovarajućeg servera iz baze podataka
        server = Server.objects.get(id=server_id)
        
        # Pronalaženje odgovarajuće mašine (machine) za ovaj server
        machine = Machine.objects.get()
        ftp_username = server.ftp_user
        



        # Uspostavljanje SSH konekcije
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine.machine_address, port=22, username=machine.ssh_username, password=machine.ssh_password)
        
        # Ovde možete izvršavati različite komande na serveru preko ssh.exec_command() ili raditi druge SSH radnje.
        # Na primer, izvršite komandu za pokretanje CS 1.6 servera:
        command = f"screen -X -S {ftp_username}_server{server.port} quit"
        stdin, stdout, stderr = ssh.exec_command(command)

        # Provera da li je komanda uspešno izvršena
        if not stderr.read():
            return Response({'message': 'CS 1.6 server je uspešno stopiran.'})
        else:
            return Response({'error': 'Došlo je do greške prilikom stopiranja servera.'}, status=500)
    except Server.DoesNotExist:
        return Response({'error': 'Server nije pronađen.'}, status=404)
    except Machine.DoesNotExist:
        return Response({'error': 'Mašina nije pronađena.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def server_info(request, server_id):
    # Postavite IP adresu i port vašeg CS 1.6 servera
    server = Server.objects.get(id=server_id)
    server_address = (str(server.ip_address), int(server.port))

    try:
        with A2SQuery(*server_address) as a2s:
            info = a2s.info()

            # Informacije o serveru
            server_name = info.name
            player_count = info.players
            max_players = info.max_players
            current_map = info.map
            
            status = "Online"

            data = {
                'server_name': server_name,
                'player_count': player_count,
                'max_players': max_players,
                'current_map': current_map,
                'status': status,
            }

            return JsonResponse(data)

    except Exception as e:
        status = "Offline"
        # Obrada grešaka ako ne možete dohvatiti informacije
        data = {'error_message': f"Greška prilikom komunikacije sa serverom: {str(e)}",
                'status': status,}
        return JsonResponse(data)

@user_passes_test(is_superuser)
@api_view(['GET'])
def send_rcon_cs16_server(request, server_id, rcon_command):
    server = Server.objects.get(id=server_id)
    server_host = str(server.ip_address)
    server_port = server.port
    rcon_password = str(server.rcon_password)

    # Initialize Console object
    console = Console(host=server_host, port=server_port, password=rcon_password)

    try:
        # Connect to the server
        console.connect()
        
        server_info = console.execute(rcon_command)

        # Sačuvaj rezultat u bazi podataka
        RconResult.objects.create(user=request.user, result=server_info)

        # Return the parsed information as JSON response
        return JsonResponse({'server_info': server_info})

    except Exception as e:
        # Handle errors and return an error response
        return JsonResponse({'error': str(e)}, status=500)

    finally:
        # Always disconnect to release resources
        console.disconnect()

@user_passes_test(is_superuser)
@api_view(['GET'])
def rcon_connection_view(request, server_id):
    server = Server.objects.get(id=server_id)
    server_host = str(server.ip_address)
    server_port = server.port
    rcon_password = str(server.rcon_password)

    # Initialize Console object
    console = Console(host=server_host, port=server_port, password=rcon_password)

    try:
        # Connect to the server
        console.connect()
        
        server_info = console.execute("status")

        # Execute RCON command to get server information
        parsed_info = parse_hlds_status(server_info)

        # Return the parsed information as JSON response
        return JsonResponse(parsed_info)

    except Exception as e:
        # Handle errors and return an error response
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # Always disconnect to release resources
        console.disconnect()


def parse_hlds_status(status_string):
    params = [
        {"name": 'hostname', "pattern": "^hostname\s*:\s*(.*)$"},
        {"name": 'version', "pattern": "version\s*:\s*(.*)$"},
        {"name": 'tcp/ip', "pattern": "tcp\/ip\s*:\s*(.*)"},
        {"name": 'map', "pattern": "map\s*:\s*([\w-]+).*$"},
        {"name": 'maxplayers', "pattern": "players\s*:\s*(\d+).*\((\d+).*\)$"}
    ]

    matches = {}
    for param in params:
        match = re.search(param['pattern'], status_string, re.MULTILINE | re.IGNORECASE)
        if match:
            matches[param['name']] = match.group(1)

    # Pravimo listu linija sa informacijama o igračima
    player_data_lines = [line for line in status_string.split('\n') if line.startswith("#")]

    # Ažuriramo parsiranje igrača
    players = [parse_player_line(line) for line in player_data_lines[1:]]  # Preskoči prvu liniju sa zaglavljem
    matches['players'] = players

    return matches


def _combine_array(row, header):
    return dict(zip(header, row))

def parse_player_line(string):
    # Uzimamo deo između navodnika kao ime
    name_start = string.find('"') + 1
    name_end = string.find('"', name_start)
    name = string[name_start:name_end]

    # Razbijamo liniju na reči i uzimamo samo one koje nisu prazne
    words = [word.strip('"') for word in string.split() if word.strip('"')]

    # Provera za uniqueid
    uniqueid_candidates = [word for word in words if word.startswith(("VALVE", "STEAM", "BOT"))]
    uniqueid = uniqueid_candidates[0] if uniqueid_candidates else None

    # Vraćamo rezultat
    return {
        "#": words[0],
        "name": name,
        "userid": int(words[1]) if words[1].isdigit() else None,
        "uniqueid": uniqueid,
        "frag": words[4],
        "time": words[5],
        "ping": words[6],
        "loss": words[7],
        "adr": words[8] if len(words) > 7 else None
    }






def explode_by_whitespace(string):
    pattern = r"[\s,]*\"([^\"]+)\"[\s,]*|" r"[\s,]*'([^']+)'[\s,]*|" r"[\s,]+"
    return re.split(pattern, string)


def replace_null_with_empty_string(player_info, header):
    for i, value in enumerate(player_info):
        if value is None:
            player_info[i] = header[i]  # Koristi vrednost iz zaglavlja
    return player_info


@api_view(['GET'])
def install_plugin_cs16(request, server_id, plugin_id):
    try:

        server = Server.objects.get(id=server_id)
        plugin = Plugin.objects.get(id=plugin_id)

        machine = Machine.objects.get()
        game = Game.objects.get()
        
        ftp_user = server.ftp_user

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine.machine_address, port=22, username=machine.ssh_username, password=machine.ssh_password)
        
        command = f"cp /home/plugins/{server.game}/{plugin.name} /home/{ftp_user}/{server.port}/cstrike/addons/amxmodx/plugins"
        stdin, stdout, stderr = ssh.exec_command(command)


        if not stderr.read():

            return Response({'message': 'Uspesno instaliran plugin na cs 1.6 server! .'})
        else:
            return Response({'error': 'Došlo je do greške prilikom instaliranja plugina.'}, status=500)
    except Server.DoesNotExist:
        return Response({'error': 'Server nije pronađen.'}, status=404)
    except Machine.DoesNotExist:
        return Response({'error': 'Mašina nije pronađena.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def factoryreset_cs16_server(request, server_id):
    try:
        # Pozovi API view za brisanje servera
        delete_cs16__server(request, server_id)
        # Proveri odgovor i dodaj logiku po potrebi
        
        # Pozovi API view za kreiranje servera
        create_cs16_server(request, server_id)
        # Proveri odgovor i dodaj logiku po potrebi

        # Vrati odgovor korisniku (npr. kombinacija poruka iz delete_response i create_response)
        return Response({'message': f'CS 1.6 server je uspešno resetovan.'})

    except Exception as e:
        # Tvoj kod za rukovanje greškom
        return Response({'error': str(e)}, status=500)