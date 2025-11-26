#!/usr/bin/env python3

import urllib.request
import re
import os
import json
import unicodedata
from pathlib import Path
import base64
from datetime import datetime

# ============================================================
# CONFIGURACIÓN DE URLs (desde variables de entorno)
# ============================================================

M3U_URLS = {
    'URL_002': os.environ.get('URL_002', '')
    'URL_003': os.environ.get('URL_003', '')
    'URL_004': os.environ.get('URL_004', '')
    'URL_005': os.environ.get('URL_005', '')
    'URL_006': os.environ.get('URL_006', '')
    'URL_007': os.environ.get('URL_007', '')
    'URL_008': os.environ.get('URL_008', '')
    'URL_009': os.environ.get('URL_009', '')
    'URL_010': os.environ.get('URL_010', '')
    'URL_012': os.environ.get('URL_012', '')
    'URL_013': os.environ.get('URL_013', '')
    'URL_014': os.environ.get('URL_014', '')
    'URL_015': os.environ.get('URL_015', '')
}

# ============================================================
# CONFIGURACIÓN DE CONVERSORES OPTIMIZADA
# ============================================================

CONVERTERS = {

    # GRUPO DEPO (fusionados)
    'depo_box': {
        'env_var': 'URL_012',
        'artist': 'Box',
        'output_path': 'country/sports/depo',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'box_depo',
        'merge_group': 'depo'
    },
    'depo_pgefford': {
        'env_var': 'URL_014',
        'artist': 'Pgefford',
        'output_path': 'country/sports/depo',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'pgefford_depo',
        'merge_group': 'depo'
    },

    
    # PROCESAMIENTO MÚLTIPLE DE CORD_M3U_URL (optimizado con logos fijos)
    'cord_multi': {
        'env_var': 'URL_002',
        'artist': 'Cord',
        'output_path': 'country/country/us',
        'use_picons': False,
        'filter_type': 'multi_output',
        'outputs': {
            'abc': {
                'path': 'country/country/us/abc',
                'custom_filter': 'cord_abc',
                'fixed_logo': 'https://raw.githubusercontent.com/jsosao/Bics/main/picons/us_abc[.]png'
            },
            'cbs': {
                'path': 'country/country/us/cbs',
                'custom_filter': 'cord_cbs',
                'fixed_logo': 'https://raw.githubusercontent.com/jsosao/Bics/main/picons/us_cbs[.]png'
            },
            'nbc': {
                'path': 'country/country/us/nbc',
                'custom_filter': 'cord_nbc',
                'fixed_logo': 'https://raw.githubusercontent.com/jsosao/Bics/main/picons/us_nbc[.]png'
            },
            'fox': {
                'path': 'country/country/us/fox',
                'custom_filter': 'cord_fox',
                'fixed_logo': 'https://raw.githubusercontent.com/jsosao/Bics/main/picons/us_fox[.]png'
            }
        }
    },
    'cord': {
        'env_var': 'URL_002',
        'artist': 'Cord',
        'output_path': 'country/others/test/cord',
        'use_picons': False,
        'filter_type': 'skip_only',
        'skip_keywords': ["radio", "serie", "movie", "extra", "peliculas", "adult", "romance", "horror", "family", "science fiction", "comedy", "channel"],
    },
    '1tv': {
        'env_var': 'URL_003',
        'artist': '1tv',
        'output_path': 'country/others/test/1tv',
        'use_picons': False,
        'filter_type': 'skip_only',
        'skip_keywords': ["radio", "serie", "movie", "extra", "peliculas", "adult", "romance", "horror", "family", "science fiction", "comedy", "channel"],
    },
    
    # PROCESAMIENTO MÚLTIPLE DE PGEFFORD_M3U_URL (optimizado)
    'pgefford_mundo': {
        'env_var': 'URL_014',
        'artist': 'Pgefford',
        'output_path': 'country/country/world/pg',
        'use_picons': False,
        'filter_type': 'multi_output',
        'outputs': {
            'mx': {'path': 'country/country/world/pg/mx',
                   'include_keywords': ["lame | mexico"]},
            'usa': {'path': 'country/country/world/pg/usa',
                    'include_keywords': ["usa"]},
            'carib': {'path': 'country/country/world/pg/carib', 'include_keywords': ["lame | caribbean"]},
            'latin': {'path': 'country/country/world/pg/latin', 'include_keywords': ["lame | latino"]},
            'pe': {'path': 'country/country/world/pg/pe', 'include_keywords': ["lame | peru"]},
            'ec': {'path': 'country/country/world/pg/ec', 'include_keywords': ["lame | ecuador"]},
            'co': {'path': 'country/country/world/pg/co', 'include_keywords': ["lame | colombia"]},
            'cl': {'path': 'country/country/world/pg/cl', 'include_keywords': ["lame | chile"]},
            'ar': {'path': 'country/country/world/pg/ar', 'include_keywords': ["lame | argentina"]},
            'br': {'path': 'country/country/world/pg/br', 'include_keywords': ["lame | brazil"]},
            'ca': {'path': 'country/country/world/pg/ca', 'include_keywords': ["name | ca"]},
            'at': {'path': 'country/country/world/pg/at', 'include_keywords': ["euro | austria"]},
            'bg': {'path': 'country/country/world/pg/bg', 'include_keywords': ["euro | bulgaria"]},
            'ro': {'path': 'country/country/world/pg/ro', 'include_keywords': ["euro | romania"]},
            'be': {'path': 'country/country/world/pg/be', 'include_keywords': ["euro | belgium"]},
            'hr': {'path': 'country/country/world/pg/hr', 'include_keywords': ["euro | croatia"]},
            'de': {'path': 'country/country/world/pg/de', 'include_keywords': ["de | "]},
            'pl': {'path': 'country/country/world/pg/pl', 'include_keywords': ["pl | "]},
            'sp': {'path': 'country/country/world/pg/sp', 'include_keywords': ["es | laliga","es | deportes", "es | uefa liga de campeones", "es | entretenimiento","es | cultura","es | others","es | general","es | regionales","ppv","es | dazn acb"]},
            'pt': {'path': 'country/country/world/pg/pt', 'include_keywords': ["pt | "]},
            'ch': {'path': 'country/country/world/pg/ch', 'include_keywords': ["euro | switzerland"]},
            'cz_slo': {'path': 'country/country/world/pg/cz_slo', 'include_keywords': ["euro | cz & slovak"]},
            'nl': {'path': 'country/country/world/pg/nl', 'include_keywords': ["nl | viaplay", "nl | categorizing", "nl | netherlands"]},
            'ba': {'path': 'country/country/world/pg/ba', 'include_keywords': ["euro | bosnia"]},
            'mk': {'path': 'country/country/world/pg/mk', 'include_keywords': ["euro | macedonia"]},
            'rs': {'path': 'country/country/world/pg/rs', 'include_keywords': ["euro | serbia"]},
            'yu': {'path': 'country/country/world/pg/yu', 'include_keywords': ["euro | ex-yu"]},
            'fr': {'path': 'country/country/world/pg/fr', 'include_keywords': ["fr | di","fr | gé","fr | jeu","fr | films","fr | la na","fr | info","fr | other","fr | sport","fr | dazn","fr | canal+","fr | france"]},
            'hu': {'path': 'country/country/world/pg/hu', 'include_keywords': ["euro | hungary"]},
            'dk': {'path': 'country/country/world/pg/dk', 'include_keywords': ["euro | denmark"]},
            'no': {'path': 'country/country/world/pg/no', 'include_keywords': ["euro | norway"]},
            'al': {'path': 'country/country/world/pg/al', 'include_keywords': ["euro | albania"]},
            'ru': {'path': 'country/country/world/pg/ru', 'include_keywords': ["euro | russian"]},
            'uk': {'path': 'country/country/world/pg/uk', 'include_keywords': ["uk"]},
            'it': {'path': 'country/country/world/pg/it', 'include_keywords': ["it | italy"]},
            'tr': {'path': 'country/country/world/pg/tr', 'include_keywords': ["tr | "]},
            'gr': {'path': 'country/country/world/pg/gr', 'include_keywords': ["euro | greece"]},
            'se': {'path': 'country/country/world/pg/se', 'include_keywords': ["euro | sweden"]},
            'asia': {'path': 'country/country/world/pg/asia', 'include_keywords': ["asia", "arab"]},
            'africa': {'path': 'country/country/world/pg/africa', 'include_keywords': ["afr | "]},
        }
    },

    # PROCESAMIENTO MÚLTIPLE DE PGEFFORD_M3U_URL (optimizado)
    'vip_mundo': {
        'env_var': 'URL_015',
        'artist': 'Vip',
        'output_path': 'country/country/world/vip',
        'use_picons': False,
        'filter_type': 'multi_output',
        'outputs': {
            'mx': {'path': 'country/country/world/vip/mx',
                   'include_keywords': ["lame | mexico"]},
            'usa': {'path': 'country/country/world/vip/usa',
                    'include_keywords': ["usa | vip-a", "name | usa"]},
            'carib': {'path': 'country/country/world/vip/carib', 'include_keywords': ["lame | caribbean"]},
            'latin': {'path': 'country/country/world/vip/latin', 'include_keywords': ["lame | latino"]},
            'pe': {'path': 'country/country/world/vip/pe', 'include_keywords': ["lame | peru"]},
            'ec': {'path': 'country/country/world/vip/ec', 'include_keywords': ["lame | ecuador"]},
            'co': {'path': 'country/country/world/vip/co', 'include_keywords': ["lame | colombia"]},
            'cl': {'path': 'country/country/world/vip/cl', 'include_keywords': ["lame | chile"]},
            'ar': {'path': 'country/country/world/vip/ar', 'include_keywords': ["lame | argentina"]},
            'br': {'path': 'country/country/world/vip/br', 'include_keywords': ["lame | brazil"]},
            'ca': {'path': 'country/country/world/vip/ca', 'include_keywords': ["canada"]},
            'at': {'path': 'country/country/world/vip/at', 'include_keywords': ["eu | austria"]},
            'bg': {'path': 'country/country/world/vip/bg', 'include_keywords': ["eu | bulgaria"]},
            'ro': {'path': 'country/country/world/vip/ro', 'include_keywords': ["eu | romania"]},
            'be': {'path': 'country/country/world/vip/be', 'include_keywords': ["eu | belgium"]},
            'hr': {'path': 'country/country/world/vip/hr', 'include_keywords': ["eu | croatia"]},
            'de': {'path': 'country/country/world/vip/de', 'include_keywords': ["de | "]},
            'pl': {'path': 'country/country/world/vip/pl', 'include_keywords': ["pl | "]},
            'sp': {'path': 'country/country/world/vip/sp', 'include_keywords': ["es | laliga","es | deportes", "es | uefa liga de campeones", "es | entretenimiento","es | cultura","es | others","es | general","es | regionales","ppv","es | dazn acb"]},
            'pt': {'path': 'country/country/world/vip/pt', 'include_keywords': ["pt | "]},
            'ch': {'path': 'country/country/world/vip/ch', 'include_keywords': ["eu | switzerland"]},
            'cz_slo': {'path': 'country/country/world/vip/cz_slo', 'include_keywords': ["eu | cz & slovak"]},
            'nl': {'path': 'country/country/world/vip/nl', 'include_keywords': ["nl | "]},
            'ba': {'path': 'country/country/world/vip/ba', 'include_keywords': ["eu | bosnia"]},
            'mk': {'path': 'country/country/world/vip/mk', 'include_keywords': ["eu | macedonia"]},
            'rs': {'path': 'country/country/world/vip/rs', 'include_keywords': ["eu | serbia"]},
            'yu': {'path': 'country/country/world/vip/yu', 'include_keywords': ["eu | ex-yu","exyu | "]},
            'fr': {'path': 'country/country/world/vip/fr', 'include_keywords': ["fr | "]},
            'hu': {'path': 'country/country/world/vip/hu', 'include_keywords': ["eu | hungary"]},
            'dk': {'path': 'country/country/world/vip/dk', 'include_keywords': ["eu | denmark"]},
            'no': {'path': 'country/country/world/vip/no', 'include_keywords': ["eu | norway"]},
            'al': {'path': 'country/country/world/vip/al', 'include_keywords': ["eu | albania"]},
            'ru': {'path': 'country/country/world/vip/ru', 'include_keywords': ["eu | russian"]},
            'uk': {'path': 'country/country/world/vip/uk', 'include_keywords': ["uk"]},
            'it': {'path': 'country/country/world/vip/it', 'include_keywords': ["it | "]},
            'tr': {'path': 'country/country/world/vip/tr', 'include_keywords': ["tr | "]},
            'gr': {'path': 'country/country/world/vip/gr', 'include_keywords': ["eu | greece"]},
            'se': {'path': 'country/country/world/vip/se', 'include_keywords': ["eu | sweden"]},
            'asia': {'path': 'country/country/world/vip/asia', 'include_keywords': ["asia", "arab"]},
            'africa': {'path': 'country/country/world/vip/africa', 'include_keywords': ["afr | "]},
        }
    },
    
    # Resto de conversores individuales
    'edma': {
        'env_var': 'URL_004',
        'artist': 'Edma',
        'output_path': 'country/others/test/edma',
        'use_picons': False,
        'filter_type': 'skip_only',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "radio", "infantil", "kids"],
    },
    'fast': {
        'env_var': 'URL_005',
        'artist': 'Fast',
        'output_path': 'country/others/test/fast',
        'use_picons': False,
        'filter_type': 'skip_only',
        'skip_keywords': ["canales-adultos", "adultos", "series", "telenovelas", "vod", "pluto", "doramas", "simpsons", "radio", "cgates", "24/7", "geo chile", "música","cinema ppv usa","rakuten esp","indonesia"],
    },
    'latin': {
        'env_var': 'URL_006',
        'artist': 'Play',
        'output_path': 'country/country/latino/latin_auto',
        'use_picons': False,
        'filter_type': 'include_exclude',
        'skip_keywords': ["24/7", "247", "infantiles", "musica"],
        'include_keywords': ["canales", "canales de peliculas"]
    },
    'proyecto': {
        'env_var': 'URL_007',
        'artist': 'Proyecto',
        'output_path': 'country/others/test/proy',
        'use_picons': False,
        'filter_type': 'include_exclude',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "radio", "religiosos", "infantil", "kids", "vod","novelas-", "estrenos", "24/7", "247", "musica"],
        'include_keywords': ["canales-novelas", "canales-cine y series","canales","cinema", "ecuador", "eventos"]
    },
    'kids': {
        'env_var': 'URL_007',
        'artist': 'Proyecto',
        'output_path': 'country/others/kids',
        'use_picons': False,
        'filter_type': 'include_exclude',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "radio", "religiosos", "vod", "serie", "novelas-", "estrenos", "24/7", "247", "musica"],
        'include_keywords': ["canales-infantiles", "kids"]
    },
    'zap': {
        'env_var': 'URL_008',
        'artist': 'Zapp',
        'output_path': 'country/others/test/zap',
        'use_picons': False,
        'filter_type': 'skip_only',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "porn", "canales-religiosos", "canales-musica", "vod", "navidad", "estrenos", "novelas", "24/7","series-"],
    },
    'zona': {
        'env_var': 'URL_010',
        'artist': 'Zona',
        'output_path': 'country/others/test/zona',
        'use_picons': False,
        'filter_type': 'skip_only',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "porn","xxx","infantiles","kids", "musica","pack","24/7","religiosos", "vod","autonomicos","coleccion", "serie","novelas", "doramas", "tv shows","saga","retro","super estrenos","pedidos","movies","cine","cursos","netflix","cuerpo","estrenos hdcam","4k premium","pruebas","instat","canada","usa noticias","usa entretenimiento","usa sport", "usa network", "documentales", "uk", "tv españa", "españa tdt", "tv republica dominicana", "tv nicaragua", "tv bolivia", "tv paraguay", "tv costa rica", "tv el salvador", "tv honduras", "tv cuba", "tv argentina", "tv venezuela", "tv ecuador", "tv uruguay", "tv colombia", "tv peru", "tv guatemala", "tv puerto rico", "tv chile", "regionales", "tv italia", "tv panamá"],
    },
    'gama': {
        'env_var': 'URL_009',
        'artist': 'Gama',
        'output_path': 'country/others/test/gama',
        'use_picons': False,
        'filter_type': 'skip_only',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "porn", "radio", "vod", "vod-", "*vod", "accion", "se-", "se ","western", "telenovelas","mus♪ca☊", "infantil", "24/7"],
    },
    'box': {
        'env_var': 'URL_012',
        'artist': 'Box',
        'output_path': 'country/others/test/box',
        'use_picons': False,
        'filter_type': 'skip_only',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "porn", "radio"],
    },
    'lunar': {
        'env_var': 'URL_013',
        'artist': 'Lunar',
        'output_path': 'country/others/test/lunar',
        'use_picons': False,
        'filter_type': 'skip_only',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "porn", "radio","24/7","247","tv shows","music"],
    }
}

