#!/usr/bin/env python3
"""
Validador de Streams - Ejecutable desde GitHub
Descarga, valida y puede actualizar streams remotamente
"""

import urllib.request
import urllib.error
from urllib.parse import urlparse
import socket
import re
import json
import base64
import sys
import os

# Configuración de GitHub
GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "jsosao"
REPO_NAME = "Bics"
FILE_PATH = "country/apps"
RAW_FILE_URL = "https://raw.githubusercontent.com/jsosao/Bics/refs/heads/main/country/apps"

def validate_stream_url(url, timeout=10):
    """
    Valida si una URL de streaming está en línea y responde correctamente.
    """
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return False
        
        socket.setdefaulttimeout(timeout)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if 200 <= response.getcode() < 400:
                return True
            
        return False
        
    except urllib.error.HTTPError as e:
        return 200 <= e.code < 400
        
    except (urllib.error.URLError, socket.timeout, socket.error):
        return False
        
    except Exception:
        return False

def parse_stream_block(block_text):
    """
    Parsea un bloque de stream y extrae la información relevante.
    """
    try:
        title_match = re.search(r'Title:\s*"([^"]*)"', block_text)
        title = title_match.group(1) if title_match else ""
        
        stream_match = re.search(r'Stream:\s*"([^"]*)"', block_text)
        stream_url = stream_match.group(1) if stream_match else ""
        
        artist_match = re.search(r'Artist:\s*"([^"]*)"', block_text)
        artist = artist_match.group(1) if artist_match else "web"
        
        stream_format_match = re.search(r'streamFormat:\s*"([^"]*)"', block_text)
        stream_format = stream_format_match.group(1) if stream_format_match else "hls|mts"
        
        switching_strategy_match = re.search(r'SwitchingStrategy:\s*"([^"]*)"', block_text)
        switching_strategy = switching_strategy_match.group(1) if switching_strategy_match else "full-adaptation"
        
        logo_match = re.search(r'Logo:\s*"([^"]*)"', block_text)
        logo = logo_match.group(1) if logo_match else "https://raw.githubusercontent.com/jsosao/Bics/main/picons/no_logo.png"
        
        live_match = re.search(r'Live:\s*(true|false)', block_text)
        live = live_match.group(1) if live_match else "true"
        
        return {
            'artist': artist,
            'title': title,
            'stream_format': stream_format,
            'switching_strategy': switching_strategy,
            'logo': logo,
            'stream_url': stream_url,
            'live': live
        }
    except Exception:
        return None

def update_title_status(title, is_online):
    """
    Actualiza el título basado en el estado de la URL.
    """
    has_x_marker = title.startswith("[X] ")
    
    if is_online:
        if has_x_marker:
            return title[4:]
        else:
            return title
    else:
        if not has_x_marker:
            return f"[X] {title}"
        else:
            return title

def create_stream_block(stream_data):
    """
    Crea un bloque de stream en el formato correcto.
    """
    return f'''{{
    Artist: "{stream_data['artist']}"
    Title: "{stream_data['title']}"
    streamFormat: "{stream_data['stream_format']}"
    SwitchingStrategy: "{stream_data['switching_strategy']}"
    Logo: "{stream_data['logo']}"
    Stream: "{stream_data['stream_url']}"
    Live: {stream_data['live']}
}}'''

