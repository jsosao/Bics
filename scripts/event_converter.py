#!/usr/bin/env python3

import urllib.request
import re
import os
import json
import unicodedata
from pathlib import Path
import base64
from datetime import datetime
from datetime import timedelta

# Al inicio del script, crear una única timestamp para toda la ejecución
EXECUTION_TIMESTAMP = (datetime.now() - timedelta(hours=6)).strftime('%d-%m-%Y %H:%M:%S')

# ============================================================
# CONFIGURACIÓN DE URLs (desde variables de entorno)
# ============================================================

M3U_URLS = {
    'URL_001': os.environ.get('URL_001', ''),
    'URL_002': os.environ.get('URL_002', ''),
    'URL_011': os.environ.get('URL_011', '')
}

# ============================================================
# ASIGNACIÓN ÚNICA DE VARIACIONES DE TITULOS EN STREAM
# ============================================================

EQUAL_NAMES = {
    "sunday_ticket": ["sunday ticket", "nfl sunday ticket"],
    "nba": ["nba", "brooklyn nets", "charlotte hornets", "cleveland cavaliers", "new york knicks", "miami heat", "orlando magic", "toronto raptors",
            "atlanta hawks", "philadelphia 76ers", "boston celtics", "detroit pistons", "chicago bulls", "new orleans pelicans", "memphis grizzlies",
            "washington wizards", "milwaukee bucks", "los angeles clippers", "utah jazz", "san antonio spurs", "dallas mavericks", "sacramento kings",
            "phoenix suns", "minnesota timberwolves", "portland trail blazers","golden state warriors"],
    "mlb": ["mlb"],
    "nhl": ["nhl","chicago blackhawks","seattle kraken","sacramento kings","denver nuggets","vancouver canucks","nashville predators",
            "edmonton oilers","st louis blues","pittsburgh penguins","toronto maple leafs","winnipeg jets","los angeles kings","detroit red wings",
            "vegas golden knights","florida panthers","anaheim ducks","tampa bay lightning","colorado avalanche","boston bruins","new york islanders",
            "utah mammoth","buffalo sabres","carolina hurricanes","new york rangers","philadelphia flyers","montreal canadiens","columbus blue jackets","calgary flames"],
    "ufc": ["ufc"],
    "wwe": ["wwe"],
    "f1": ["formula 1", "^f1 ", "fórmula f1"],    
    "sky_sports": ["cielo sport","sky","cielo evento"],
    "mls": ["mls"],    
    "liga_femenil_mx": ["liga femenil mx", "fem mx", "mx fem", "liga_femenil_mx", "liga mx fem"],
    "liga mx": ["liga mx", "mx liga", "ligamx", "mxliga", "pachuca", "tigres uanl", "queretaro fc", "cd guadalajara", "atlas fc", "club leon",
                "club tijuana", "cd toluca", "pumas unam", "atletico san luis"],
    "lmp": ["lmp", "lmp_"],
    "lmb": ["lmb"],
    "liga_expansion_mx": ["expansión mx", "exp mx"],
    "epl": ["premier league", "epl "],
    "serie_a": ["serie a", "seriea"],
    "ligue_1": ["ligue 1", "ligue1"],
    "bundesliga": ["bundesliga"],
    "la_liga_smartbank": ["laliga smartbank"],
    "la_liga": ["laliga","laligaes"],    
    "ucl_women": ["ucl women","champions league women"],
    "afc": ["afc ","afc champions", "afc champions league"],        
    "ucl": ["ucl ","champions league"],
    "uel": ["uefa europa","uel ","europa league"],
    "efl": ["efl ", "efl cup"],
    "dfb": ["dfb_pokal"],
    "sudamericana": ["sudamericana"],
    "libertadores": ["libertadores"],
    "championship": ["championship"],
    "caribbean_cup": ["concacaf caribbean cup", "copa del caribe"],
    "eredivisie": ["eredivisie"],
    "argentina": ["argentina","arg "],
    "colombia": ["colombia","col "],
    "ecuador": ["ecuador","ecu "],
    "chile": ["chile ", "cl "],
    "honduras": ["honduras "],
    "guatemala": ["guatemala "],
    "costa rica": ["costa rica ", "cr "],
    "brasileirão": ["brasileirão"],
    "uruguay": ["uruguay"],
    "el salvador": ["el salvador"],
    "perú": ["perú"],
    "saudi": ["saudi "],
    "polonia": ["polonia"],
    "portugal": ["portugal", "pt "],
    "amistoso": ["amistoso"]
}

