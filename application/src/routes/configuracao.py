import sqlite3
from flask_login import UserMixin
from flask_bcrypt import check_password_hash, generate_password_hash
from flask import render_template, Blueprint, redirect, flash, url_for, request, session
import requests
from datetime import datetime
from flask_login import current_user, login_required
from application.src.database.users.configure_users import my_db, Links, link_of_user
from application.src.models.link_validators import is_valid_link, is_linkedin_link, personal_link
from application.src.services.user_service import get_user_info, UserData
import os
from dotenv import load_dotenv

configuracao_ = Blueprint('config', __name__, template_folder='templates')
load_dotenv()


@configuracao_.route('/devorbit/configuracao/<usuario>', methods=['POST', 'GET'])
def config_account(usuario):
    # Inicializando variáveis para evitar problemas
    
    user_photo = None
    email_usuario = None
    bio = None
    status = None
    id_usuario = None
    date_create = None

    if request.method == 'POST':
        github = request.form.get('github')
        linkedin = request.form.get('linkedin')  
        site = request.form.get('site')

          
        # Validação dos links
        is_github_valid = is_valid_link(github) if github else False
        is_linkedin_valid = is_linkedin_link(linkedin) if linkedin else False
        my_link = personal_link(site) if site else False

    # Validar os links
        if not is_github_valid:
            flash(('github', "O link do GitHub fornecido é inválido."), "error")
        if not is_linkedin_valid:
            flash(('linkedin', "O link do LinkedIn fornecido é inválido."), "error")
        if not my_link:
            flash(('site', "O site pessoal fornecido é inválido."), "error")

    # Verifica se pelo menos um dos links é válido
        if is_github_valid or is_linkedin_valid:
            user_id = session.get('user', {}).get('id')
            if not user_id:
                return redirect(url_for('login.login_page'))

        # Correção: Passar valores diretamente
            link_data = Links(github=is_github_valid, linkedin=is_linkedin_valid, site=my_link)
            link_of_user(link_data, user_id)
            flash("Links salvos com sucesso!", "success")
            return redirect(url_for('config.config_account', usuario=usuario))
        else:
        # Redireciona de volta com mensagens de erro
            flash("Erro ao salvar links. Verifique os links e tente novamente.", "error")
            return redirect(url_for('config.config_account', usuario=usuario))

    try:
        
        conn = sqlite3.connect(os.getenv("BANCO_DB"))
        cursor = conn.cursor()
        cursor.execute('SELECT id, photo, email, bio, date_create, banner FROM usuarios WHERE name = ?', (usuario,))

        user = cursor.fetchone()
        user_photo = user[1]
        email_usuario = user[2]
        bio = user[3]
        date_create = user[4][0:10]
        usuario = current_user.username
        id_usuario = current_user.id
        banner = user[5]

        searching_account_data = UserData(current_user.id)
        if not searching_account_data:
            return redirect(url_for('errorHttp.page_erro'))
        
        username = searching_account_data[0]['username']
        user_id = searching_account_data[0]['id']
       

        status = "Conta Saudável" if usuario else "Sua conta está sendo verificada."


        conn.close()

       
    except requests.exceptions.RequestException:
        flash("Erro ao carregar a página. Tente novamente mais tarde.", "error")

    finally:
        conn.close()


    return render_template('configuracao.html',  user_photo=user_photo, usuario=usuario, 
                           email_usuario=email_usuario, status=status, id_usuario=id_usuario,
                            bio=bio, date_create=date_create, banner=banner, username=username)
