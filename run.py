from flask import Flask, render_template as rt, url_for, request, flash, redirect
import datetime 
import requests


class Vreme:
	pass


def neutral(grad):
    global k
    k=0
    return prognoza(grad)

def napred(grad):
    global k
    k+=1
    if k==40:
        k=39
    return prognoza(grad)

def nazad(grad):
    global k
    k-=1
    if k==-1:
        k=0
    return prognoza(grad)

def prognoza(grad):
    
    if ',' not in grad:
        grad=grad+',RS'
    kljuc='e91a20a3187eb120ff46939973a01438'
    url='http://api.openweathermap.org/data/2.5/forecast'
    params={'APPID':kljuc, 'q':grad, 'lang':'en', 'units':'metric'}
    odgovor=requests.get(url,params)
    vreme=odgovor.json()
    
    stanje=Vreme()

    stanje.grad=grad
    
    stanje.temperatura=vreme['list'][k]['main']['temp']
    stanje.pritisak=vreme['list'][k]['main']['pressure']
    stanje.vlaznost=vreme['list'][k]['main']['humidity']
    stanje.ikona=vreme['list'][k]['weather'][0]['icon']
    
    opis=vreme['list'][k]['weather'][0]['description']
    stanje.opis=opis.capitalize()

    datum=vreme['list'][k]['dt_txt']
    stanje.datum=datetime.datetime.strptime(datum,'%Y-%m-%d %H:%M:%S')
    dan=stanje.datum.strftime('%a')
    stanje.uv=uv_dicto[dan]
    
    vetar=vreme['list'][k]['wind']['speed']
    stanje.vetar=int(vetar*3.6)

    return stanje

def uv_f(grad):

	global uv_dicto
	uv_dicto={}

	if ',' not in grad:
 		grad=grad+',RS'
    
	kljuc_geo = '8edff4ad42134e689149911c9ad897d8'
	url_geo = 'https://api.opencagedata.com/geocode/v1/json'
	params_geo={'key':kljuc_geo, 'q':grad}
	odgovor_geo=requests.get(url_geo,params_geo)
	vreme_geo=odgovor_geo.json()
	
	lat=vreme_geo['results'][0]['geometry']['lat']
	lng=vreme_geo['results'][0]['geometry']['lng']

	kljuc='e91a20a3187eb120ff46939973a01438'
	url_uv='http://api.openweathermap.org/data/2.5/uvi/forecast'
	params_uv={'APPID':kljuc, 'lat':lat,'lon':lng,'cnt':6}
	odgovor_uv=requests.get(url_uv,params_uv)
	vreme_uv=odgovor_uv.json()
	
	for dicto in vreme_uv:
		datum=dicto['date_iso']
		dt=datetime.datetime.strptime(datum, '%Y-%m-%dT%H:%M:%SZ')
		dan=dt.strftime('%a')
		uv=dicto['value']
		if uv<3:
			uv_dicto[dan]= uv,'#53c653','Low'
		elif uv<6:
			uv_dicto[dan]= uv,'#ffd11a', 'Medium'
		elif uv<8:
			uv_dicto[dan]= uv,'#ff9900', 'High'
		elif uv<11:
			uv_dicto[dan]= uv,'#ff531a', 'Very high'
		else:
			uv_dicto[dan]= uv,'#9900cc', 'Extreme'
		
	
app=Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

@app.route('/', methods=['GET','POST'])
def home():
	return rt (('base.html'))


@app.route('/weather/<string:grad>', methods=['GET','POST'])
def podaci(grad):
	#grad = request.form['grad']
	try: 
		uv=uv_f(grad)
		status=neutral(grad)
	except:
		if ',' not in grad:
			flash('Use: '+grad+', Alpha-2 code (ex: New York, US)')
		else:
			flash('City with that Alpha-2 code does not exist in data base')
		return redirect(url_for('home'))
	return rt('podaci.html', stanje=status)


@app.route('/weather/<string:grad>/ahead', methods=['GET','POST'])
def plus(grad):
	#grad = request.form['grad']
	try:
		status=napred(grad)
	except:
		if ',' not in grad:
			flash('Use: '+grad+', Alpha-2 code (ex: New York, US)')
		else:
			flash('City with that Alpha-2 code does not exist in data base')
		return redirect(url_for('home'))
	return rt('podaci.html', stanje=status)


@app.route('/weather/<string:grad>/back', methods=['GET','POST'])
def minus(grad):
	#grad = request.form['grad']
	try:
		status=nazad(grad)
	except:
		if ',' not in grad:
			flash('Use: '+grad+', Alpha-2 code (ex: New York, US)')
		else:
			flash('City with that Alpha-2 code does not exist in data base')
		return redirect(url_for('home'))
	return rt('podaci.html', stanje=status)