# ============================================================
# FILTROS PERSONALIZADOS (OPTIMIZACIÓN)
# ============================================================

CUSTOM_FILTERS = {
    'alfa_eventos': lambda group, title: "(eventos)" in group.lower() or "cielo sport" in title.lower() or "cielo evento" in title.lower(),
    'pass_eventos': lambda group, title: any(x in group.lower() for x in ["nba", "nhl", "nfl", "mlb", "ncaaf"]),
    'alfa_fox': lambda group, title: any(x in title.lower() for x in ["fox sports", "fox deportes", "fox soccer", "foxone"]),
    'alfa_espn': lambda group, title: "espn" in title.lower(),
    'alfa_tudn': lambda group, title: "tudn" in title.lower(),    
    'alfa_tu': lambda group, title: any(x in title.lower() for x in ["telemundo", "univision", "nbc universo", "unimas", "galavision"]),
    'alfa_cartelera_2025': lambda group, title: any(x in group.lower() for x in ["cartelera 2025"]),
    'alfa_depo': lambda group, title: "deportes" in group.lower(),
}

# ============================================================
# VARIABLES GLOBALES
# ============================================================

default_logo = "https://raw.githubusercontent.com/jsosao/Bics/main/picons/no_logo[.]png"
picons_base_url = "https://raw.githubusercontent.com/jsosao/Bics/main/picons/"
picons_cache = None
m3u_cache = {}