# ============================================================
# PATH DE LOGOS A CAMBIAR
# ============================================================

IN_TITLE_LOGOS = {
    "sunday_ticket": "https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nfl_sundayticket[.]png",
    "nba": "https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nba[.]png",
    "mlb": "https://raw.githubusercontent.com/jsosao/bics/main/picons/us_mlb[.]png",
    "ufc": "https://raw.githubusercontent.com/jsosao/bics/main/picons/us_ufc_fight_pass[.]png",
    "nhl": "https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nhl[.]png",
    "wwe": "https://raw.githubusercontent.com/jsosao/bics/main/picons/us_wwe_network[.]png",
    "sky_sports": "https://raw.githubusercontent.com/jsosao/bics/main/picons/mx_sky_sports[.]png",
    "liga_femenil_mx": "https://raw.githubusercontent.com/jsosao/bics/main/picons/mx_liga_femenil_mx[.]png",
    "liga mx": "https://raw.githubusercontent.com/jsosao/bics/main/picons/mx_liga_mx[.]png",
    "lmp": "https://raw.githubusercontent.com/jsosao/bics/main/picons/mx_beisbol_lmp[.]png",
    "lmb": "https://raw.githubusercontent.com/jsosao/bics/main/picons/mx_beisbol_lmb[.]png",
    "liga_expansion_mx": "https://raw.githubusercontent.com/jsosao/bics/main/picons/mx_expansion_mx[.]png",
    "epl": "https://raw.githubusercontent.com/jsosao/bics/main/picons/uk_premier_league[.]png",
    "efl": "https://raw.githubusercontent.com/jsosao/bics/main/picons/uk_efl_football_league[.]png",
    "serie_a": "https://raw.githubusercontent.com/jsosao/bics/main/picons/it_serie_a[.]png",
    "la_liga_smartbank": "https://raw.githubusercontent.com/jsosao/bics/main/picons/sp_la_liga_smartbank[.]png",
    "la_liga": "https://raw.githubusercontent.com/jsosao/bics/main/picons/sp_la_liga[.]png",
    "bundesliga": "https://raw.githubusercontent.com/jsosao/bics/main/picons/de_bundesliga[.]png",
    "ligue_1": "https://raw.githubusercontent.com/jsosao/bics/main/picons/fr_ligue_1[.]png",
    "mls": "https://raw.githubusercontent.com/jsosao/bics/main/picons/us_mls[.]png",
    "f1": "https://raw.githubusercontent.com/jsosao/bics/main/picons/us_f1[.]png",
    "ucl_women": "https://raw.githubusercontent.com/jsosao/bics/main/picons/uefa_women_champions[.]png",
    "ucl": "https://raw.githubusercontent.com/jsosao/bics/main/picons/uefa_champions[.]png",
    "afc": "https://raw.githubusercontent.com/jsosao/bics/main/picons/afc_champions[.]png",
    "uel": "https://raw.githubusercontent.com/jsosao/bics/main/picons/uel_champions[.]png",
    "dfb": "https://raw.githubusercontent.com/jsosao/bics/main/picons/po_dfb_pokal[.]png",
    "sudamericana": "https://raw.githubusercontent.com/jsosao/bics/main/picons/conmebol_sudamericana[.]png",
    "libertadores": "https://raw.githubusercontent.com/jsosao/bics/main/picons/conmebol_libertadores[.]png",
    "caribbean cup": "https://raw.githubusercontent.com/jsosao/bics/main/picons/concacaf_caribbean_cup[.]png",
    "championship": "https://raw.githubusercontent.com/jsosao/bics/main/picons/uk_championship_epl[.]png",  
    "eredivisie": "https://raw.githubusercontent.com/jsosao/bics/main/picons/nl_eredivise[.]png",
    "ecuador": "https://raw.githubusercontent.com/jsosao/bics/main/picons/ec_liga_pro[.]png",
    "colombia": "https://raw.githubusercontent.com/jsosao/bics/main/picons/co_dimayor[.]png",
    "chile": "https://raw.githubusercontent.com/jsosao/bics/main/picons/cl_liga_futbol[.]png",
    "argentina": "https://raw.githubusercontent.com/jsosao/bics/main/picons/ar_primera_nacional[.]png",
    "el salvador": "https://raw.githubusercontent.com/jsosao/bics/main/picons/sv_primera_division[.]png",
    "honduras": "https://raw.githubusercontent.com/jsosao/bics/main/picons/hn_primera_division[.]png",
    "guatemala": "https://raw.githubusercontent.com/jsosao/bics/main/picons/gt_primera_division[.]png",
    "costa rica": "https://raw.githubusercontent.com/jsosao/bics/main/picons/cr_promerica[.]png",
    "brasileirão": "https://raw.githubusercontent.com/jsosao/bics/main/picons/br_brasileirao[.]png",
    "uruguay": "https://raw.githubusercontent.com/jsosao/bics/main/picons/uy_primera_division[.]png",
    "perú": "https://raw.githubusercontent.com/jsosao/bics/main/picons/pe_primera_division[.]png",
    "saudi": "https://raw.githubusercontent.com/jsosao/bics/main/picons/sa_primera_division[.]png",
    "polonia": "https://raw.githubusercontent.com/jsosao/bics/main/picons/pl_primera_division[.]png",
    "portugal": "https://raw.githubusercontent.com/jsosao/bics/main/picons/pt_primera_division[.]png",
    "amistoso": "https://raw.githubusercontent.com/jsosao/bics/main/picons/us_fifa_amistoso[.]png"    
}

