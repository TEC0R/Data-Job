import pandas as pd
import requests
import hashlib
from bs4 import BeautifulSoup
from tqdm import tqdm


def api_freework():
  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'application/json',

  }

  l_df = []
  for page in tqdm(range(1,23)):

      url = f"https://www.free-work.com/api/job_postings?page={page}&itemsPerPage=16&searchKeywords=data+analyste"
      response = requests.get(url, headers=headers)
      if response.status_code == 200:
          data = response.json()  # Si la réponse est en JSON
          df = pd.DataFrame(data)
          l_df.append(df)
      else:
          print(f"Échec de la requête avec le statut: {response.status_code}")


  df = pd.concat(l_df)
  return df


def clean_data(df):
# réitialisation de l'index
  df =df.reset_index(drop=True)

# supprimer colonne
  colonne_a_supprimer = ['startsAt','minAnnualSalary','maxAnnualSalary','applicationContact','applicationUrl','modifiedByUserAt','annualSalary','status','published','renewable','applicationType','createdAt','publishedAt','expiredAt']
  df = df.drop(columns=colonne_a_supprimer)

# creer une colonne pr l'origine de la données
  df['site_annonce']= 'freework'

# créer colonne lien
  df['lien'] = "https://www.free-work.com/fr/tech-it/analyste/job-mission/" + df['slug']

# Remplacer  par "€" dans la colonne 'colonne'
  df['currency'] = '€'

# remplacer les nan par inconnu dans company description
  for c  in ['remoteMode','candidateProfile','companyDescription'] :
    df[c] = df[c].fillna("aucun")

# Remplacer "Expert" par "senior" dans la colonne 'experienceLevel'
  df['experienceLevel'] = df['experienceLevel'].replace('expert', 'senior', regex=False)


# afficher les annonces commençant par data, business
  keywords = 'data|Data|Business|business|💼|Data Project Manager|Data scientist|PO DATA|Data Engineer|DATA engineer|Senior Data|Consultant Data|Consultant BI|Business Intelligence|DATA ENGINEER|'
  df = df[df['title'].str.contains(keywords, regex=True)]

#recuperer que les freelance
  df['contracts'] = df['contracts'].str.join(',')
  df = df[df.contracts.str.contains('contractor', na = False)]

# réitialisation de l'index
  df=df.reset_index(drop=True)

# extraire skills
  df['skills'] = df['skills'].apply(lambda list_dico_skill :   [dico['name']   for dico in list_dico_skill] )
  df['softSkills'] = df['softSkills'].apply(lambda list_dico_skill :   [dico['name']   for dico in list_dico_skill] )

# extraire location
  def extract_location(row):
    loc  = row['location']
    return loc['country'] , loc['adminLevel1'],  loc['adminLevel2'], loc['postalCode'],loc['label'], str(loc['longitude']), str(loc['latitude'])

  result = df.apply(extract_location, axis = 1, result_type='expand')

# Renommer les colonnes
  result.columns = ['country', 'region', 'departement', 'postalCode','label','longitude', 'latitude']

# Joindre le résultat à la dataframe d'origine
  df = pd.concat([df, result], axis=1)

# extraire company
  def extract_compagny(row):
    loc  = row['company']
    try :
      return loc['description'] , loc['logo']['medium'],  loc['name'].lower()
    except :

      return loc['description'] , loc['logo'],  loc['name'].lower()

  result_compagny = df.apply(extract_compagny, axis = 1, result_type='expand')

# Renommer les colonnes
  result_compagny.columns = ['description', 'logo', 'name']

# Joindre le résultat à la dataframe d'origine
  df= pd.concat([df, result_compagny], axis=1)

# mettre durationValue en int
  df['durationValue'] = df['durationValue'].astype(int)

# calcul de la moyenne salaire avec création de la colonne
  df['averageDailySalary'] = df[['minDailySalary', 'maxDailySalary']].mean(axis=1).round(2)

