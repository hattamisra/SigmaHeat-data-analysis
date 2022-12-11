import requests
import time as tm



def proccess_data(data):
    return {"city":data['name'],"datetime":tm.ctime(int(data['dt'])),"temp":data['main']['temp'],"humidity":data['main']['humidity']}



def get_weather_data(city='Hamburg',appid='API Token'): ### das ist meine eigene App ID, vorsichtig!!
    URL = "https://api.openweathermap.org/data/2.5/weather"
    PARAMS = {'q' :city ,'appid' :appid, 'units' : 'metric' }
    r = requests.get(url = URL, params = PARAMS)
    return proccess_data(r.json()), r.json()



while True: ## ctrl + C zu abbrechen
    data = get_weather_data('Hannover') # du kannst hier die Stadt verändern
    print(data[0])
    print(data[1])
    tm.sleep(2)