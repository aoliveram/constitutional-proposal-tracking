import requests
from bs4 import BeautifulSoup
import json
import urllib3
import re
import logging
from urllib.parse import urljoin
import time

urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os

class BCNConvencionalesScraper:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_URL = "https://www.bcn.cl/historiapolitica/convencionales_constituyentes/"
    JSON_PATH = os.path.join(SCRIPT_DIR, "../convention_members.json")
    OUTPUT_FILE = os.path.join(SCRIPT_DIR, "conventional-profiles-raw.json")

    def __init__(self, delay=1.0):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = delay
        self.session.verify = False

    def load_json_names(self):
        """Loads and normalizes the target convention members from JSON."""
        with open(self.JSON_PATH, 'r', encoding='utf-8') as f:
            members = json.load(f)
        
        normalized = []
        for m in members:
            parts = m.split(',')
            last = parts[0].strip().lower()
            first = parts[1].strip().lower()
            normalized.append({
                "original": m,
                "first_name_lower": first,
                "last_name_lower": last,
                "bcn_url": None
            })
        return normalized

    def fetch_bcn_directory_links(self):
        logger.info("Fetching the general BCN directory for convencionales...")
        response = self.session.get(self.BASE_URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.select("a[href*='ficha/']")
        bcn_profiles = {}
        
        for link in links:
            href = link.get('href')
            text_name = link.get_text(strip=True).lower()
            if not text_name:
                url_name_parts = href.split('/')[-1].replace('_', ' ')
                text_name = url_name_parts.lower()
                
            full_url = urljoin(self.BASE_URL, href)
            bcn_profiles[text_name] = full_url

        logger.info(f"Retrieved {len(bcn_profiles)} unique profiles from BCN directory.")
        return bcn_profiles

    def match_names(self, json_members, bcn_profiles):
        matched_count = 0
        
        for member in json_members:
            for bcn_name, bcn_url in bcn_profiles.items():
                import unicodedata
                
                def normalize_text(text):
                    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()
                
                bcn_normalized = normalize_text(bcn_name)
                first_norm = normalize_text(member['first_name_lower'])
                last_norm = normalize_text(member['last_name_lower'])

                if first_norm in bcn_normalized and last_norm in bcn_normalized:
                    member['bcn_url'] = bcn_url
                    matched_count += 1
                    break

        logger.info(f"Successfully matched canonical URLs for {matched_count} out of {len(json_members)} members.")
        return json_members

    def parse_profile(self, url, original_name):
        if not url:
            return None
        
        logger.info(f"Parsing: {url}")
        response = self.session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = {
            "nombre_original_json": original_name,
            "url_bcn": url,
            "intro_wiki": None,
            "familia_y_juventud": None,
            "estudios_y_vida_laboral": None,
            "trayectoria_politica_y_publica": None,
            "temas_interes_y_propuestas": None,
            "integracion_comisiones": None,
            "distrito": None,
            "afiliacion_politica": None,
            "nombre_completo": None,
            "fecha_nacimiento": None,
            "lugar_nacimiento": None,
            "grado_academico": None,
            "profesion": None
        }
        
        # 1. Wiki Intro
        intro_div = soup.find('div', class_='intro_wiki')
        if intro_div:
            data["intro_wiki"] = intro_div.get_text('\n', strip=True)
            
        # 2. Box contenidos
        boxes = soup.find_all('div', class_='box_contenidos')
        for box in boxes:
            h4 = box.find('h4')
            if not h4:
                continue
            title = h4.get_text(strip=True).lower()
            content = box.find('div')
            if content:
                text = content.get_text('\n', strip=True)
                if 'familia' in title and 'juventud' in title:
                    data["familia_y_juventud"] = text
                elif 'estudios' in title and 'laboral' in title:
                    data["estudios_y_vida_laboral"] = text
                elif 'trayectoria' in title and 'política' in title:
                    data["trayectoria_politica_y_publica"] = text
                elif 'temas de interés' in title or 'propuestas' in title:
                    data["temas_interes_y_propuestas"] = text
                elif 'integración de comisiones' in title:
                    data["integracion_comisiones"] = text

        # 3. Datos personales (Atributos semánticos)
        name_span = soup.find('span', property="foaf:name")
        if name_span:
            data["nombre_completo"] = name_span.get_text(strip=True)
            
        date_span = soup.find('span', property="bio:date")
        if date_span:
            data["fecha_nacimiento"] = date_span.get('content', date_span.get_text(strip=True))
            
        place_span = soup.find('span', property="bio:place")
        if place_span:
            data["lugar_nacimiento"] = place_span.get_text(strip=True)
            
        # 4. Profesion and Grado Academico via table label rows
        for tr in soup.find_all('tr'):
            tds = tr.find_all(['td', 'th'])
            if len(tds) >= 2:
                b_tag = tds[0].find('b')
                label = b_tag.get_text(strip=True).lower() if b_tag else tds[0].get_text(strip=True).lower()
                
                # Check for the bcnbio:profession property inside the cell
                prof_span = tds[1].find('span', property="bcnbio:profession")
                if prof_span:
                    value = prof_span.get_text(strip=True)
                    if 'grado' in label and 'académico' in label:
                        data["grado_academico"] = value
                    elif 'profesión' in label:
                        data["profesion"] = value
            
        # 5. Distrito y afiliacion
        district_span = soup.find('span', property="bcnbio:representingPlaceNamed")
        
        party_span_named = soup.find('span', property="bcnbio:ofNamedPoliticalParty")
        party_span_alt = soup.find('span', property="bcnbio:PoliticalParty")
        party_span = party_span_named if party_span_named else party_span_alt
        
        if district_span:
            data["distrito"] = district_span.get_text(strip=True)
        if party_span:
            data["afiliacion_politica"] = party_span.get_text(strip=True)
            
        return data

    def run(self):
        targets = self.load_json_names()
        bcn_profiles = self.fetch_bcn_directory_links()
        matched_targets = self.match_names(targets, bcn_profiles)
        
        results = []
        for i, target in enumerate(matched_targets):
            if target['bcn_url']:
                data = self.parse_profile(target['bcn_url'], target['original'])
                if data:
                    results.append(data)
                time.sleep(self.delay)  # Be nice to the server
            else:
                logger.warning(f"No BCN profile found for {target['original']}")
                
        # Save output
        with open(self.OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            
        logger.info(f"Saved {len(results)} profiles to {self.OUTPUT_FILE}")

if __name__ == "__main__":
    scraper = BCNConvencionalesScraper(delay=0.5)
    scraper.run()
