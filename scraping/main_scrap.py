import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from apec_scrap import main_apec
from wttj_scrap import main_wttj
from cadreemploi_scrap import main_cadreemploi
from hellowork_scrap import main_hellowork
from freework_scrap import main_freework

class BigQueryStorage:
    def __init__(self, project_id, credentials_path):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        self.client = bigquery.Client(
            credentials=self.credentials,
            project=project_id
        )
        self.dataset_id = "job_scraping"
        
    def store_data(self, df, table_id):
        table_ref = f"{self.client.project}.{self.dataset_id}.{table_id}"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
        )
        
        try:
            job = self.client.load_table_from_dataframe(
                df, table_ref, job_config=job_config
            )
            job.result()
            print(f"✓ {len(df)} lignes chargées dans {table_ref}")
        except Exception as e:
            print(f"⚠ Erreur lors du chargement vers BigQuery: {str(e)}")

    def get_data(self, table_id):
        query = f"""
        SELECT * 
        FROM `{self.client.project}.{self.dataset_id}.{table_id}`
        """
        
        try:
            return self.client.query(query).to_dataframe()
        except Exception as e:
            print(f"⚠ Erreur lors de la récupération des données: {str(e)}")
            return pd.DataFrame()

def update(storage):
    # Dictionnaire des sources avec leurs fonctions correspondantes
    sources = {
        'apec': main_apec,
        'wttj': main_wttj,
        'cadreemploi': main_cadreemploi,
        'hellowork': main_hellowork,
        'freework': main_freework
    }
    
    # Exécute le scraping pour chaque source
    for source_name, scraping_function in sources.items():
        try:
            print(f"Scraping de {source_name}...")
            df = scraping_function()
            storage.store_data(df, f"{source_name}_jobs")
        except Exception as e:
            print(f"⚠ Erreur lors du scraping de {source_name}: {str(e)}")

def concat_all_data(storage):
    # Liste des sources
    sources = ['apec', 'wttj', 'cadreemploi', 'hellowork', 'freework']
    
    # Récupère les données de chaque source
    dataframes = []
    for source in sources:
        df = storage.get_data(f"{source}_jobs")
        if not df.empty:
            dataframes.append(df)
    
    # Concatène tous les DataFrames
    if dataframes:
        df_all = pd.concat(dataframes).reset_index(drop=True)
        
        # Stocke le résultat dans BigQuery
        storage.store_data(df_all, "all_jobs")
        
        # Sauvegarde optionnelle en CSV local pour backup
        df_all.to_csv('./data/database.csv', index=False)
        print("✓ Données combinées sauvegardées avec succès")
    else:
        print("⚠ Aucune donnée à combiner")

if __name__ == "__main__":
    # Configuration du stockage
    storage = BigQueryStorage(
        project_id="data-job",  # 
        credentials_path="./credentials.json"
    )
    
    # Exécution du pipeline
    print("Démarrage de la mise à jour des données...")
    update(storage)
    print("\nConcaténation des données...")
    concat_all_data(storage)