import pandas as pd
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
from selenium import webdriver
import requests
import warnings
import numpy as np
import hashlib
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

def nb_pages(url):
    driver.get(url + str(1))
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div[1]/div/div/div[2]/div/div[2]/nav/ul/li[8]/a"))
    )
    html = driver.page_source
    return int(driver.find_elements(By.XPATH, "//*[@id='app']/div[1]/div/div/div[2]/div/div[2]/nav/ul/li[8]/a")[0].text)

def multi_page_wtj(url, nb_pages):
    
    list_href_list = []    
    for page in tqdm(range(1, nb_pages + 1),desc="Pages WTTJ"):
        driver.get(url + str(page) + "&sortBy=mostRecent&searchTitle=true")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div[1]/div/div/div[2]/div/div[2]/nav/ul/li[8]/a"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        queryparamshandling_list = soup.find_all('div', {"class" : "sc-bXCLTC kkKAOM ais-Hits-list-item"})
        is_break = 0
        for href in queryparamshandling_list:
            if href.find_all('span')[-1].text == 'hier':
                is_break = 1
                break
            company_url = re.sub(r'/fr/companies/', '', href.find('a')['href'])
            full_url = f"https://api.welcometothejungle.com/api/v1/organizations/{company_url}"
            list_href_list.append(full_url)
        if is_break == 1 :
            break
            
    return list_href_list

def api_hide_wtj(href_list):
    df = pd.DataFrame()
    for href in tqdm(href_list,desc="Annonces WTTJ"):
        request = requests.get(href)
        job_data = request.json()['job']
        job_df = pd.json_normalize(job_data)
        job_df['link'] = re.sub(r'https://api.welcometothejungle.com/api/v1/organizations/', 'https://www.welcometothejungle.com/fr/companies/',href)
        df = pd.concat([df, job_df], axis=0, ignore_index=True)
    return df

def clean_df_wtj(df):
    rename_dico = {
    
        "id" : "id",
        "site_annonce" : "site_annonce",
        "organization.name" : "entreprise",
        "updated_at" : "publication",
        "name" : "poste",
        "experience_level" : "experience",
        "contract_type" : "contrat",
        "contract_duration_min" : "valeur_duree_contrat",
        "type_duree_contrat" : "type_duree_contrat",
        "remote" : "teletravail",
        "valeur_salaire" : "valeur_salaire", 
        "salary_currency" : "devise_salaire",
        "periode_salaire" : "periode_salaire",         
        "skills" : "competences",
        "profile" : "profil",
        "description" : "description",
        "office.city" : "ville",
        "link" : "lien"
        
    }
    
    dico_id = {
    
        "experience_level" : {
    
            'LESS_THAN_6_MONTHS' : 'junior',
            '6_MONTHS_TO_1_YEAR' : 'junior',
            '1_TO_2_YEARS' : 'junior',
            '2_TO_3_YEARS' : 'junior',
            '3_TO_4_YEARS' : 'intermediaire',
            '4_TO_5_YEARS' : 'intermediaire',
            '5_TO_7_YEARS' : 'intermediaire',
            '5_TO_7_YEARS' : 'intermediaire',
            '7_TO_10_YEARS' : 'senior'
        },
    
        "contract_type" : {
    
            'full_time' : 'cdi',
            'internship' : 'stage',
            'freelance' : 'freelance',
            'other' : 'cdd',
            'temporary' : 'cdd',
            'apprenticeship' : 'alternance'
        },
        
        "remote" : {
    
            'partial' : 'partiel',
            'punctual' : 'partiel',
            'no' : 'aucun',
            'fulltime' : 'total'
            
        }
    
        
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
    df['updated_at'] = pd.to_datetime(df['updated_at']).dt.strftime('%d-%m-%Y')
    df['valeur_salaire'] = df['salary_min'] + df['salary_max'] / 2
    df['salary_currency'] = df['salary_currency'].replace('EUR', '€')
    df['periode_salaire'] = df['valeur_salaire'].apply(lambda x: 'mois' if len(str(x)) == 6 else 'annee' if len(str(x)) == 7 else np.nan)
    df['profile'].apply(lambda x: np.nan if not x else BeautifulSoup(x, "html.parser").text)
    df['description'] = df['description'].apply(lambda x: BeautifulSoup(x, "html.parser").text)
    df['id'] = df.apply(lambda row: generate_id(row, ['organization.name','name','contract_type','office.city']), axis=1)
    df['skills'] = df['skills'].apply(lambda x: ' '.join([pd.NA if not x else item['name']['fr'] for item in x]))
    df['type_duree_contrat'] = 'mois'
    df['site_annonce'] = 'welcometothejungle'
    df['type_duree_contrat'] = df['contract_duration_min'].apply(lambda x: 'mensuel' if x is not None else np.nan)
    filtre_columns = [v for k,v in rename_dico.items()]
    df = df.rename(columns=rename_dico)[filtre_columns]
    df = df.fillna(value=dico_nan)
    return df

def main_wttj():
    url = "https://www.welcometothejungle.com/fr/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR&query=data&page=" 
    nb_page_max = nb_pages(url)
    href_list = multi_page_wtj(url,nb_page_max)
    df_not_clean = api_hide_wtj(href_list)
    
    return clean_df_wtj(df_not_clean)