# convertir update en date .dt.strftime('%d-%m-%Y')
  df['updatedAt'] = pd.to_datetime(df['updatedAt'])  # Conversion en datetime
  df["updatedAt"] = df["updatedAt"].dt.date  # Extraire la date

# Normalisation
  dico_renommage = {
        'site_annonce': 'site_annonce',
        'name': 'entreprise',
        'updatedAt': 'publication',
        'title': 'poste',
        'experienceLevel': 'experience',
        'contracts': 'contrat',
        'durationValue': 'valeur_duree_contrat',
        'durationPeriod': 'type_duree_contrat',
        'remoteMode': 'teletravail',
        'averageDailySalary': 'valeur_salaire',
        'currency': 'devise_salaire',
        'companyDescription': 'competences',
        'candidateProfile': 'profil',
        'description': 'description',
        'label': 'ville',
    }

  df = df.rename(columns=dico_renommage)

# Remplacer "none" par "aucun" et traduction des mots dans la colonne 'teletravail'
  df['teletravail'] = df['teletravail'].replace('none', 'aucun', regex=False)
  df['teletravail'] = df['teletravail'].replace('partial', 'partiel', regex=False)
  df['teletravail'] = df['teletravail'].replace('full', 'total', regex=False)


# traduction colonne experience :
  df['experience'] = df['experience'].replace('intermediate', 'intermediaire', regex=False)

# traduction colonne contrat :
  df['contrat'] = df['contrat'].replace('contractor', 'freelance', regex=False)
  df['contrat'] = df['contrat'].replace('contractor,permanent', 'freelance,cdi', regex=False)
  df['contrat'] = df['contrat'].replace('permanent,contractor', 'cdi,freelance', regex=False)

# traduction colonne type_duree_contrat:
  df['type_duree_contrat'] = df['type_duree_contrat'].replace('year', 'annee', regex=False)
  df['type_duree_contrat'] = df['type_duree_contrat'].replace('month', 'mois', regex=False)
  df['type_duree_contrat'] = df['type_duree_contrat'].replace('day', 'jour', regex=False)


# Convertir les colonnes  en lower
  df[['poste', 'teletravail','competences','profil','description']] = df[['poste', 'teletravail','competences','profil','description']].apply(lambda x: x.str.lower())
  df['ville'] = df['ville'].str.lower()

#  créer un id
  def generate_id(row, columns):
    # Concaténer les valeurs des colonnes sélectionnées en une seule chaîne
    value = ''.join(str(row[col]) for col in columns)
    # Générer un hachage MD5 de cette chaîne
    return hashlib.md5(value.encode()).hexdigest()

  df['id'] = df.apply(lambda row: generate_id(row, ["entreprise", "poste" , "contrat" , "ville"]), axis=1)

# Réorganiser les colonnes selon l'ordre souhaité
  colonnes_finales = [
        'id', 'site_annonce', 'entreprise', 'publication', 'poste', 'experience',
        'contrat', 'valeur_duree_contrat', 'type_duree_contrat', 'teletravail',
        'valeur_salaire', 'devise_salaire', 'competences', 'profil', 'description', 'ville','lien'
    ]

# Vérifier et supprimer les colonnes en double
  df = df.loc[:,~df.columns.duplicated()]

# Reorganiser les colonnes
  df = df.reindex(columns=colonnes_finales)


# Fonction pour enlever toutes les balises HTML dans les colonnes de mon dataframe grâce à BeautifulSoup
  df['profil'] = df['profil'].apply(lambda x: BeautifulSoup(x, 'html.parser').text)
  df['competences'] = df['competences'].apply(lambda x: BeautifulSoup(x, 'html.parser').text)
  df['description'] = df['description'].apply(lambda x: BeautifulSoup(x, 'html.parser').text)
  return df


def main_freework():
   df_all = api_freework()
   return clean_data(df_all)
