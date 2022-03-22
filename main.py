# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
# [START gae_python3_app]
from flask import Flask, render_template, Response, url_for, session, redirect, request
from google.cloud import datastore
from authlib.integrations.flask_client import OAuth
from authlib.integrations.flask_oauth2 import ResourceProtector
from datetime import datetime
from flask_wtf_polyglot import PolyglotForm
from jinja2 import Undefined
#tämä tuottaa xml-yhteensopivia lomakekenttiä
from wtforms import Form, PasswordField, StringField, validators, IntegerField, SelectField, widgets, SelectMultipleField, ValidationError, FieldList, FormField, BooleanField
from functools import wraps


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
app.secret_key = '!secret'
app.config.from_object('config')

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

#dekoraattori joka estää sivuille pääsemisen iilman kirjautumista
def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not 'user' in session:
            return redirect(url_for('main'))
        return f(*args, **kwargs)
    return decorated

import requests
# funktio jolla haetaan kirjautuneen käyttäjän tiedot
def get_user_email(access_token):
    r = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            params={'access_token': access_token})
    return r.json()

# Pääsivu jossa haetaan alkutiedot
@app.route('/')
def main():
    joukkueet = [{"sarja": "8 h", "nimi": "Onnenonkijat", "jasenet": ["Antero Paununen", "Pekka Paununen", "Raimo Laine"]}, {"sarja": "8 h", "nimi": "Mudan Ystävät", "jasenet": ["Kaija Kinnunen", "Teija Kinnunen"]}, {"sarja": "8 h", "nimi": "Vara 3", "jasenet": ["barbar", "foofoo"]}, {"sarja": "8 h", "nimi": "Tollot", "jasenet": ["Juju", "Tappi"]}, {"sarja": "8 h", "nimi": "Kahden joukkue", "jasenet": ["Matti Humppa", "Miikka Talvinen"]}, {"sarja": "8 h", "nimi": "Siskokset", "jasenet": ["Sanna Haavikko", "Seija Kallio"]}, {"sarja": "8 h", "nimi": "Dynamic Duo", "jasenet": ["Karhusolan Rentukka", "Kutajoen Tiukunen"]}, {"sarja": "8 h", "nimi": "Toipilas", "jasenet": ["Leena Annila", "Satu Lehtonen"]}, {"sarja": "8 h", "nimi": "Sopupeli", "jasenet": ["Antti Haukio", "Janne Hautanen", "Taina Pekkanen", "Venla Kujala"]}, {"sarja": "4 h", "nimi": "Retkellä v 13", "jasenet": ["Henna Venäläinen", "Katja Vitikka"]}, {"sarja": "4 h", "nimi": "Pelättimet", "jasenet": ["Kari Vaara", "Katja Vaara"]}, {"sarja": "8 h", "nimi": "Kaakelin putsaajat", "jasenet": ["Jaana Kaajanen", "Mikko Kaajanen", "Timo Ruonanen"]}, {"sarja": "8 h", "nimi": "Vara 1", "jasenet": ["barfoo","foobar"]}, {"sarja": "2 h", "nimi": "Hullut fillaristit", "jasenet": ["Hannele Saari", "Paula Kujala"]}, {"sarja": "2 h", "nimi": "Kotilot", "jasenet": ["Jaana Meikäläinen", "Kaisa Konttinen", "Maija Meikäläinen", "Niina Salonen"]}, {"sarja": "8 h", "nimi": "Rennot 1", "jasenet": ["Anja Huttunen", "Siru Kananen"]}, {"sarja": "8 h", "nimi": "Vara 2", "jasenet": ["bar","foo"]}, {"sarja": "4 h", "nimi": "Vapaat", "jasenet": ["Juha Vapaa", "Matti Vapaa"]}, {"sarja": "8 h", "nimi": "Susi jo syntyessään", "jasenet": ["Janne Pannunen", "Riku Aarnio"]}, {"sarja": "8 h", "nimi": "Vara 4", "jasenet": ["foo","bar"]}, {"sarja": "4 h", "nimi": "Rennot 2", "jasenet": ["Heikki Häkkinen", "Piia Virtanen", "Sari Maaninka"]}, {"sarja": "4 h", "nimi": "Tähdenlento", "jasenet": ["Anu", "Virva"]}, {"sarja": "8 h", "nimi": "RogRog", "jasenet": ["Antti Kaakkuri", "Mikko Meikäläinen", "Pekka Kosonen", "Samuli Paavola"]}]
    kilpailut = [
        {"kisanimi":"Jäärogaining", "loppuaika": "2019-03-17 20:00:00", "alkuaika": "2019-03-15 09:00:00"}, 
        {"kisanimi":"Fillarirogaining", "loppuaika": "2016-03-17 20:00:00", "alkuaika": "2016-03-15 09:00:00"}, 
        {"kisanimi":"Kintturogaining", "loppuaika": "2017-03-18 20:00:00", "alkuaika": "2017-03-18 09:00:00"}
        ]

    sarjat = [
        {"sarjanimi":"4 h", "kilpailu": "Jäärogaining", "kesto": 4}, 
        {"sarjanimi":"2 h", "kilpailu": "Jäärogaining", "kesto": 2}, {"sarjanimi":"8 h", "kilpailu": "Jäärogaining", "kesto": 8},{"sarjanimi":"Pikkusarja", "kilpailu": "Kintturogaining", "kesto": 4},{"sarjanimi":"Isosarja", "kilpailu": "Kintturogaining", "kesto": 8},{"sarjanimi":"Pääsarja", "kilpailu": "Fillarirogaining", "kesto": 4}]
    client = datastore.Client()
    for i in range(len(kilpailut)):
        vanhempikey = client.key("kilpailu", (i+1))
        vanhempi_entity = datastore.Entity(key=vanhempikey)
        kilpailut[i]["alkuaika"] = datetime.strptime(kilpailut[i]["alkuaika"], "%Y-%m-%d %H:%M:%S")
        kilpailut[i]["loppuaika"] = datetime.strptime(kilpailut[i]["loppuaika"], "%Y-%m-%d %H:%M:%S")
        vanhempi_entity.update(kilpailut[i])
        client.put(vanhempi_entity)

    for i in range(len(sarjat)):
        vanhempikey = client.key("sarja", (i+1))
        vanhempi_entity = datastore.Entity(key=vanhempikey)
        vanhempi_entity.update(sarjat[i])
        client.put(vanhempi_entity)

    for i in range(len(joukkueet)):
        avain = str(datetime.now())
        joukkueetkey = client.key("joukkueet", (i+1))
        joukkueet_entity = datastore.Entity(key=joukkueetkey)
        joukkueet_entity.update(joukkueet[i])
        joukkueet_entity.update({"avain": avain})
        client.put(joukkueet_entity)

    user = session.get('user')
    return render_template('home.html', user=user)

