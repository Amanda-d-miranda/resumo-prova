import requests


#dados de SP
URL = 'https://api.open-meteo.com/v1/forecast?latitude=-23.5505&longitude=-46.6333&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m'

resposta = requests.get(URL)

dados = resposta.json()

print(resposta.status_code)

if resposta.status_code == 200:
    dados = resposta.json()

    print(dados)

else:
    print('Erro')

clima = dados['current']
print(dados)


while True:
    print('=========== MENU ==========')
    print('Digite: 1/ Temperatura')
    print('Digite: 2/ Humidade')
    print('Digite: 3/ Data')
    print('Digite: 4/ Elevação')
    print('Digite: 5/ Velocidade do Vento')
    print('Digite: 6/ Sair')

    ver = input('Digite o que você quer consultar:')

    if ver == '1':
        print('Temperatura:', clima['temperature_2m'], '°C')

    elif ver == '2':
        print('Humidade:', clima['relative_humidity_2m'], 'UR%')
    

    elif ver == '3':
        print('Data:', clima['time'])


    elif ver == '4':
        print('Elevação:', dados['elevation'])


    elif ver == '5':
        print('Velocidade:', clima['wind_speed_10m'],'K/h')

    elif ver == '6':
        print('Consulta Finalizada!!')
        break



        