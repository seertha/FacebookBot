#Servidor de prueba Messenger Bot con saludo inicial
import json
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "EAAiFKZBnaUtEBAOOFjeEAaB8ZCGvv2hw2BM7EknrrrND4Er2z6ZA0jPceoK0YjK6vtPA3DNCTDjGp5zka6mRZCF7OUEqYKWnIpXD9BgobZAOybLPCrZAPqoxc6yqYG8BrwctwKGf1wlPKm5aME26vcFvxo5ENiHaCDO1OwkQlGJ3aAAH2GlXgkGRZCD0n3o59wZD"
FB_API_URL = "https://graph.facebook.com/v2.6/me/messages"

def verificar_webhook(req):
    mode = req.args.get("hub.mode")
    token = req.args.get("hub.verify_token")
    challenge = req.args.get("hub.challenge")
    #print("mode:{}\ntoken:{}\nchallenge:{}".format(mode,token,challenge))
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge
        else:
            return "403"

def eventoWebhook(data):
    #Obtiene el contenido del evento
    webhook_event = data['entry'][0]['messaging']
    #print("webhook_event:{}".format(webhook_event))

    #Obtener PSID del usuario
    sender_psid = webhook_event[0]['sender']['id']
    #print("sender_psid:{}".format(sender_psid))

    #Verifica el tipo de evento (message o postback) y llama a la funcion correspondiente
    if 'message' in webhook_event[0]:
        handleMessage(sender_psid, webhook_event[0]['message'])       
    elif 'postback' in webhook_event[0]:
        handlePostback(sender_psid,webhook_event[0]['postback'])
    return "EVENT_RECEIVED"

def handleMessage(sender_psid, webhook_event):
    if 'text' in webhook_event:
        if webhook_event['text'] == 'menu':
            menuInicio(sender_psid)
        else:
            respuesta = {"text":"Escriba 'menu' para ver las opciones"}
            callSendAPI(sender_psid,respuesta)

def handlePostback(sender_psid,webhook_postback):
    payload = webhook_postback['payload']
    #print("payload:{}".format(payload))
    if payload == 'inicio':
        menuInicio(sender_psid)
    elif payload == 'op1' or 'op2' or 'op3':
        opcion(sender_psid,payload)
    else:
        salir_menu(sender_psid)
        
            
    

def menuInicio(sender_psid):
    respuesta = {
        "attachment":{
            "type":"template",
            "payload":{
                "template_type":"generic",
                "elements":[
                    {
                        "title":"Menú 1 - Deslize para más opciones.",
                        "buttons":[
                            {
                               "type":"postback",
                               "title":"Opción1",
                               "payload":"op1"
                           },
                           {
                               "type":"postback",
                               "title":"Opción2",
                               "payload":"op2"
                           },
                           {
                               "type":"postback",
                               "title":"Opción3",
                               "payload":"op3"
                           }                    
                        ]
                    },
                    {
                        "title":"Menú 2",
                        "buttons":[
                            {
                               "type":"postback",
                               "title":"Salir",
                               "payload":"salir"

                            }
                        ]
                    }
                ]
            }
        }
    }
    callSendAPI(sender_psid,respuesta)

def opcion(sender_psid, payload):
    if payload == 'op1':
        respuesta = {"text":"opcion1"}
    elif payload == 'op2':
        respuesta = {"text":"opcion2"}
    elif payload == 'op3':
        respuesta = {"text":"opcion3"}
    else:
        return salir_menu(sender_psid)    
    callSendAPI(sender_psid,respuesta)
    menuInicio(sender_psid) 

def salir_menu(sender_psid):
    respuesta = {"text":"Gracias, vuelva pronto"}    
    callSendAPI(sender_psid,respuesta)


def callSendAPI(sender_psid, resp):
    #Mensaje de respuesta
    respJson = json.dumps(resp)
    request_body = {
        "recipient":{
            "id":sender_psid
        },
        "message":respJson
    }
    #request_bodyJson = json.dumps(request_body)

    #Enviar respuesta a la API de Facebook Messenger
    auth = {
        "access_token": VERIFY_TOKEN
    }
    respEnvio = requests.post(
        FB_API_URL,
        params=auth,
        json=request_body               
    )
    return respEnvio.json()

@app.route("/", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return verificar_webhook(request)
    if request.method == 'POST':
        payload = request.json
        #print("payload_org:{}".format(payload))
        if payload["object"] == "page":
            return eventoWebhook(payload)
        else:
            return "404"

if __name__ == "__main__":
    print("INICIO")
    app.run(debug=True)