# Sovelluksen päääsivu, listaus kisoista,sarjoista,joukkuesita
@app.route('/kilpailut', methods=['POST', 'GET'])
@require_login
def kilpailut():
    client = datastore.Client()
    kisat = client.query(kind="kilpailu")#.fetch()
    kisat.order = ["kisanimi"]
    kisat = kisat.fetch()
    
    sarjat = client.query(kind="sarja")#.fetch()
    sarjat.order = ["sarjanimi"]
    sarjat = sarjat.fetch()
    
    joukkueet = client.query(kind="joukkueet")#.fetch()
    joukkueet.order = ["nimi"]
    joukkueet = joukkueet.fetch()
    
    kisanimet = []
    for k in kisat:
        kisanimet.append(k)
    
    sarjanimet = []
    for s in sarjat:
        sarjanimet.append(s)
    
    joukkueentiedot = []
    for j in joukkueet:
        joukkueentiedot.append(j)
    
    joukkueentiedot_jarj = sorted(joukkueentiedot, key=lambda d: d['nimi'].lower())
    
    for k in range(len(joukkueentiedot)):
        joukkueentiedot[k]['jasenet'].sort()
    
    omistaja = session.get('email_info')
    return Response(render_template('kilpailut.html', kisanimet=kisanimet,sarjanimet=sarjanimet, joukkueentiedot=joukkueentiedot_jarj, omistaja=omistaja))

# Sarjan valintasivu
@app.route('/kilpailut/<kilpailu>', methods=['POST', 'GET'])
@require_login
def sarjat(kilpailu):
    client = datastore.Client()
    results = client.query(kind="kilpailu").add_filter("kisanimi", "=", kilpailu).fetch()
    dicti = {}
    for r in results:
        dicti[r.id] = r['kisanimi']

    sarja = client.query(kind="sarja")
    sarja.order = ['sarjanimi']
    sarja = sarja.fetch()
    sarjanimet = []
    for s in sarja:
        if s['kilpailu'] == dicti[r.id]:
            sarjanimet.append(s)
    return Response(render_template('sarjat.html', sarjanimet=sarjanimet))