# ============================================================
# CONFIGURACIÓN DE CONVERSORES OPTIMIZADA
# ============================================================

CONVERTERS = {
    # GRUPO EVENTOS (fusionados)
    'alfa_eventos': {
        'env_var': 'URL_001',
        'artist': 'Alfa',
        'category_name': 'Eventos',        
        'output_path': 'country/sports/sections/sports',
        'use_picons': True,
        'filter_type': 'custom',
        'custom_filter': 'alfa_eventos',
        'merge_group': 'sections_sports'
    },
#    'pass_eventos': {
#        'env_var': 'URL_011',
#        'artist': 'Pass',
#        'category_name': 'Eventos',    
#        'output_path': 'country/sports/sections/sports',
#        'use_picons': True,
#        'filter_type': 'custom',
#        'custom_filter': 'pass_eventos',
#        'merge_group': 'sections_sports'
#    },

    # FUSION DE EVENTOS DEPORTIVOS
    'alfa_nba': {
        'env_var': 'URL_001',
        'artist': 'Alfa',
        'category_name': 'NBA',        
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'alfa_nba',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nba[.]png',                
        'merge_group': 'sections_sports'
    },
    'pass_nba': {
        'env_var': 'URL_011',
        'artist': 'Pass',
        'category_name': 'NBA',
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'pass_nba',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nba[.]png',                        
        'merge_group': 'sections_sports'
    },
    'cord_nba': {
        'env_var': 'URL_002',
        'artist': 'Cord',
        'category_name': 'NBA',        
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'cord_nba',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nba[.]png',                        
        'merge_group': 'sections_sports'
    },
    'alfa_nfl': {
        'env_var': 'URL_001',
        'artist': 'Alfa',
        'category_name': 'NFL',        
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'alfa_nfl',
        'merge_group': 'sections_sports'
    },
    'pass_nfl': {
        'env_var': 'URL_011',
        'artist': 'Pass',
        'category_name': 'NFL',        
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'pass_nfl',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nfl_sundayticket[.]png',                        
        'merge_group': 'sections_sports'
    },  
    'cord_nfl': {
        'env_var': 'URL_002',
        'artist': 'Cord',
        'category_name': 'NFL',        
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'cord_nfl',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nfl_gamepass[.]png',                        
        'merge_group': 'sections_sports'
    },      
    'alfa_mlb': {
        'env_var': 'URL_001',
        'artist': 'Alfa',
        'category_name': 'MLB',        
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'alfa_mlb',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_mlb[.]png',                        
        'merge_group': 'sections_sports'
    },
    'pass_mlb': {
        'env_var': 'URL_011',
        'artist': 'Pass',
        'category_name': 'MLB',        
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'pass_mlb',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_mlb[.]png',                                
        'merge_group': 'sections_sports'
    },    
    'cord_mlb': {
        'env_var': 'URL_002',
        'artist': 'Cord',
        'category_name': 'MLB',        
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'cord_mlb',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_mlb[.]png',                                
        'merge_group': 'sections_sports'
    },     
    'pass_nhl': {
        'env_var': 'URL_011',
        'artist': 'Pass',
        'category_name': 'NHL',                
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'pass_nhl',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nhl[.]png',                                
        'merge_group': 'sections_sports'
    },    
    'cord_nhl': {
        'env_var': 'URL_002',
        'artist': 'Cord',
        'category_name': 'NHL',                      
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'cord_nhl',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nhl[.]png',                                
        'merge_group': 'sections_sports'
    },     
   'pass_ncaaf': {
        'env_var': 'URL_011',
        'artist': 'Pass',
        'category_name': 'NCAAF',                      
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'pass_ncaaf',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_ncaaf[.]png',                                
        'merge_group': 'sections_sports'
    },    
    'cord_ncaaf': {
        'env_var': 'URL_002',
        'artist': 'Cord',
        'category_name': 'NCAAF',                             
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'cord_ncaaf',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_ncaaf[.]png',                                
        'merge_group': 'sections_sports'
    },     

   'pass_ppv': {
        'env_var': 'URL_011',
        'artist': 'Pass',
        'category_name': 'PPV',                             
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'pass_ppv',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_ppv[.]png',                                
        'merge_group': 'sections_sports'
    },    
    'cord_ppv': {
        'env_var': 'URL_002',
        'artist': 'Cord',
        'category_name': 'PPV',                                    
        'output_path': 'country/sports/sections/sports',
        'use_picons': False,
        'filter_type': 'custom',
        'custom_filter': 'cord_ppv',
        'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_ppv[.]png',                                
        'merge_group': 'sections_sports'
    },     
    
    # PROCESAMIENTO MÚLTIPLE DE URL_001 (optimizado)
    'alfa_sports': {
        'env_var': 'URL_001',
        'artist': 'Alfa',
        'output_path': 'country/sports',
        'use_picons': True,
        'filter_type': 'multi_output',
        'outputs': {
            'fox': {
                'path': 'country/sports/fox',
                'custom_filter': 'alfa_fox'
            },
            'fox_1': {
                'path': 'country/sports/fox_1',
                'custom_filter': 'alfa_fox_1'
            },
            'espn': {
                'path': 'country/sports/espn',
                'custom_filter': 'alfa_espn'
            },
            'tudn': {
                'path': 'country/sports/tudn',
                'custom_filter': 'alfa_tudn'
            },            
            't_u': {
                'path': 'country/country/tu/t_u_auto',
                'custom_filter': 'alfa_tu'
            },
            'alfa_sky': {
                'path': 'country/sports/sections/sky',
                'custom_filter': 'alfa_sky'
            },
            
            'cartelera_2025': {
                'path': 'country/others/cinema/cartelera_2025',
                'use_picons': False,
                'custom_filter': 'alfa_cartelera_2025'
            },
            'depo': {
                'path': 'country/sports/depo',
                'use_picons': False,
                'custom_filter': 'alfa_depo',
                'merge_group': 'depo'
            }
        }
    },

    # PROCESAMIENTO MÚLTIPLE DE URL_002 (optimizado)
    'cord_sports': {
        'env_var': 'URL_002',
        'artist': 'Cord',
        'output_path': 'country/sports',
        'use_picons': False,
        'filter_type': 'multi_output',
        'outputs': {
            'pass_ncaab': {
                'path': 'country/sports/sections/ncaab',
                'custom_filter': 'cord_ncaab',
                'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_ncaab[.]png'                
            }
        }
    },
    
    # PROCESAMIENTO MÚLTIPLE DE URL_011 (optimizado)
    'pass_sports': {
        'env_var': 'URL_011',
        'artist': 'Pass',
        'output_path': 'country/sports',
        'use_picons': False,
        'filter_type': 'multi_output',
        'outputs': {
            'pass_wnba': {
                'path': 'country/sports/sections/wnba',
                'custom_filter': 'pass_wnba',
                'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_wnba[.]png'                
            }
#            'pass_nhl': {
#                'path': 'country/sports/sections/nhl',
#                'custom_filter': 'pass_nhl',
#                'fixed_logo': 'https://raw.githubusercontent.com/jsosao/bics/main/picons/us_nhl[.]png'                                        
#            }
        }
    },
    
    # ALFA - Otros contenidos
    'alfa': {
        'env_var': 'URL_001',
        'artist': 'Alfa',
        'output_path': 'country/others/test/alfa',
        'use_picons': False,
        'filter_type': 'include_exclude',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "cartelera", "estrenos", "disney", "recien", "cine de oro", "marvel", "radio", "religiosos", "infantil", "kids", "vod", "serie", "novelas-", "24/7", "247", "musica"],
        'include_keywords': ["cine", "cultura", "deportes", "canales", "entretenimiento", ".hbo", "noticias", "(eventos)"]
    },
    'premium': {
        'env_var': 'URL_001',
        'artist': 'Alfa',
        'output_path': 'country/country/premium',
        'use_picons': False,
        'filter_type': 'include_exclude',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "cartelera", "estrenos", "disney", "recien", "cine de oro", "marvel", "radio", "religiosos", "infantil", "kids", "vod", "serie", "novelas-", "24/7", "247", "musica"],
        'include_keywords': ["cine", "cultura", "deportes", "canales", "entretenimiento", ".hbo", "noticias", "(eventos)"]
    },    
    'pass': {
        'env_var': 'URL_011',
        'artist': 'Pass',
        'output_path': 'country/others/test/pass',
        'use_picons': False,
        'filter_type': 'skip_only',
        'skip_keywords': ["canales-adultos", "adultos", "adult", "porn"]
    }    
}

