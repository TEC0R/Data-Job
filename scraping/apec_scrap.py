import pandas as pd
from bs4 import BeautifulSoup
import time
import re
from tqdm import tqdm
import requests
import warnings
import numpy as np
import hashlib
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

warnings.simplefilter(action='ignore', category=FutureWarning)

#Reglage et lancement du webdriver pour selenium

options = webdriver.ChromeOptions()

options.add_argument("--headless")  # Mode sans affichage
options.add_argument("--incognito")  # Mode incognito
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # Agent utilisateur

service = webdriver.chrome.service.Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)


def generate_id(row, columns):
    # Concaténer les valeurs des colonnes sélectionnées en une seule chaîne
    value = ''.join(str(row[col]) for col in columns)
    # Générer un hachage MD5 de cette chaîne
    return hashlib.md5(value.encode()).hexdigest()

def enter_apec(url):

    driver.get(url + str(0))
    
    cookies_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
    )
    cookies_button.click()

    time.sleep(1)
    pagemax = driver.find_elements(By.CLASS_NAME, "page-item")[-1]
    pagemax.click()
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "container-result"))
    )
    
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    return int(soup.find_all('a', {'class' : 'page-link'})[-1].text)

# Recuperation des données

def multi_page_apec(nb_page_max, url):

    list_href_list = []
    
    for page in tqdm(range(nb_page_max), desc='Pages Apec'):
        
        driver.get(url + str(page))
        
        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "container-result"))
        )
    
        time.sleep(1)
        
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        queryparamshandling_list = soup.find_all('a', {'queryparamshandling' : 'merge'})
        list_href_list += ["https://www.apec.fr" + href['href'] for href in queryparamshandling_list]

    
    return list_href_list


        
def api_hide_apec(href_list):

    df = pd.DataFrame()
        
    for href in tqdm(href_list, desc='Annonces Apec'):
        
        id = re.findall(r'\/([0-9]+[A-Z]+)\?', href)[0]
        link = f"https://www.apec.fr/cms/webservices/offre/public?numeroOffre={id}"
        request = requests.get(link)
        job_data = request.json()
        job_df = pd.json_normalize(job_data)
        job_df = job_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
        job_df['link'] = href
        if job_df['intitule'].str.lower().str.contains('data').all():
            df = pd.concat([df, job_df], axis=0, ignore_index=True)
        else :
            pass
    return df

# Nettoyage des données

def clean_df_apec(df):  
    dico_id = {
    
        "idNomTypeContrat" : {
    
            101888 : "cdi",
            101887 : "cdd",
            20053 : "alternance",
            101930 : "interim",
            101889 : "interim",
            597137 : "alternance",
            597138 : "alternance"
            
        },
    
        "idNomNiveauExperience" : {
    
            200269 : "junior",
            597150 : "junior",
            597151 : "junior",
            597152 : "junior",
            597153 : "intermediaire",
            597154 : "intermediaire",
            597155 : "intermediaire",
            597156 : "intermediaire",
            597157 : "senior",
            597158 : "senior",
            597159 : "senior",
            597160 : "senior"            
            
        },
    
        "idNomTeletravail" : {
            
            20766 : "partiel",
            20765 : "partiel",
            20767 : "total",
            20949 : "aucun"
            
        }
    }
    
    rename_dico = {
    
        "id" : "id",
        "site_annonce" : "site_annonce",
        "nomCompteEtablissement" : "entreprise",
        "audit.dateModification" : "publication",
        "intitule" : "poste",
        "idNomNiveauExperience" : "experience",
        "idNomTypeContrat" : "contrat",
        "valeur_duree_contrat" : "valeur_duree_contrat",
        "type_duree_contrat" : "type_duree_contrat",
        "idNomTeletravail" : "teletravail",
        "valeur_salaire" : "valeur_salaire",
        "devise_salaire" : "devise_salaire",
        "periode_salaire" : "periode_salaire",        
        "competences" : "competences",
        "texteHtmlProfil" : "profil",
        "texteHtml" : "description",
        "adresseOffre.adresseVille" : "ville",
        "link" : "lien"
        
    }
    
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
    
    df = df.apply(lambda x: x.replace({k: v for k, v in dico_id.get(x.name, {}).items()}))
    df['audit.dateModification'] = pd.to_datetime(df['audit.dateModification']).dt.strftime('%d-%m-%Y')
    df['texteHtml'] = df['texteHtml'].apply(lambda x: BeautifulSoup(x, "html.parser").text)
    df['texteHtmlProfil'] = df['texteHtmlProfil'].apply(lambda x: BeautifulSoup(x, "html.parser").text)
    df['competences'] = df['competences'].apply(lambda x: [ x if not x else item['libelle'] for item in x])
    df['competences'] = df['competences'].apply(lambda x: list(set(x)))
    df['competences'] = df['competences'].apply(lambda x: ' '.join([skill.replace(" ", "-") for skill in x]))
    df['adresseOffre.adresseVille'] = df['adresseOffre.adresseVille'].apply(lambda x: x if pd.isna(x) else re.findall(r'^[a-zA-Z]+\b', x)[0])
    df['site_annonce'] = "apec"
    df['id'] = df.apply(lambda row: generate_id(row, ['nomCompteEtablissement','intitule','idNomTypeContrat','adresseOffre.adresseVille']), axis=1)
    df['valeur_salaire'] = df['salaireTexte'].apply(lambda x: np.nan if x == "a négocier" else int(re.findall(r'[0-9]+', x )[0] + "000"))
    df['devise_salaire'] = df['salaireTexte'].apply(lambda x: np.nan if x == "a négocier" else re.findall(r'(?:£|\$|€)', x )[0])
    df['periode_salaire'] = df['salaireTexte'].apply(lambda x: np.nan if x == "a négocier" else re.findall(r'.*?(\w+)$', x )[0])
    df['periode_salaire'] = df['periode_salaire'].str.replace('annuel', 'annee')    
    df['valeur_duree_contrat'] = df.apply(lambda row: row['dureeContrat'] if 'dureeContrat' in row.index else np.nan, axis=1)
    df['type_duree_contrat'] = df.apply(lambda row: 'mensuel' if 'dureeContrat' in row.index else np.nan, axis=1)
    filtre_columns = [v for k,v in rename_dico.items()]
    df = df.rename(columns=rename_dico)[filtre_columns]
    df = df.fillna(value=dico_nan)
    return df


def main_apec():
    url = "https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles=data&salaireMinimum=20&salaireMaximum=200&typesConvention=143684&typesConvention=143685&typesConvention=143686&typesConvention=143687&anciennetePublication=101850&page="
    nb_page_max = enter_apec(url)
    href_list = multi_page_apec(nb_page_max, url)
    
    df_not_clean = api_hide_apec(href_list)
    
    return clean_df_apec(df_not_clean)