# Lomake joukkueen lisäämiseen
@app.route('/kilpailut/<kilpailu>/<sarja>', methods=['POST', 'GET'])
@require_login
def lomake(kilpailu, sarja):

    class joukkueentiedot(PolyglotForm):
        joukkuenimi = StringField('Joukkueen nimi',validators=[my_length_check])
        jasen1 = StringField('Jäsen 1', validators=[my_length_check])
        jasen2 = StringField('Jäsen 2', validators=[my_length_check])
        jasen3 = StringField('Jäsen 3')
        jasen4 = StringField('Jäsen 4')
        jasen5 = StringField('Jäsen 5')
    form = joukkueentiedot()

    if request.method == 'POST' and form.validate():
        joukkuenimi = request.form.get("joukkuenimi")
        jasen1 = request.form.get("jasen1")
        jasen2 = request.form.get("jasen2")
        jasen3 = request.form.get("jasen3")
        jasen4 = request.form.get("jasen4")
        jasen5 = request.form.get("jasen5")

        taulu = [jasen1,jasen2,jasen3,jasen4,jasen5]
        taulu2 = []
        for i in range(len(taulu)):
            if taulu[i].strip() != "":
                taulu2.append(taulu[i])
            else:
                continue

        testitaulu = []
        for i in range(len(taulu)):
            if taulu[i].strip() != "":
                testitaulu.append(taulu[i])
            else:
                continue
        samoja = onko_samoja(testitaulu)
        if samoja:
            viesti = "Joukkueessa ei saa olla samannimisiä henkilöitä"
            return render_template('lomake.html',form=form,viesti=viesti)
        
        samoja = duplikaatti_joukkueita(joukkuenimi,sarja)
        if samoja:
            viesti = "Sarjassa on jo "+joukkuenimi+" niminen joukkue"
            return render_template('lomake.html',form=form,viesti=viesti)

        client = datastore.Client()
        avain = str(datetime.now())
        joukkue = client.key("joukkueet", avain)
        joukkue_entity = datastore.Entity(key=joukkue)
        joukkue_entity.update( { "kilpailu": kilpailu, "sarja": sarja, "nimi": joukkuenimi, "jasenet": taulu2, "omistaja":session.get('email_info'), "avain": avain} )
        client.put(joukkue_entity)
        

    return Response(render_template('lomake.html', form=form))

# Joukkueen lisäykseen tarkistin että ei ole samannimisiä joukkueita
def duplikaatti_joukkueita(joukkue, sarja):
    client = datastore.Client()
    results = client.query(kind="joukkueet").add_filter("sarja","=",sarja).fetch()
    tiedot = []
    for r in results:
        tiedot.append(r)
    tulos = False
    for i in range(len(tiedot)):
        if joukkue.lower().strip() == tiedot[i]['nimi'].lower().strip():
            tulos = True
    return tulos
    

