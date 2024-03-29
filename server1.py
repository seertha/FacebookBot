#Servidor de prueba para implemnentar un bot en la aplicación messenger de Facebook.
import json
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "<Token_de_verificación>"
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

def callSendAPI(sender_psid, respJson):
    #Mensaje de respuesta
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



def handleMessage(sender_psid, webhook_event):
    print("Evento message")
    if 'text' in webhook_event:
        respuesta = {
            "text": 'Enviaste el mensaje "{}", ahora envia una imagen'.format(webhook_event['text'])
        }
#        respJson = json.dumps(respuesta)
    elif 'attachments' in webhook_event:
        #respuesta = {
        #    "text": "Imagen recibida"
        #}
        attachment_url = webhook_event['attachments'][0]['payload']['url']
        #print("webhook_attach:{}".format(webhook_event['attachments']))
        print("attachment_url:{}".format(attachment_url))
        respuesta = {
            "attachment":{
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "Esta es su imagen?",
                        "subtitle": "Haga Click para responder",
                        "image_url": attachment_url,
                        "buttons": [
                            {
                                "type": "postback",
                                "title": "Sí!",
                                "payload": "yes",
                            },
                            {
                                "type": "postback",
                                "title": "No!",
                                "payload": "no"
                            }
                        ],
                    }]
                }
            }
        }
    else:
        print("Error en diccionario, llave no encontrada")
        return "404"    
    #Envia el mensaje de respuesta
    respJson = json.dumps(respuesta)
    callSendAPI(sender_psid, respJson)

def handlePostback(sender_psid, webhook_event):
    print("Evento postback") 
    #print("Evento postback:{}".format(webhook_event))
    payload = webhook_event['payload']

    #Enviar respuesta
    if payload == 'yes':
        respuesta = {
            "text": "Gracias!"
        }
    elif payload == 'no':
        respuesta = {
            "text": "Menudo Error el mío!"
        }
    respJson = json.dumps(respuesta)
    callSendAPI(sender_psid, respJson)

def eventoWebhook(data):
    #Obtiene el contenido del evento
    webhook_event = data['entry'][0]['messaging']
    print("webhook_event:{}".format(webhook_event))

    #Obtener PSID del usuario
    sender_psid = webhook_event[0]['sender']['id']
    print("sender_psid:{}".format(sender_psid))

    #Verifica el tipo de evento (message o postback) y llama a la funcion correspondiente
    if 'message' in webhook_event[0]:
        handleMessage(sender_psid, webhook_event[0]['message'])        
    elif 'postback' in webhook_event[0]: #webhook_event[0]['postback']:
        handlePostback(sender_psid, webhook_event[0]['postback'])    
    return "EVENT_RECEIVED" 

@app.route("/", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return verificar_webhook(request)
    if request.method == 'POST':
        payload = request.json
        print("payload_org:{}".format(payload))
        if payload["object"] == "page":
            return eventoWebhook(payload)
        else:
            return "404"
         

if __name__== "__main__":
    app.run(debug=True)
