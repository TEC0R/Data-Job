import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(destinataire,object,contenu):
    # Informations sur le compte email
    email_receiver = destinataire  # Adresse email du destinataire
    email_sender = 'cornelusse.terry@gmail.com'
    mot_de_passe = 'hqeg nvcz nunx tsaf'  # Mot de passe de votre compte email

    # Création du message
    message = MIMEMultipart()
    message['To'] = email_receiver
    message['Subject'] = object

    # Corps de l'email
    corps_email = contenu
    message.attach(MIMEText(corps_email, 'plain'))

    # Connexion au serveur SMTP
    serveur_smtp = smtplib.SMTP('smtp.gmail.com', 587)  # Serveur SMTP de Gmail
    serveur_smtp.starttls()  # Activer le chiffrement TLS
    serveur_smtp.login(email_sender, mot_de_passe)  # Authentification

    # Envoi de l'email
    texte_email = message.as_string()
    serveur_smtp.sendmail(email_sender, email_receiver, texte_email)

    # Fermeture de la connexion SMTP
    serveur_smtp.quit()