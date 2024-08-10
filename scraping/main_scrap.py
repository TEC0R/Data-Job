import sqlite3
from apec_scrap import main_apec
from wttj_scrap import main_wttj
from cadreemploi_scrap import main_cadreemploi
from hellowork_scrap import main_hellowork
from freework_scrap import main_freework
import pandas as pd

def db_file_storage(db_name, table_name, df):

    # Connexion à la base de données SQLite
    conn = sqlite3.connect(f"./data/{db_name}.db")
    
    # Enregistrer le DataFrame dans la base de données
    df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    
    # Fermer la connexion
    conn.close()

def connect_db(file, table):
    # Connectez-vous à la base de données
    conn = sqlite3.connect(f"./data/{file}.db")
    
    # Supposez que vous voulez lire une table nommée 'nom_table'
    table_name = table
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def update():

    df_apec = main_apec()
    db_file_storage('apec', 'df_clean', df_apec)

    df_wttj = main_wttj()
    db_file_storage('wttj', 'df_clean', df_wttj)

    df_cadreemploi = main_cadreemploi()
    db_file_storage('cadreemploi', 'df_clean', df_cadreemploi)

    df_hellowork = main_hellowork()
    db_file_storage('hellowork', 'df_clean', df_hellowork)

    df_freework = main_freework()
    db_file_storage('freework', 'df_clean', df_freework)



def concat_all_df():
    df_apec = connect_db('apec', 'df_clean')
    df_wttj = connect_db('wttj', 'df_clean')
    df_cadreemploi = connect_db('cadreemploi', 'df_clean')
    df_hellowork = connect_db('hellowork', 'df_clean')
    df_freework = connect_db('freework', 'df_clean')

    df_all = pd.concat([df_apec, df_wttj, df_cadreemploi, df_hellowork, df_freework]).reset_index(drop=True)
    db_file_storage('database', 'df_all', df_all)
    df_all.to_csv('./data/database.csv', index = False)