def download_file_content(url):
    """
    Descarga el contenido de un archivo desde una URL.
    """
    try:
        print(f"📥 Descargando contenido desde: {url}")
        
        headers = {
            'User-Agent': 'GitHub-Stream-Validator/1.0'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.getcode() == 200:
                content = response.read().decode('utf-8')
                print(f"✅ Contenido descargado exitosamente ({len(content)} caracteres)")
                return content
            else:
                print(f"❌ Error: Código de respuesta {response.getcode()}")
                return None
                
    except Exception as e:
        print(f"❌ Error al descargar el archivo: {str(e)}")
        return None

def save_local_copy(content, filename="apps_validated.txt"):
    """
    Guarda una copia local del contenido procesado.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Copia local guardada como: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar copia local: {str(e)}")
        return False

def update_github_file(content, github_token=None, commit_message="Actualización automática de streams validados"):
    """
    Actualiza el archivo en GitHub (requiere token de acceso).
    """
    if not github_token:
        print("⚠️  No se proporcionó token de GitHub. Solo se guardará copia local.")
        return False
    
    try:
        # Obtener información actual del archivo
        api_url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Stream-Validator/1.0'
        }
        
        req = urllib.request.Request(api_url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            file_info = json.loads(response.read().decode('utf-8'))
            sha = file_info['sha']
        
        # Preparar datos para la actualización
        content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        update_data = {
            'message': commit_message,
            'content': content_encoded,
            'sha': sha
        }
        
        # Realizar la actualización
        req_data = json.dumps(update_data).encode('utf-8')
        req = urllib.request.Request(api_url, data=req_data, headers=headers, method='PUT')
        
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                print("🚀 Archivo actualizado exitosamente en GitHub!")
                return True
            else:
                print(f"❌ Error al actualizar: Código {response.getcode()}")
                return False
                
    except Exception as e:
        print(f"❌ Error al actualizar GitHub: {str(e)}")
        return False

def process_streams(content, validate_urls=True):
    """
    Procesa el contenido de streams y valida las URLs.
    """
    # Dividir el contenido en bloques
    blocks = []
    current_block = ""
    brace_count = 0
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        current_block += line + '\n'
        brace_count += line.count('{') - line.count('}')
        
        if brace_count == 0 and current_block.strip():
            blocks.append(current_block.strip())
            current_block = ""
    
    if not blocks:
        print("❌ No se encontraron bloques de streams válidos.")
        return None
    
    print(f"📊 Se encontraron {len(blocks)} streams para procesar.")
    
    if validate_urls:
        print("🔍 Iniciando validación de URLs...")
    
    updated_blocks = []
    valid_count = 0
    invalid_count = 0
    updated_count = 0
    
    for i, block in enumerate(blocks, 1):
        stream_data = parse_stream_block(block)
        
        if not stream_data:
            print(f"⚠️  Error al parsear el bloque {i}, se mantiene sin cambios.")
            updated_blocks.append(block)
            continue
        
        original_title = stream_data['title']
        stream_url = stream_data['stream_url']
        
        if validate_urls and stream_url:
            print(f"🔍 Validando {i}/{len(blocks)}: {original_title[:50]}...")
            is_online = validate_stream_url(stream_url)
            
            if is_online:
                valid_count += 1
                print("  ✅ Online")
            else:
                invalid_count += 1
                print("  ❌ Offline")
            
            new_title = update_title_status(original_title, is_online)
            
            if new_title != original_title:
                updated_count += 1
                print(f"  🔄 Título actualizado: '{original_title}' → '{new_title}'")
            
            stream_data['title'] = new_title
        else:
            print(f"📝 Procesando {i}/{len(blocks)}: {original_title[:50]} (sin validar)")
        
        updated_block = create_stream_block(stream_data)
        updated_blocks.append(updated_block)
    
    # Generar contenido final
    final_content = '\n'.join(updated_blocks)
    
    # Mostrar estadísticas
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"   Total de streams: {len(blocks)}")
    if validate_urls:
        print(f"   URLs válidas: {valid_count}")
        print(f"   URLs inválidas: {invalid_count}")
        print(f"   Títulos actualizados: {updated_count}")
        if (valid_count + invalid_count) > 0:
            percentage = (valid_count / (valid_count + invalid_count)) * 100
            print(f"   Porcentaje de URLs válidas: {percentage:.1f}%")
    
    return final_content

def main():
    """
    Función principal del programa.
    """
    print("🎯 === VALIDADOR DE STREAMS - GITHUB EDITION ===")
    print(f"📍 Repositorio: {REPO_OWNER}/{REPO_NAME}")
    print(f"📄 Archivo: {FILE_PATH}")
    print()
    
    # Descargar contenido
    content = download_file_content(RAW_FILE_URL)
    if not content:
        print("❌ No se pudo descargar el archivo. Terminando programa.")
        return 1
    
    print()
    
    # Pregunta sobre validación
    print("❓ ¿Desea validar las URLs de streaming? (s/n): ", end="")
    validate_choice = input().lower().strip()
    validate_urls = validate_choice in ['s', 'si', 'sí', 'y', 'yes']
    
    if not validate_urls:
        print("⚡ Procesando sin validar URLs...")
    
    print()
    
    # Procesar streams
    processed_content = process_streams(content, validate_urls)
    
    if not processed_content:
        print("❌ Error al procesar el contenido.")
        return 1
    
    # Guardar copia local
    save_local_copy(processed_content)
    
    print()
    
    # Pregunta sobre actualización en GitHub
    print("❓ ¿Desea actualizar el archivo en GitHub? (requiere token) (s/n): ", end="")
    update_choice = input().lower().strip()
    
    if update_choice in ['s', 'si', 'sí', 'y', 'yes']:
        print("🔑 Ingrese su token de GitHub (o Enter para omitir): ", end="")
        github_token = input().strip()
        
        if github_token:
            print()
            print("🚀 Intentando actualizar archivo en GitHub...")
            success = update_github_file(processed_content, github_token)
            if not success:
                print("⚠️  La actualización en GitHub falló, pero la copia local fue guardada.")
        else:
            print("⚠️  No se proporcionó token. Solo se guardó la copia local.")
    
    print()
    print("✅ === PROCESO COMPLETADO ===")
    print("📁 Revisa el archivo 'apps_validated.txt' para ver los resultados.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
