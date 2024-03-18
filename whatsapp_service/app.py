import requests
import json
from flask import Flask, request

app = Flask(__name__)

@app.route('/saludar', methods=['GET'])
def Saludar():
    return "Hola mundo desde flask"

@app.route('/whatsapp', methods=['GET'])
def verifyToken():
    try:
        access_token = "E23431A21A991BE82FF3D79D5F1F8"
        token = request.args.get('hub.verify_token')
        challengue = request.args.get('hub.challengue')
        #mode = request.args.get('hub.mode')

        if token == access_token:
            return challengue
        else:
            return "Error", 400
    except Exception as e:
        print ("Error", e)
        return "Error", 400

    

@app.route('/whatsapp', methods=['POST'])
def Received_message():
    try:
        body = request.get_json()
        entry = body["entry"][0] 
        changes = entry["changes"][0] 
        value = changes["value"] 
        messages = value["messages"][0]
        text = messages["text"]
        body = text["body"]
        number = messages["from"]
        
        print(f"Este es el mensaje de la persona: ", body)
        
        answer_body = send_message(text, number)
        send_message_whatsapp = WhatsappService(answer_body)
        if send_message_whatsapp:
            print("Envio de mensaje correctamente")
        else:
            print("Error al enviar el mensaje")
        return "EVENT_RECEIVED"
    except Exception as e:
        print(e)
        return "EVENT_RECEIVED"
def WhatsappService(body):
    try:
        token = "E23431A21A991BE82FF3D79D5F1F8"
        api_url = "https://graph.facebook.com/v18.0/245533201976802/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = requests.post(api_url, data=json.dumps(body), headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)

def send_message(text, number):
    body = {
    "messaging_product": "whatsapp",    
    "recipient_type": "individual",
    "to": f"{number}",
    "type": "text",
    "text": {
        "body": f"Esta es la respuesta a la pregunta: {text}"
    }
    }
    
    return body 

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True)