# Sivu joukkueen muokkaamiseen
@app.route('/muokkaa_<avain>', methods=['POST', 'GET'])
@require_login
def muokkaa_joukkuetta(avain):
    client = datastore.Client()
    results = client.query(kind="joukkueet").add_filter("avain", "=", avain).fetch()
    joukkuetiedot = []
    for r in results:
        joukkuetiedot.append(r)
    
    sarja = client.query(kind="sarja")
    sarja.order = ['sarjanimi']
    sarja = sarja.fetch()
    sarjanimet = []
    for s in sarja:
        if s['kilpailu'] == joukkuetiedot[0]['kilpailu']:
            sarjanimet.append(s)
    
    sarjat_formiin = []
    for s in sarjanimet:
        sarjat_formiin.append(s['sarjanimi'])

    class joukkueentiedot(PolyglotForm):
        joukkuenimi = StringField('Joukkueen nimi',validators=[my_length_check], default=joukkuetiedot[0]['nimi'])
        sarjalista = SelectField('Sarja', choices=sarjat_formiin)
        jasen1 = StringField('Jäsen 1', validators=[my_length_check], default=joukkuetiedot[0]['jasenet'][0])
        jasen2 = StringField('Jäsen 2', validators=[my_length_check], default=joukkuetiedot[0]['jasenet'][1])
        try:
            jasen3 = StringField('Jäsen 3', default=joukkuetiedot[0]['jasenet'][2])
        except:
            jasen3 = StringField('Jäsen 3')
        try:
            jasen4 = StringField('Jäsen 4', default=joukkuetiedot[0]['jasenet'][3])
        except:
            jasen4 = StringField('Jäsen 4')
        try:
            jasen5 = StringField('Jäsen 5', default=joukkuetiedot[0]['jasenet'][4])
        except:
            jasen5 = StringField('Jäsen 5')
        poistajoukkue = BooleanField('Poista joukkue')
    
    form = joukkueentiedot()

    if request.method == 'POST':
        joukkuenimi = request.form.get("joukkuenimi")
        sarjalista = request.form.get("sarjalista")
        jasen1 = request.form.get("jasen1")
        jasen2 = request.form.get("jasen2")
        jasen3 = request.form.get("jasen3")
        jasen4 = request.form.get("jasen4")
        jasen5 = request.form.get("jasen5")
        poistajoukkue = request.form.get("poistajoukkue")

        taulu = [jasen1,jasen2,jasen3,jasen4,jasen5]
        jasentaulu = []
        for i in range(len(taulu)):
            if taulu[i].strip() != "":
                jasentaulu.append(taulu[i])
            else:
                continue
        testitaulu = []
        for i in range(len(taulu)):
            if taulu[i].strip() != "":
                testitaulu.append(taulu[i])
            else:
                continue
        if poistajoukkue == "y":
            avain = client.key("joukkueet", joukkuetiedot[0]['avain'])
            client.delete(avain)
            return redirect('/kilpailut')
        
        # onko jäsenissä samannimisiä
        samoja = onko_samoja(testitaulu)
        if samoja:
            viesti = "Joukkueessa ei saa olla samannimisiä henkilöitä"
            return render_template('muokkaa.html',form=form,viesti=viesti)
        
        # Onko samannimisiä joukkueita
        samajoukkue = samoja_joukkueita(joukkuenimi, sarjalista, joukkuetiedot[0]['avain'])
        
        if samajoukkue:
            viesti = "Kilpailussa on jo "+joukkuenimi+" niminen joukkue"
            return render_template('muokkaa.html',form=form,viesti=viesti)

        if form.validate():
            # Allaoleva toimii vain itse lisätyille joukkueille koska avain on 
            # sama kuin key. Luennoitsija lahtosen valmiiksi antamille 
            # joukkueille ei käy mutta niihin ei tehtävässä tarvitsekkaan koskea.
            avain = client.key("joukkueet", joukkuetiedot[0]['avain'])
            muokkaus = datastore.Entity(avain)
            muokkaus.update({
                'nimi':joukkuenimi,
                'jasenet':jasentaulu,
                "sarja":sarjalista,
                "kilpailu":joukkuetiedot[0]['kilpailu'],
                "omistaja":joukkuetiedot[0]['omistaja'],
                "avain":joukkuetiedot[0]['avain']
            })
            client.put(muokkaus)
            
    return render_template('muokkaa.html',form=form)

# tarkistaa syötettyjen jäsenten niumen pituuden onko validi
def my_length_check(form, field):
    if len(field.data.strip()) < 1:
        raise ValidationError('Liian lyhyt nimi')

# Tarkistaa ollaanko syöttämässä samanimisiä jäseniä
def onko_samoja(jasenet):
    for i in range(len(jasenet)):
        jasenet[i] = jasenet[i].upper().strip()
    onko_duplikaatteja = any(jasenet.count(element) > 1 for element in jasenet) 
    return onko_duplikaatteja

# Duplikaattijoukkueiden tarkistus onko samassa sarjassa jo joukkue samalla nimellä
def samoja_joukkueita(joukkue, sarja, avain):
    client = datastore.Client()
    results = client.query(kind="joukkueet").add_filter("sarja","=",sarja).fetch()
    joukkueet = []
    tulos = False
    for r in results:
        joukkueet.append(r)
        
    k = 0
    for j in joukkueet:
        if j['avain'] == avain:
            joukkueet.pop(k)
            k = k
        else: 
            k = k+1

    for i in range(len(joukkueet)):
        if joukkueet[i]['nimi'].lower().strip() == joukkue.lower().strip():
            tulos = True
    
    return tulos

# login reitti
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

# autentikointi reitti
@app.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    user = token.get('access_token')
    email = get_user_email(user)
    session['email_info'] = email['email']
    if user:
        session['user'] = user
    else:
        redirect('/')
    return redirect('/kilpailut')

# logout reitti
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('email_info', None)
    return redirect('/')



if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. You
    # can configure startup instructions by adding `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]
