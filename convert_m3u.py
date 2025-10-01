import requests
import re
import os

def get_country_code(title):
    """Extrae el código de país del título"""
    match = re.match(r'^([A-Z]{2}):', title)
    if match:
        return match.group(1).lower()
    return "xx"

def get_tag(group_title, title):
    """Determina el tag basado en el grupo y título"""
    group_lower = group_title.lower()
    title_lower = title.lower()
    
    if 'sport' in group_lower or 'sport' in title_lower:
        return "Sports"
    elif 'news' in group_lower or 'news' in title_lower:
        return "News"
    elif 'kids' in group_lower or 'kids' in title_lower:
        return "Kids"
    elif 'music' in group_lower or 'music' in title_lower:
        return "Music"
    elif 'entertainment' in group_lower:
        return "Entertainment"
    elif 'documentary' in group_lower or 'docu' in group_lower:
        return "Documentary"
    else:
        return "General"

def escape_stream_url(url):
    """Convierte la URL en formato escapado"""
    return url.replace('http://', 'http[:[/][/]]').replace('.', '[.]').replace('/', '[/]')

def get_logo_url(title, picons_base_url):
    """Genera la URL del logo basándose en el título"""
    # Eliminar prefijo de país
    clean_title = re.sub(r'^[A-Z]{2}:\s*', '', title)
    
    # Convertir a minúsculas y reemplazar espacios/caracteres especiales
    logo_name = clean_title.lower()
    logo_name = re.sub(r'[^\w\s-]', '', logo_name)
    logo_name = re.sub(r'\s+', '_', logo_name.strip())
    logo_name = re.sub(r'_+', '_', logo_name)
    
    # Construir URL del logo
    logo_url = f"{picons_base_url}{logo_name}.png"
    
    # Por simplicidad, retornamos la URL construida
    # En producción, podrías hacer una verificación con HEAD request
    return logo_url

def should_skip_group(group_title):
    """Verifica si el grupo debe ser omitido"""
    skip_groups = ['radio', 'movies', 'series', 'movie', 'serie']
    group_lower = group_title.lower()
    return any(skip in group_lower for skip in skip_groups)

def parse_m3u(content, picons_base_url):
    """Parsea el contenido M3U y genera el formato de salida"""
    lines = content.strip().split('\n')
    result = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF:'):
            # Extraer información de la línea EXTINF
            tvg_name_match = re.search(r'tvg-name="([^"]*)"', line)
            group_title_match = re.search(r'group-title="([^"]*)"', line)
            
            if tvg_name_match and group_title_match:
                title = tvg_name_match.group(1)
                group_title = group_title_match.group(1)
                
                # Verificar si debemos omitir este grupo
                if should_skip_group(group_title):
                    i += 2  # Saltar también la línea de URL
                    continue
                
                # Obtener la URL del stream (siguiente línea)
                if i + 1 < len(lines):
                    stream_url = lines[i + 1].strip()
                    
                    if stream_url.startswith('http'):
                        country_code = get_country_code(title)
                        tag = get_tag(group_title, title)
                        logo_url = get_logo_url(title, picons_base_url)
                        escaped_stream = escape_stream_url(stream_url)
                        
                        # Construir el objeto de salida
                        entry = f'''{{
Artist: "Cord"
Title: "{title}"
streamFormat: "hls|mts"
SwitchingStrategy: "full-adaptation"
Logo: "{logo_url}"
Stream: "{escaped_stream}"
Live: true
Country: "{country_code}"
Tag: "{tag}"
}}'''
                        result.append(entry)
            
            i += 2  # Saltar a la siguiente entrada EXTINF
        else:
            i += 1
    
    return '\n'.join(result)

def main():
    # URLs
    m3u_url = "http://cord-cutter.net:8080/get.php?username=19174796&password=19174796&type=m3u_plus"
    picons_base_url = "https://raw.githubusercontent.com/jsosao/Bics/main/picons/"
    no_logo_url = "https://raw.githubusercontent.com/jsosao/Bics/main/picons/no_logo.png"
    
    print("Descargando archivo M3U...")
    try:
        response = requests.get(m3u_url, timeout=30)
        response.raise_for_status()
        m3u_content = response.text
        print(f"Archivo descargado: {len(m3u_content)} caracteres")
    except Exception as e:
        print(f"Error al descargar el archivo: {e}")
        return
    
    print("Procesando contenido...")
    output_content = parse_m3u(m3u_content, picons_base_url)
    
    if not output_content:
        print("Advertencia: No se generó contenido. Creando archivo vacío.")
        output_content = "# No se encontraron entradas válidas"
    
    # Guardar en Cord.txt
    output_file = "Cord.txt"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Archivo generado exitosamente: {output_file}")
    except Exception as e:
        print(f"Error al escribir el archivo: {e}")
        return
    
    entry_count = output_content.count('Artist: "Cord"')
    print(f"Total de entradas procesadas: {entry_count}")

if __name__ == "__main__":
    main()
