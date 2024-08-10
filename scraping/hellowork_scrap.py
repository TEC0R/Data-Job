import pandas as pd
import re
from tqdm import tqdm
import requests
import hashlib
import numpy as np

def api_helloworld(periode="h", local="france", keyword="Data Analyst"):
    results = []
    page = 1
    while True:
        params = {
            "k": keyword,
            "l": local,
            "ray": "all",
            "cod": "all",
            "d": periode,
            "p": page,
            "mode": "scroll",
            "alert": " ",
            "timestamp": 1701361414591
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            "Referer": "www.hellowork.com"
        }

        response = requests.get("https://www.hellowork.com/searchoffers/getsearchfacets",
                               params=params, headers=headers)
        response_json = response.json()
        if "Results" not in response_json or not response_json["Results"]:
            break
        for result in tqdm(response_json["Results"],desc="hellowork"):
            publication_date = result["PublishDate"]
            match = re.search(r'(\d{4}-\d{2}-\d{2})', publication_date)
            formatted_date = match.group(0) if match else publication_date
            lien = result["UrlOffre"]
            lien_origine = (f'https://www.hellowork.com{lien}')
            results.append({
                "entreprise": result["CompanyName"],
                "publication": formatted_date,
                "poste": result["OfferTitle"],
                "contrat": result["ContractType"],
                "contrat_type": result["Criterions"][3]["Label"],
                "teletravail": result["Telework"],
                "salaire": result["DisplayedSalary"],
                "profil": result["Profile"],
                "description": result["Description"],
                "ville": result["Localisation"],
                "lien": lien_origine,
                "source": result["ResponseUrl"]
        })

        page += 1

    df = pd.DataFrame(results)
    df.reset_index(inplace=True)
    return df

def generate_id(row, columns):
    # Concaténer les valeurs des colonnes sélectionnées en une seule chaîne
    value = ''.join(str(row[col]) for col in columns)
    # Générer un hachage MD5 de cette chaîne
    return hashlib.md5(value.encode()).hexdigest()

def clean(df):

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

    df['site_annonce'] = 'hellowork'
    df['publication'] = pd.to_datetime(df['publication'],dayfirst=True).dt.strftime('%d-%m-%Y')
    df = df.apply(lambda x: x.str.lower() if x.name != 'publication' else x, axis=1)
    df['id'] = df.apply(lambda row: generate_id(row, ["entreprise", "poste" , "contrat" , "ville"]), axis=1)
    colonnes_finales = [
            'id', 'site_annonce', 'entreprise', 'publication', 'poste',
            'contrat','teletravail',
            'profil','description', 'ville','lien'
        ]
    df = df.reindex(columns=colonnes_finales)
    df = df.fillna(value=dico_nan)
    return df

def main_hellowork():
    df = api_helloworld()
    return clean(df)