# ============================================================
# FILTROS PERSONALIZADOS (OPTIMIZACIÓN)
# ============================================================

CUSTOM_FILTERS = {
    #'alfa_eventos': lambda group, title: "(eventos)" in group.lower(),    
    'alfa_eventos': lambda group, title: "(eventos)" in group.lower() and not any(excluido in group.lower() for excluido in ["nba (eventos)", "nfl (eventos)"]),
    #'alfa_eventos': lambda group, title: "(eventos)" in group.lower() or "cielo sport" in title.lower() or "cielo evento" in title.lower(),        
    #'pass_eventos': lambda group, title: any(x in group.lower() for x in ["nba", "nhl", "nfl", "mlb", "ncaaf"]),
    'pass_ncaaf': lambda group, title: "ncaaf" in group.lower(),  
    'pass_nba': lambda group, title: "nba" in group.lower(),    
    'pass_nfl': lambda group, title: any(x in group.lower() for x in ["nfl"]) or any(x in title.lower() for x in ["nfl network","nfl redzone"]),    
    'pass_nhl': lambda group, title: any(x in group.lower() for x in ["nhl"]) or any(x in title.lower() for x in ["nhl network"]),    
    'pass_mlb': lambda group, title: any(x in group.lower() for x in ["mlb"]) or any(x in title.lower() for x in ["mlb network"]),   
    'pass_wnba': lambda group, title: "wnba" in group.lower(),
    'pass_ppv': lambda group, title: "ppv" in group.lower(),  
    'alfa_fox': lambda group, title: any(x in title.lower() for x in ["fox sports", "fox deportes", "fox soccer"]),
    'alfa_fox_1': lambda group, title: "foxone" in title.lower(),
    'alfa_espn': lambda group, title: "espn" in title.lower(),
    'alfa_tudn': lambda group, title: "tudn" in title.lower(),    
    'alfa_tu': lambda group, title: any(x in title.lower() for x in ["telemundo", "univision", "nbc universo", "unimas", "galavision"]),
    'alfa_sky': lambda group, title: any(x in title.lower() for x in ["cielo evento", "cielo sport"]),
    'alfa_nba': lambda group, title: any(x in group.lower() for x in ["nba"]) or any(x in title.lower() for x in ["nba tv"]),    
    'alfa_nfl': lambda group, title: any(x in group.lower() for x in ["nfl"]),    
    'alfa_mlb': lambda group, title: any(x in group.lower() for x in ["mlb"]) or any(x in title.lower() for x in ["mlb net"]),    
    'alfa_cartelera_2025': lambda group, title: any(x in group.lower() for x in ["cartelera 2025"]),
    'alfa_depo': lambda group, title: "deportes" in group.lower(),
    'cord_nfl': lambda group, title: any(x in group.lower() for x in ["nfl"]),  
    'cord_mlb': lambda group, title: any(x in group.lower() for x in ["mlb"]),   
    'cord_nba': lambda group, title: any(x in group.lower() for x in ["nba"]),    
    'cord_nhl': lambda group, title: any(x in group.lower() for x in ["nhl"]),
    'cord_ncaaf': lambda group, title: any(x in group.lower() for x in ["ncaaf"]),        
    'cord_ncaab': lambda group, title: any(x in group.lower() for x in ["ncaab"]), 
    'cord_ppv': lambda group, title: any(x in group.lower() for x in ["ppv"])           
}

