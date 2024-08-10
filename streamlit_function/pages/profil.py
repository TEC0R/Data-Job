import streamlit as st
from rag.load_cv_model import pdf_loader, transform_text_to_json

diplomes_et_titres_pro_france = [
    "Doctorat (PhD)",
    "Habilitation à Diriger des Recherches (HDR)",
    "Master",
    "Diplôme d'Études Approfondies (DEA)",
    "Diplôme d'Études Supérieures Spécialisées (DESS)",
    "Diplôme d'Ingénieur",
    "Titre d'Ingénieur",
    "Licence",
    "Bachelor",
    "Licence Professionnelle",
    "Diplôme de Technicien Supérieur (DTS)",
    "Diplôme de Responsable",
    "Brevet de Technicien Supérieur (BTS)",
    "Diplôme Universitaire de Technologie (DUT)",
    "Diplôme de Comptabilité et Gestion (DCG)",
    "Diplôme d'État d'Éducateur Spécialisé (DEES)",
    "Brevet de Technicien (BT)",
    "Baccalauréat (BAC)",
    "Baccalauréat Professionnel",
    "Baccalauréat Technologique",
    "Brevet des Collèges",
    "Diplôme National du Brevet (DNB)",
    "Certificat d'Aptitude Professionnelle (CAP)",
    "Brevet d'Études Professionnelles (BEP)",
    "Certificat de Formation Professionnelle (CFP)",
    "Certificat de Compétence Professionnelle (CCP)",
    "Certificat de Qualification Professionnelle (CQP)",
    "Certificat de Scolarité",
    "Attestation de Formation",
    # Titres Professionnels avec niveaux
    "Titre Professionnel Niveau 5",
    "Titre Professionnel Niveau 4",
    "Titre Professionnel Niveau 3"
]

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
    "Pandas",        # Analyse et manipulation de données
    "Numpy",         # Calcul scientifique et manipulation de tableaux
    "Matplotlib",    # Visualisation de données
    "Seaborn",       # Visualisation statistique
    "Plotly",        # Visualisation interactive
    "Altair",        # Visualisation déclarative
    "Scikit-learn",  # Apprentissage automatique
    "Tensorflow",    # Apprentissage profond
    "Keras",         # API haut niveau pour TensorFlow
    "Pytorch",       # Apprentissage profond
    "Nltk",          # Traitement du langage naturel
    "Spacy",         # Traitement du langage naturel
    "Transformers",  # Modèles de langage basés sur des transformateurs
    "Sqlalchemy",    # ORM pour bases de données SQL
    "Sqlite3",       # Interface pour SQLite
    "Pyodbc",        # Interface ODBC pour bases de données
    "Dask",          # Calcul parallèle et manipulation de grands ensembles de données
    "Vaex",          # Analyse de grands ensembles de données en mémoire
    "Streamlit"      # Création d'applications web interactives
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

list_contrat = ["CDI","CDD","STAGE","ALTERNANCE"]

def profil():
    profil_authen = st.session_state["config"]["credentials"]["usernames"][st.session_state["username"]]
    st.header("Vous pouvez directement importer votre CV")

    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # Création du fichier uploader avec les paramètres spécifiés
    uploaded_file = st.file_uploader(
        label="Téléchargez un fichier PDF",  # Label du widget
        type=["pdf"],                       # Accepter uniquement les fichiers PDF
        accept_multiple_files=False,        # Autoriser seulement un fichier
        label_visibility="visible"          # Visibilité du label
    )


    # Vérification si un fichier a été téléchargé
    if uploaded_file is not None:
        st.write("Fichier téléchargé :")
        st.write(uploaded_file.name)  # Afficher le nom du fichier téléchargé
        docu_pdf = pdf_loader(uploaded_file)
        result_json = transform_text_to_json(docu_pdf)

        profil_authen["contrat"] = [element for element in list_contrat if element in result_json["contrat"]]
        profil_authen["ville"] = result_json["ville"]
        profil_authen["hardskills"]["sql"] = [element for element in sql_languages_known if element in result_json["sql"]]
        profil_authen["hardskills"]["python"] = [element for element in python_libraries if element in result_json["python"]]
        profil_authen["hardskills"]["dashboard"] = [element for element in dashboarding_tools if element in result_json["dashboarding"]]
        profil_authen["softskills"] = [element for element in soft_skills_data if element in result_json["softskills"]]


    else:
        st.write("Veuillez télécharger un fichier PDF.")


    st.header("Sinon remplir votre profil manuellement")

    st.header("Profil")

    _1, _2, _3 = st.columns(3)

    with _1:
        info_username = st.text_input("Pseudo", st.session_state["username"])
        info_name = st.text_input("Prenom", st.session_state["name"])
    with _2:

        if "diplome" in profil_authen:
            info_diplome = st.selectbox('Diplome', diplomes_et_titres_pro_france, index= diplomes_et_titres_pro_france.index(profil_authen["diplome"]))
        else:
            info_diplome = st.selectbox('Diplome', diplomes_et_titres_pro_france)

        if "contrat" in profil_authen:
            info_contrat = st.multiselect('Contrat', list_contrat, default=profil_authen["contrat"])
        else:
            info_contrat = st.multiselect('Contrat', list_contrat)
    with _3:
        if "ville" in profil_authen:
            info_ville = st.text_input("Ville", profil_authen["ville"])
        else :
            info_ville = st.text_input("Ville","")
        
        if "niveau" in profil_authen:
            info_niveau = st.selectbox('Niveau', ["JUNIOR","INTEMERDIAIRE","SENIOR"], index=["JUNIOR","INTEMERDIAIRE","SENIOR"].index(profil_authen["niveau"]))
        else:
            info_niveau = st.selectbox('Niveau', ["JUNIOR","INTEMERDIAIRE","SENIOR"])
        
    st.subheader("Hard Skills")


    if "sql" in profil_authen["hardskills"]:
        info_hardskills_sql = st.multiselect("SQL", sql_languages_known, default=profil_authen["hardskills"]["sql"])
    else:
        info_hardskills_sql = st.multiselect("SQL" ,sql_languages_known)
    
    if "python" in profil_authen["hardskills"]:
        info_hardskills_python = st.multiselect("Python", python_libraries, default=profil_authen["hardskills"]["python"])
    else:
        info_hardskills_python = st.multiselect("Python" ,python_libraries)

    if "dashboard" in profil_authen["hardskills"]:
        info_hardskills_dashboard = st.multiselect("Logiciel de Dashboard", dashboarding_tools, default=profil_authen["hardskills"]["dashboard"])
    else:
        info_hardskills_dashboard = st.multiselect("Logiciel de Dashboard" ,dashboarding_tools)

    st.subheader("Soft Skills")

    if "softskills" in profil_authen:
        info_hardskills_dashboard = st.multiselect("", soft_skills_data, default=profil_authen["softskills"])
    else:
        info_hardskills_dashboard = st.multiselect("" ,soft_skills_data)


    if st.button("Sauvegarder"):
        profil_authen["name"] = info_name
        profil_authen["diplome"] = info_diplome
        profil_authen["contrat"] = info_contrat
        profil_authen["ville"] = info_ville
        profil_authen["niveau"] = info_niveau
        profil_authen["hardskills"]["sql"] = info_hardskills_sql
        profil_authen["hardskills"]["python"] = info_hardskills_python
        profil_authen["softskills"] = info_hardskills_dashboard
        st.success("Enregistrement avec succes !")