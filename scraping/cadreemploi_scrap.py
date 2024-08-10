import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from tqdm import tqdm
from datetime import datetime
import hashlib
import numpy as np


# urls des annonces des 30 premieres pages
def get_all_links(base_url, num_pages):
    data = []
    domain = "https://www.cadremploi.fr"

    for page_num in tqdm(range(1, num_pages + 1),desc="Pages cadreemploi"):
        url = f"{base_url}{page_num}"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            for offer in soup.find_all('a', class_='row js-lien-detail-offre offre'):
                href = urljoin(domain, offer.get('href'))
                date_block = offer.find_next('div', class_='col-xs-12 derniere-ligne')
                date_text = date_block.get_text().strip()

                entry = {
                    'lien': href,
                    'publication': date_text
                }
                data.append(entry)
        else:
            print(f"Erreur lors de la récupération de la page {page_num}")
            break

    df = pd.DataFrame(data)
    return df

# determiner les annonces publié il y a moins de 24h
def annonces_moins_de_24h(df):
    cadremploi_24h = df[df['publication'].str.contains("Publiée il y a moins de 24h")]
    cadremploi_24h = cadremploi_24h.drop(columns=['publication'])
    return cadremploi_24h

# recuperer les infos des offres de moins de 24h
def scrape_pages(df_jobs):
    site_annonce = "cadre emploi"
    df_merged = pd.DataFrame()
    for url in tqdm(df_jobs['lien'], desc="Annonce cadreemploi"):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                entreprise = soup.find('div', class_='detail-nom-entreprise').text.strip()
                publication_time = soup.find('span', class_='date-publication').find('time')['datetime']
                publication = datetime.strptime(publication_time, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d-%m-%Y')
                poste = soup.find('span', class_='position titre-offre').text.strip()
                contrat = soup.find('div', class_='detail-type-contrat-entreprise').text.strip()
                profil = soup.find('p', class_='desc__p desc_profil cache').text.strip()
                description = soup.find('p', class_='desc__p desc_missions cache').text.strip()
                ville = soup.find('div', class_='detail-localisation-entreprise').text.strip()

                entry = {
                    'site_annonce': site_annonce,
                    'entreprise': entreprise,
                    'publication': publication,
                    'poste': poste,
                    'contrat': contrat,
                    'profil': profil,
                    'description': description,
                    'ville': ville,
                    'lien': url
                }
                data = pd.json_normalize(entry)

                if data['poste'].str.lower().str.contains('data').all():
                    df_merged = pd.concat([df_merged, data], axis=0, ignore_index=True)
                else :
                    pass
                
        except:
            pass

    return df_merged

# generer une colonne id
def generate_id(row, columns):
    # Concaténer les valeurs des colonnes sélectionnées en une seule chaîne
    value = ''.join(str(row[col]) for col in columns)
    # Générer un hachage MD5 de cette chaîne
    return hashlib.md5(value.encode()).hexdigest()

# nettoyer et filtrer le csv
def clean_data(df):

    dico_nan = {
    
        "entreprise" : "inconnu",
        "publication" : np.nan,
        "poste" : "inconnu",
        "experience" : "inconnu",
        "contrat" : "inconnu",
        "valeur_duree_contrat" : np.nan,
        "type_duree_contrat" : "inconnu",
        "teletravail" : "inconnu",
        "valeur_salaire" : np.nan,
        "devise_salaire" : "inconnu",
        "periode_salaire" : "inconnu",
        "competences" : "inconnu",
        "profil" : "inconnu",
        "description" : "inconnu",
        "ville" : "inconnu",
    }

    df = df.apply(lambda x: x.str.lower())
    df = df.drop_duplicates(subset=['lien'])
    df['poste'] = df['poste'].str.replace(r'\s+nouveau$', '', regex=True)
    df['contrat'] = df['contrat'].str.replace(r'^apprentissage/alternance', 'alternance', regex=True)
    df['id'] = df.apply(lambda row: generate_id(row, ["entreprise", "poste" , "contrat" , "ville"]), axis=1)
    ordre_final = [ 'id','site_annonce','entreprise', 'publication', 'poste', 'contrat', 'profil', 'description', 'ville', 'lien']
    df = df[ordre_final]
    df['publication'] = pd.to_datetime(df['publication'],dayfirst=True)
    df = df.fillna(value=dico_nan)
    return df


def main_cadreemploi():
    url = "https://www.cadremploi.fr/emploi/liste_offres?motscles=data&page="
    df_jobs = get_all_links(url, 30)
    cadremploi_24h = annonces_moins_de_24h(df_jobs)
    df_all_jobs = scrape_pages(cadremploi_24h)

    return clean_data(df_all_jobs)