# ============================================================
# FUNCIONES DE VALIDACIÓN DE FECHAS
# ============================================================

def extract_event_date(title):
    """Extrae fecha de un título de evento"""
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",           # 2025-01-15
        r"(\d{1,2}/\d{1,2})",             # 1/15 o 01/15
        r"([A-Za-z]+ \d{1,2})",           # January 15 o Jan 15
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            try:
                text = match.group(1)
                for fmt in ("%Y-%m-%d", "%m/%d", "%B %d", "%b %d"):
                    try:
                        parsed = datetime.strptime(text, fmt)
                        if "%Y" not in fmt:
                            parsed = parsed.replace(year=datetime.now().year)
                        return parsed.date()
                    except ValueError:
                        continue
            except Exception:
                continue
    return None

def is_event_outdated(title):
    """Verifica si un evento ya pasó"""
    event_date = extract_event_date(title)
    if event_date:
        today = datetime.now().date()
        return event_date < today
    return False
    
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
    #text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\.', ' ', text.strip())
    #text = re.sub(r'[^\w\s&!:@]', '', text)
    text = re.sub(r'[^\w\s&!:@\/\\]', '', text)
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
        if item['type'] == 'file' and item['name'].endswith('.png'):
            logo_url = picons_base_url + path.lstrip('/') + ('/' if path else '') + item['name']
            logo_name = item['name'].replace('.png', '')
            logos.append({
                'name': logo_name,
                'normalized_name': normalize_text(logo_name),
                'url': logo_url.replace(".png", "[.]png"),
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
        print(f"✓ Se encontraron {len(picons_cache)} picons disponibles\n")
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

def find_best_logo_match(title, picons_list):
    if not picons_list:
        return None
    
    title = replace_country_codes(title)
    normalized_title = re.sub(r'\s+', '_', title).lower()

    for logo in picons_list:
        if logo['normalized_name'] == normalized_title:
            return logo['url']
    
    best_match = None
    max_score = 0
    
    for logo in picons_list:
        logo_words = set(logo['normalized_name'].split('_'))
        title_words = set(normalized_title.split('_'))
        common_words = logo_words.intersection(title_words)
        
        if len(common_words) > 0:
            score = len(common_words) / max(len(logo_words), len(title_words))
            if score > max_score and score > 0.3:
                max_score = score
                best_match = logo
    
    if best_match and max_score > 0.5:
        return best_match['url']
    
    if not best_match:
        for logo in picons_list:
            if len(logo['normalized_name']) >= 3:
                if normalized_title in logo['normalized_name'] or logo['normalized_name'] in normalized_title:
                    if len(logo['normalized_name']) >= len(normalized_title) * 0.6:
                        return logo['url']
    
    if best_match:
        return best_match['url']
    
    return None

def get_in_title_logo(title):
    title_lower = title.lower()
    for variation, canonical in VARIATION_TO_CANONICAL.items():
        if variation in title_lower:
            return IN_TITLE_LOGOS.get(canonical)
    return None

def get_country(title):
    return "us"

def get_tag(group_title):
    return group_title.lower()

def should_skip_channel(group_title, channel_title, config, output_name=None):

    #if is_event_outdated(channel_title):
    #    return True
        
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
    use_picons = config.get('use_picons', False)
    fixed_logo = config.get('fixed_logo', None)
    
    if output_name and config['filter_type'] == 'multi_output':
        output_config = config['outputs'].get(output_name, {})
        use_picons = output_config.get('use_picons', use_picons)
        fixed_logo = output_config.get('fixed_logo', fixed_logo)
    
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
                
                # Determinar logo con lógica optimizada
                final_logo = None
                
                # PRIORIDAD 1: Logo fijo (para ABC, NBC, CBS, FOX)
                if fixed_logo:
                    final_logo = fixed_logo
                    logos_fixed += 1
                
                # PRIORIDAD 2: Verificar palabras clave en título
                elif use_picons:
                    in_title_logo = get_in_title_logo(original_title)
                    if in_title_logo:
                        final_logo = in_title_logo
                        logos_in_title += 1
                
                # PRIORIDAD 3: Buscar en repositorio de picons
                if not final_logo and use_picons:
                    matched_picon = find_best_logo_match(title, picons_list)
                    if matched_picon:
                        final_logo = matched_picon
                        logos_found += 1
                
                # PRIORIDAD 4: Usar logo original del stream
                if not final_logo and tvg_logo and tvg_logo.strip():
                    final_logo = tvg_logo.replace("[", "").replace("]", "")
                    logos_original += 1

                # PRIORIDAD 5: Logo por defecto
                if not final_logo:
                    final_logo = default_logo
                    logos_default += 1

                entry = {
                    'Artist': config['artist'],
                    'Title': title,
                    'streamFormat': 'hls|mts',
                    'SwitchingStrategy': 'full-adaptation',
                    'Logo': final_logo.replace("[", "").replace("]", ""),
                    'Stream': escape_url(stream_url),
                    'Country': get_country(title),
                    'Tag': get_tag(group_title),
                    'Live': True     
                }
                entries.append(entry)
        
        i += 1
    
    return entries, skipped_count, logos_original, logos_found, logos_default, logos_in_title, logos_fixed, invalid_count

def generate_output(entries, category_name=None):

    """Genera salida en formato JSON con categorías opcionales"""
    
    # Si no hay categoría, generar lista simple
    if category_name is None:
        return json.dumps(entries, indent=2, ensure_ascii=False, sort_keys=False)
    
    # Si hay categoría, generar con estructura de categorías
    output = {category_name: entries}
    return json.dumps(output, indent=2, ensure_ascii=False, sort_keys=False)

def generate_merged_output(entries_by_category):
    """Genera salida JSON con múltiples categorías para archivos fusionados"""
    output = {}
    for category, entries in entries_by_category.items():
        output[category] = entries
    return json.dumps(output, indent=2, ensure_ascii=False, sort_keys=False)

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
    
    # Obtener picons si algún conversor los necesita
    picons_list = []
    needs_picons = any(config.get('use_picons', False) or 
                      (config.get('filter_type') == 'multi_output' and 
                       any(out.get('use_picons', False) for out in config.get('outputs', {}).values()))
                      for config in CONVERTERS.values())
    if needs_picons:
        picons_list = get_picons_list()
    
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
# Procesar grupos de fusión
    for merge_group, converters in merge_groups.items():
        try:
            print(f"{'='*60}")
            print(f"🔗 GRUPO DE FUSIÓN: {merge_group.upper()}")
            print(f"{'='*60}")
            
            # Diccionario para agrupar por categoría
            entries_by_category = {}
            total_skipped = 0
            total_orig = 0
            total_found = 0
            total_default = 0
            total_in_title = 0
            total_fixed = 0
            total_invalid = 0
            
            for converter_name, config in converters:
                print(f"\n  📦 Procesando: {converter_name} - {config['artist']}")
                
                env_var = config['env_var']
                content = m3u_cache.get(env_var)
                
                if not content:
                    print(f"  ✗ No se pudo obtener contenido de {env_var}")
                    continue
                
                entries, skipped, orig, found, default, in_title, fixed, invalid = process_m3u_content(
                    content, config, converter_name, picons_list
                )
                
                # Usar el nombre del conversor como categoría
                category_name = config.get('category_name', config['artist'])
                entries_by_category[category_name] = entries
                
                total_skipped += skipped
                total_orig += orig
                total_found += found
                total_default += default
                total_in_title += in_title
                total_fixed += fixed
                total_invalid += invalid
                
                print(f"  ✓ Canales obtenidos: {len(entries)} | Omitidos: {skipped} | Inválidos: {invalid}")
            
            if not entries_by_category:
                print(f"\n⚠ No se generaron entradas para el grupo {merge_group}\n")
                failed += 1
                continue
            
            # Generar salida JSON con categorías
            output_content = generate_merged_output(entries_by_category)
            total_entries = sum(len(entries) for entries in entries_by_category.values())
            
            output_config = converters[0][1]
            save_output(output_config['output_path'], output_content)
            
            print(f"\n{'='*60}")
            print(f"✓ Ruta fusionada: {output_config['output_path']}")
            print(f"✓ Total de fusionados: {len(all_entries)} | Total omitidos: {total_skipped}")
            
            total = len(all_entries) if all_entries else 1
            stats = f"📊 Logos - "
            if total_fixed > 0:
                stats += f"Fijos: {total_fixed} ({total_fixed*100//total}%) | "
            if total_in_title > 0:
                stats += f"Por título: {total_in_title} ({total_in_title*100//total}%) | "
            if output_config.get('use_picons'):
                stats += f"Encontrados: {total_found} ({total_found*100//total}%) | "
            stats += f"Originales: {total_orig} ({total_orig*100//total}%) | Default: {total_default} ({total_default*100//total}%)"
            if total_outdated > 0:  # ← AGREGAR ESTAS LÍNEAS
                print(f"⏰ Total eventos vencidos: {total_outdated}")            
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
            total_outdated_multi = 0  # ← NUEVO
            
            for output_name, output_config in config['outputs'].items():
                #print(f"  📁 Procesando salida: {output_name}")
                
                entries, skipped, orig, found, default, in_title, fixed, invalid, outdated = process_m3u_content(
                    content, config, converter_name, picons_list, output_name
                )
                
                if not entries:
                    print(f"    ⚠ Sin entradas para {output_name}")
                    continue
                
                # Usar nombre del conversor o artist como categoría
                category_name = config.get('category_name', config['artist'])
                output_content = generate_output(entries, category_name)
            
                output_path = output_config['path']
                save_output(output_path, output_content)
                
                print(f"    ✓ Ruta: {output_path}")
                print(f"    ✓ Can: {len(entries)} | Omitidos: {skipped} | Inválidos: {invalid}")
                
                total = len(entries) if entries else 1
                stats = f"    📊 Logos - "
                if fixed > 0:
                    stats += f"Fijos: {fixed} ({fixed*100//total}%) | "
                if in_title > 0:
                    stats += f"Por título: {in_title} ({in_title*100//total}%) | "
                if output_config.get('use_picons', config.get('use_picons', False)):
                    stats += f"Encontrados: {found} ({found*100//total}%) | "
                stats += f"Originales: {orig} ({orig*100//total}%) | Default: {default} ({default*100//total}%)"
                if outdated > 0:
                    print(f"    ⏰ Eventos vencidos: {outdated}")                
                print(stats)
                print()
                
                outputs_generated += 1
                total_outdated_multi += outdated  # ← AGREGAR AL FINAL DEL BLOQUE

            if outputs_generated > 0:
                print(f"✓ {outputs_generated}/{len(config['outputs'])} salidas generadas exitosamente\n")
                if total_outdated_multi > 0:  # ← AGREGAR
                        print(f"⏰ Total eventos vencidos en todas las salidas: {total_outdated_multi}")                
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
            
            entries, skipped, orig, found, default, in_title, fixed, invalid, outdated = process_m3u_content(
                content, config, converter_name, picons_list
            )
            
            if not entries:
                print(f"⚠ No se generaron entradas para {converter_name}\n")
                failed += 1
                continue
            
            output_content = generate_output(entries)
            save_output(config['output_path'], output_content)
            
            print(f"\n✓ Ruta: {config['output_path']}")
            print(f"✓ Can: {len(entries)} | Omitidos: {skipped} | Inválidos: {invalid}")
            
            total = len(entries) if entries else 1
            stats = f"📊 Logos - "
            if fixed > 0:
                stats += f"Fijos: {fixed} ({fixed*100//total}%) | "
            if in_title > 0:
                stats += f"Por título: {in_title} ({in_title*100//total}%) | "
            if config.get('use_picons'):
                stats += f"Encontrados: {found} ({found*100//total}%) | "
            stats += f"Originales: {orig} ({orig*100//total}%) | Default: {default} ({default*100//total}%)"
            if outdated > 0:
                print(f"    ⏰ Eventos vencidos: {outdated}")            
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
    print(f"Descargas realizadas: {len(configured_urls)}")
    print("="*60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    main()
