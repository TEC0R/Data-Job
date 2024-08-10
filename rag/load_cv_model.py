import streamlit as st
import fitz
import warnings
warnings.filterwarnings('ignore')

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

sql_languages_known = [
    'ANSI',              # SQL standard défini par l'American National Standards Institute
    'MySQL',             # SQL utilisé par MySQL, un des SGBD open source les plus populaires
    'PostgreSQL',        # SQL utilisé par PostgreSQL, un SGBD open source réputé pour sa conformité aux standards
    'Oracle',            # SQL utilisé par Oracle Database, un des SGBD commerciaux les plus répandus
    'Microsoft SQL Server (T-SQL)', # SQL utilisé par Microsoft SQL Server, avec des extensions Transact-SQL
    'SQLite',            # SQL utilisé par SQLite, une base de données légère souvent utilisée dans les applications mobiles et les petits projets
    'MariaDB',           # SQL utilisé par MariaDB, un fork de MySQL avec des fonctionnalités améliorées
    'IBM DB2',           # SQL utilisé par IBM DB2, un SGBD commercial pour les grandes entreprises
    'Amazon Redshift',   # SQL utilisé par Amazon Redshift, un entrepôt de données basé sur PostgreSQL pour le cloud
    'Google BigQuery',   # SQL utilisé par Google BigQuery, un entrepôt de données en nuage de Google
    'Apache Hive QL',        # SQL utilisé par Apache Hive, un moteur de requêtes pour le traitement de données dans Hadoop
]

python_libraries = [
    "pandas",        # Analyse et manipulation de données
    "numpy",         # Calcul scientifique et manipulation de tableaux
    "matplotlib",    # Visualisation de données
    "seaborn",       # Visualisation statistique
    "plotly",        # Visualisation interactive
    "altair",        # Visualisation déclarative
    "scikit-learn",  # Apprentissage automatique
    "tensorflow",    # Apprentissage profond
    "keras",         # API haut niveau pour TensorFlow
    "pytorch",       # Apprentissage profond
    "nltk",          # Traitement du langage naturel
    "spacy",         # Traitement du langage naturel
    "transformers",  # Modèles de langage basés sur des transformateurs
    "sqlalchemy",    # ORM pour bases de données SQL
    "sqlite3",       # Interface pour SQLite
    "pyodbc",        # Interface ODBC pour bases de données
    "dask",          # Calcul parallèle et manipulation de grands ensembles de données
    "vaex",          # Analyse de grands ensembles de données en mémoire
    "streamlit"      # Création d'applications web interactives
]

dashboarding_tools = [
    "Tableau",          # Outil de visualisation de données très populaire pour créer des dashboards interactifs
    "Power BI",         # Outil de business intelligence de Microsoft, avec une intégration fluide dans l'écosystème Microsoft
    "Qlik Sense",       # Plateforme d'analyse de données offrant une exploration associative et des dashboards interactifs
    "Looker",           # Plateforme de business intelligence et d'analyse de données basée sur le cloud
    "Domo",             # Plateforme cloud de business intelligence pour créer des dashboards interactifs et intégrer des données en temps réel
    "Sisense",          # Logiciel d'analyse de données permettant de créer des dashboards interactifs avec des capacités d'intégration avancées
    "IBM Cognos Analytics", # Outil de business intelligence pour la création de dashboards et rapports interactifs
    "MicroStrategy",    # Plateforme de business intelligence offrant des fonctionnalités avancées pour la création de dashboards
    "Grafana",          # Outil open-source pour la visualisation de métriques en temps réel
    "Klipfolio",        # Plateforme cloud pour créer des dashboards interactifs et connecter divers types de données
    "Zoho Analytics",   # Solution de business intelligence pour la création de dashboards et d'analyses de données
    "TIBCO Spotfire",   # Outil d'analyse et de visualisation de données pour créer des dashboards interactifs
    "Chartio"           # Outil de business intelligence (Note : Acquis par Atlassian, nouvelles fonctionnalités intégrées dans Atlassian Analytics)
]

soft_skills_data = [
    "Communication",          # Capacité à expliquer clairement les résultats et les insights aux parties prenantes
    "Analyse Critique",       # Capacité à évaluer et interpréter les données de manière critique
    "Résolution de Problèmes", # Compétence pour identifier, analyser et résoudre des problèmes complexes
    "Gestion du Temps",       # Capacité à gérer efficacement son temps et à prioriser les tâches
    "Collaboration",          # Compétence pour travailler efficacement en équipe et collaborer avec différents départements
    "Adaptabilité",           # Capacité à s'adapter aux changements et aux nouvelles situations ou technologies
    "Esprit d'Initiative",    # Proactivité dans la recherche de nouvelles solutions ou opportunités d'amélioration
    "Compétences en Présentation", # Aptitude à créer et à présenter des rapports et des visualisations clairs
    "Gestion du Stress",      # Capacité à travailler sous pression et à gérer des situations stressantes
    "Compétences Interpersonnelles", # Capacité à interagir efficacement avec les autres
    "Attention aux Détails",  # Souci du détail pour assurer l'exactitude et la précision des analyses
    "Pensée Analytique",      # Capacité à réfléchir de manière analytique pour comprendre et résoudre des problèmes complexes
    "Curiosité",              # Désir d'apprendre et de comprendre davantage les données et les tendances
    "Gestion de Projet",      # Compétence à planifier, exécuter et superviser des projets de manière efficace
    "Éthique",                # Sens des responsabilités éthiques dans la manipulation et l'analyse des données
]


####################  pdf loader, va extraire le texte et retourner un str ###########################

def pdf_loader(pdf_file):
    text = ""
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

################# definir le parser ############################################

# Définition des classes Pydantic
class CV(BaseModel):
    contrat: str = Field(description="Type of employment contract in [CDI,CDD,STAGE,ALTERNANCE]")
    ville: str = Field(description="City where the job is located")
    sql: list[str] = Field(description=f"list of Proficiency in SQL in {sql_languages_known}")
    python: list[str] = Field(description=f"list of Knowledge of Python libraries in {python_libraries}")
    dashboarding: list[str] = Field(description=f"list of Experience with dashboarding software in {dashboarding_tools}")
    softskills: list[str] = Field(description=f"list of softskills in {soft_skills_data}")

# Créez le modèle de parsing JSON
class CVJsonOutputParser(JsonOutputParser):
    def __init__(self):
        super().__init__(pydantic_object=CV)

    def parse(self, text: str) -> CV:
        try:
            # Utilisation de `model_validate_json` pour créer une instance de CV à partir du JSON
            return self.pydantic_object.model_validate_json(text)
        except Exception as e:
            raise ValueError(f"Error parsing JSON: {e}")

############## definir le modele et appeler les differents elements ############################

def transform_text_to_json(text):

    template = """
    Vous êtes un assistant expert dans l'extraction des informations d'un cv. 
    Voici le texte du cv :
    <text>
    {context}
    </text>
    Retournez les informations suivantes en JSON si les éléments sont dans la liste donner :
    <text>
    {format_instructions}
    </text>

    Si tu trouve pas je souhaite que tu renvoi une liste vide
    """

    model = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=st.secrets['GROQ_API_KEY'])
    parser = CVJsonOutputParser()
    
    # Créez le modèle de prompt
    prompt = PromptTemplate(
        input_variables=["context"],
        template=template,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )


    chain = LLMChain(llm=model, prompt=prompt, output_parser=parser)
    response = chain.invoke(text)
    return response["text"]