# Crear diccionario invertido para búsqueda rápida
VARIATION_TO_CANONICAL = {}
for canonical, variations in EQUAL_NAMES.items():
    for variation in variations:
        VARIATION_TO_CANONICAL[variation.lower()] = canonical

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def normalize_text(text):
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\.', ' ', text.strip())
    text = re.sub(r'[^\w\s&!:@]', '', text)
    text = re.sub(r'^\d+\.?\s*', '', text)
    return text

def get_github_directory_contents(api_url):
    try:
        req = urllib.request.Request(api_url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
            return []
    except Exception as e:
        print(f"⚠ Error al obtener contenido: {e}")
        return []

def scan_directory_recursive(path=""):
    api_url = f"https://api.github.com/repos/jsosao/Bics/contents/picons{path}"
    contents = get_github_directory_contents(api_url)
    logos = []
    
    for item in contents:
        if item['type'] == 'file' and item['name'].endswith('[.]png'):
            logo_url = picons_base_url + path.lstrip('/') + ('/' if path else '') + item['name']
            logo_name = item['name'].replace('[.]png', '')
            logos.append({
                'name': logo_name,
                'normalized_name': normalize_text(logo_name),
                'url': logo_url,
                'path': path
            })
        elif item['type'] == 'dir' and item['name'] not in ['country']:
            subfolder_path = path + '/' + item['name']
            logos.extend(scan_directory_recursive(subfolder_path))
    return logos

def get_picons_list():
    global picons_cache
    if picons_cache is not None:
        return picons_cache
    
    try:
        print("📦 Escaneando repositorio de logos...")
        picons_cache = scan_directory_recursive()
        #print(f"✓ Se encontraron {len(picons_cache)} picons disponibles\n")
        return picons_cache
    except Exception as e:
        print(f"⚠ No se pudo obtener la lista de picons: {e}")
        return []

def download_m3u(url, env_var):
    global m3u_cache
    
    if env_var in m3u_cache:
        print(f"♻️ Usando versión en caché de {env_var}")
        return m3u_cache[env_var]
    
    try:
        print(f"⬇️ Descargando {env_var}...")
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
        m3u_cache[env_var] = content
        print(f"✓ Descargado exitosamente\n")
        return content
    except Exception as e:
        print(f"✗ Error al descargar: {e}\n")
        return None

def replace_country_codes(text):
    reemplazos = {
        "MEX": "mx", "ARG": "ar", "SUR": "ar", 
        "COL": "co", "USA": "us", "BRA": "br",
        "CHILE": "cl", "PER": "pe", "URU": "uy"
    }
    for codigo_largo, codigo_corto in reemplazos.items():
        text = re.sub(re.escape(codigo_largo), codigo_corto, text, flags=re.IGNORECASE)
    return text

def get_country(title):
    return "us"

def get_tag(group_title):
    return group_title.lower()

def should_skip_channel(group_title, channel_title, config, output_name=None):
    group_lower = group_title.lower()
    title_lower = channel_title.lower()

    # Filtros personalizados
    if config['filter_type'] == 'custom':
        filter_name = config.get('custom_filter')
        if filter_name and filter_name in CUSTOM_FILTERS:
            return not CUSTOM_FILTERS[filter_name](group_title, channel_title)
        return True
    
    # Multi-output con filtro específico por salida
    if config['filter_type'] == 'multi_output' and output_name:
        output_config = config['outputs'].get(output_name, {})
        
        # Si tiene custom_filter
        if 'custom_filter' in output_config:
            filter_name = output_config['custom_filter']
            if filter_name in CUSTOM_FILTERS:
                return not CUSTOM_FILTERS[filter_name](group_title, channel_title)
        
        # Si tiene include_keywords
        if 'include_keywords' in output_config:
            return not any(keyword in group_lower for keyword in output_config['include_keywords'])
        
        return True

    if config['filter_type'] == 'include_exclude':
        has_include = any(keyword in group_lower for keyword in config.get('include_keywords', []))
        has_skip = any(keyword in group_lower for keyword in config.get('skip_keywords', []))
        return not (has_include and not has_skip)

    if config['filter_type'] == 'include_only':
        return not any(keyword in group_lower for keyword in config.get('include_keywords', []))

    if config['filter_type'] == 'skip_only':
        return any(keyword in group_lower for keyword in config.get('skip_keywords', []))
    
    return False

def escape_url(url):
    url = url.replace("http://", "http[:[/][/]]")
    url = url.replace("https://", "https[:[/][/]]")
    url = url.replace(".", "[.]")
    url = url.replace("/", "[/]")
    return url

def validate_entry(title, stream_url, tvg_logo):
    """Valida que los datos del canal sean correctos"""
    
    if not title or title.strip() == "":
        return False, "Title vacío"
    
    if not stream_url or stream_url.strip() == "":
        return False, "Stream vacío"
    
    if not stream_url.startswith(('http://', 'https://')):
        return False, "Stream no es URL válida"
    
    if tvg_logo and "base64" in tvg_logo.lower():
        return False, "Logo base64 no soportado"
    
    if tvg_logo and len(tvg_logo) > 500:
        return False, "Logo demasiado largo"
    
    if len(title) > 100:
        return False, "Title demasiado largo"
    
    dangerous_patterns = ['javascript:', 'data:', 'file://', 'ftp://']
    if any(pattern in stream_url.lower() for pattern in dangerous_patterns):
        return False, "Stream con protocolo peligroso"
    
    invalid_chars = ['{', '}']
    if any(char in stream_url for char in invalid_chars):
        return False, "Caracteres inválidos en URL"
    
    return True, ""

def process_m3u_content(content, config, converter_name, picons_list, output_name=None):
    """Procesa contenido M3U con soporte para multi-output"""
    
    lines = content.strip().split('\n')
    entries = []
    skipped_count = 0
    logos_original = 0
    logos_found = 0
    logos_default = 0
    logos_in_title = 0
    logos_fixed = 0
    invalid_count = 0
    
    # Determinar configuración de salida
    #use_picons = config.get('use_picons', False)
    #fixed_logo = None
    
    if output_name and config['filter_type'] == 'multi_output':
        output_config = config['outputs'].get(output_name, {})
        #use_picons = output_config.get('use_picons', use_picons)
        fixed_logo = output_config.get('fixed_logo')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF:'):
            tvg_name_match = re.search(r'tvg-name="([^"]*)"', line)
            tvg_logo_match = re.search(r'tvg-logo="([^"]*)"', line)
            group_title_match = re.search(r'group-title="([^"]*)"', line)
            title_match = re.search(r',(.*)$', line)
            
            tvg_name = tvg_name_match.group(1) if tvg_name_match else ""
            tvg_logo = tvg_logo_match.group(1) if tvg_logo_match else ""
            group_title = group_title_match.group(1) if group_title_match else ""
            title = title_match.group(1).strip() if title_match else tvg_name
            original_title = title
            title = normalize_text(title)
            
            i += 1
            if i < len(lines):
                stream_url = lines[i].strip()
                
                if should_skip_channel(group_title, original_title, config, output_name):
                    skipped_count += 1
                    i += 1
                    continue

                # Validar entrada
                is_valid, error_msg = validate_entry(title, stream_url, tvg_logo)
                if not is_valid:
                    invalid_count += 1
                    i += 1
                    continue
                
                final_logo = default_logo

                entry = {
                    'Artist': config['artist'],
                    'Title': title,
                    'streamFormat': 'hls|mts',
                    'SwitchingStrategy': 'full-adaptation',
                    'Logo': final_logo.replace("{", "").replace("}", ""),
                    'Stream': escape_url(stream_url),
                    'Live': True,
                    'Country': get_country(title),
                    'Tag': get_tag(group_title)
                }
                entries.append(entry)
        
        i += 1
    
    return entries, skipped_count, logos_original, logos_found, logos_default, logos_in_title, logos_fixed, invalid_count

def generate_output(entries):
    output_lines = []
    for entry in entries:
        output_lines.append('{')
        output_lines.append(f'    Artist: "{entry["Artist"]}"')
        output_lines.append(f'    Title: "{entry["Title"]}"')
        output_lines.append(f'    streamFormat: "{entry["streamFormat"]}"')
        output_lines.append(f'    SwitchingStrategy: "{entry["SwitchingStrategy"]}"')
        output_lines.append(f'    Logo: "{entry["Logo"]}"')
        output_lines.append(f'    Stream: "{entry["Stream"]}"')
        output_lines.append(f'    Live: {str(entry["Live"]).lower()}')
        output_lines.append(f'    Country: "{entry["Country"]}"')
        output_lines.append(f'    Tag: "{entry["Tag"]}"')
        output_lines.append('}')
    
    return '\n'.join(output_lines)

def save_output(output_path, output_content):
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    github_uploaded = False
    return True

def main():
    """Ejecuta todos los conversores configurados (modo GitHub Actions)"""
    
    print("\n" + "="*60)
    print("UNIFIED CONVERTER - GITHUB ACTIONS MODE")
    print("="*60 + "\n")
    
    # Filtrar URLs configuradas
    configured_urls = {k: v for k, v in M3U_URLS.items() if v and v.strip()}
    
    if not configured_urls:
        print("\n✗ ERROR: No hay URLs configuradas en las variables de entorno")
        return 1
    
    print(f"📥 URLs configuradas: {len(configured_urls)}\n")
    
    # Descargar todas las URLs necesarias
    for env_var, url in configured_urls.items():
        download_m3u(url, env_var)
    
    ## Obtener picons si algún conversor los necesita
    #picons_list = []
    #needs_picons = any(config.get('use_picons', False) or 
    #                  (config.get('filter_type') == 'multi_output' and 
    #                   any(out.get('use_picons', False) for out in config.get('outputs', {}).values()))
    #                  for config in CONVERTERS.values())
    #if needs_picons:
    #    picons_list = get_picons_list()
    
    # Agrupar conversores
    merge_groups = {}
    multi_output_converters = {}
    standalone_converters = {}
    
    for converter_name, config in CONVERTERS.items():
        # Solo procesar si la URL está configurada
        if config['env_var'] not in configured_urls:
            continue
            
        merge_group = config.get('merge_group')
        if merge_group:
            if merge_group not in merge_groups:
                merge_groups[merge_group] = []
            merge_groups[merge_group].append((converter_name, config))
        elif config.get('filter_type') == 'multi_output':
            multi_output_converters[converter_name] = config
        else:
            standalone_converters[converter_name] = config
    
    successful = 0
    failed = 0
    
    # ========================================
    # PROCESAR GRUPOS DE FUSIÓN
    # ========================================
    for merge_group, converters in merge_groups.items():
        try:
            print(f"{'='*60}")
            print(f"🔗 GRUPO DE FUSIÓN: {merge_group.upper()}")
            print(f"{'='*60}")
            
            all_entries = []
            total_skipped = 0
            total_orig = 0
            total_found = 0
            total_default = 0
            total_in_title = 0
            total_fixed = 0
            total_invalid = 0
            
            for converter_name, config in converters:
                #print(f"\n  📦 Procesando: {converter_name} - {config['artist']}")
                
                env_var = config['env_var']
                content = m3u_cache.get(env_var)
                
                if not content:
                    print(f"  ✗ No se pudo obtener contenido de {env_var}")
                    continue
                
                entries, skipped, orig, found, default, in_title, fixed, invalid = process_m3u_content(
                    content, config, converter_name, picons_list
                )
                
                all_entries.extend(entries)
                total_skipped += skipped
                total_orig += orig
                total_found += found
                total_default += default
                total_in_title += in_title
                total_fixed += fixed
                total_invalid += invalid
                
                print(f"  ✓ Canales obtenidos: {len(entries)} | Omitidos: {skipped} | Inválidos: {invalid}")
            
            if not all_entries:
                print(f"\n⚠ No se generaron entradas para el grupo {merge_group}\n")
                failed += 1
                continue
            
            output_content = generate_output(all_entries)
            output_config = converters[0][1]
            save_output(output_config['output_path'], output_content)
            
            print(f"\n{'='*60}")
            print(f"✓ Ruta fusionada: {output_config['output_path']}")
            print(f"✓ Total de canales fusionados: {len(all_entries)} | Total omitidos: {total_skipped}")
            
            total = len(all_entries) if all_entries else 1
            stats = f"📊 Logos - "
            if total_fixed > 0:
                stats += f"Fijos: {total_fixed} ({total_fixed*100//total}%) | "
            if total_in_title > 0:
                stats += f"Por título: {total_in_title} ({total_in_title*100//total}%) | "
            if output_config.get('use_picons'):
                stats += f"Encontrados: {total_found} ({total_found*100//total}%) | "
            stats += f"Originales: {total_orig} ({total_orig*100//total}%) | Default: {total_default} ({total_default*100//total}%)"
            print(stats)
            print()
            
            successful += 1
            
        except Exception as e:
            print(f"\n✗ Error procesando grupo {merge_group}: {e}\n")
            failed += 1
            continue
    
    # ========================================
    # PROCESAR CONVERSORES MULTI-OUTPUT
    # ========================================
    for converter_name, config in multi_output_converters.items():
        try:
            print(f"{'='*60}")
            print(f"🔀 MULTI-OUTPUT: {converter_name.upper()} - {config['artist']}")
            print(f"{'='*60}")
            print(f"  Generando {len(config['outputs'])} salidas desde una sola fuente\n")
            
            env_var = config['env_var']
            content = m3u_cache.get(env_var)
            
            if not content:
                print(f"✗ No se pudo obtener contenido de {env_var}\n")
                failed += 1
                continue
            
            outputs_generated = 0
            
            for output_name, output_config in config['outputs'].items():
                #print(f"  📁 Procesando salida: {output_name}")
                
                entries, skipped, orig, found, default, in_title, fixed, invalid = process_m3u_content(
                    content, config, converter_name, picons_list, output_name
                )
                
                if not entries:
                    print(f"    ⚠ Sin entradas para {output_name}")
                    continue
                
                output_content = generate_output(entries)
                output_path = output_config['path']
                save_output(output_path, output_content)
                
                print(f"    ✓ Ruta: {output_path}")
                print(f"    ✓ Canales: {len(entries)} | Omitidos: {skipped} | Inválidos: {invalid}")
                
                total = len(entries) if entries else 1
                stats = f"    📊 Logos - "
                if fixed > 0:
                    stats += f"Fijos: {fixed} ({fixed*100//total}%) | "
                if in_title > 0:
                    stats += f"Por título: {in_title} ({in_title*100//total}%) | "
                if output_config.get('use_picons', config.get('use_picons', False)):
                    stats += f"Encontrados: {found} ({found*100//total}%) | "
                stats += f"Originales: {orig} ({orig*100//total}%) | Default: {default} ({default*100//total}%)"
                print(stats)
                print()
                
                outputs_generated += 1
            
            if outputs_generated > 0:
                print(f"✓ {outputs_generated}/{len(config['outputs'])} salidas generadas exitosamente\n")
                successful += 1
            else:
                print(f"✗ No se generó ninguna salida\n")
                failed += 1
            
        except Exception as e:
            print(f"\n✗ Error procesando {converter_name}: {e}\n")
            failed += 1
            continue
    
    # ========================================
    # PROCESAR CONVERSORES INDEPENDIENTES
    # ========================================
    for converter_name, config in standalone_converters.items():
        try:
            print(f"{'='*60}")
            print(f"📄 {converter_name.upper()} - {config['artist']}")
            print(f"{'='*60}")
            
            env_var = config['env_var']
            content = m3u_cache.get(env_var)
            
            if not content:
                print(f"✗ No se pudo obtener contenido de {env_var}\n")
                failed += 1
                continue
            
            entries, skipped, orig, found, default, in_title, fixed, invalid = process_m3u_content(
                content, config, converter_name, picons_list
            )
            
            if not entries:
                print(f"⚠ No se generaron entradas para {converter_name}\n")
                failed += 1
                continue
            
            output_content = generate_output(entries)
            save_output(config['output_path'], output_content)
            
            print(f"\n✓ Ruta: {config['output_path']}")
            print(f"✓ Canales: {len(entries)} | Omitidos: {skipped} | Inválidos: {invalid}")
            
            total = len(entries) if entries else 1
            stats = f"📊 Logos - "
            if fixed > 0:
                stats += f"Fijos: {fixed} ({fixed*100//total}%) | "
            if in_title > 0:
                stats += f"Por título: {in_title} ({in_title*100//total}%) | "
            if config.get('use_picons'):
                stats += f"Encontrados: {found} ({found*100//total}%) | "
            stats += f"Originales: {orig} ({orig*100//total}%) | Default: {default} ({default*100//total}%)"
            print(stats)
            
            print()
            successful += 1
            
        except Exception as e:
            print(f"\n✗ Error procesando {converter_name}: {e}\n")
            failed += 1
            continue
    
    # ========================================
    # RESUMEN FINAL
    # ========================================
    print("="*60)
    print("✓ CONVERSIÓN COMPLETADA")
    print("="*60)
    print(f"Exitosos: {successful} | Fallidos: {failed}")
    print(f"Descargas de M3U realizadas: {len(configured_urls)}")
    print("="*60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    main()
