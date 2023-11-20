from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import os
import json
import openai
from chat_completion_manager import ChatCompletionManager  # Import your ChatCompletionManager class
from flask import Flask, render_template, request, jsonify, redirect,make_response
import json
import threading
from dotenv import load_dotenv
load_dotenv()
openai.api_key = ""





app= Flask(__name__)
function_descriptions = [
    {
        "name": "get_meals_by_time",
        "description": "Retrieve meal details for a patient on a specific date and time of day.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "integer",
                    "description": "The ID of the patient."
                }
            },
            "required": ["patient_id"]
        }
   
     },
    # {
    #     "name": "get_appointments_by_patient",
    #     "description": "Retrieve appointment details for a specific patient, optionally filtering by time.",
    #     "parameters": {
    #         "type": "object",
    #         "properties": {
    #             "patient_id": {
    #                 "type": "integer",
    #                 "description": "The ID of the patient."
    #             },
    #             "time_after": {
    #                 "type": "string",
    #                 "format": "datetime",
    #                 "description": "Optional. Filter appointments occurring after this date and time."
    #             }
    #         },
    #         "required": ["patient_id"]
    #     }
    # },
    {
        "name": "get_providers_by_patient",
        "description": "Retrieve provider assignments for a specific patient.", 
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "integer",
                    "description": "The ID of the patient."
                }
            },
            "required": ["patient_id"]
        }
    },
    {
        "name": "get_nurses_by_ward",
        "description": "Retrieve nurse assignments for a specific ward.",
        "parameters": {
            "type": "object",
            "properties": {
                "ward_name": {
                    "type": "string",
                    "description": "The name of the ward."
                }
            },
            "required": ["ward_name"]
        }
    },
    {
        "name": "get_medications_by_patient",
        "description": "Retrieve medication details for a specific patient.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "integer",
                    "description": "The ID of the patient."
                }
            },
            "required": ["patient_id"]
        }
    },
   
    {


        "name":"get_complete_provider_information",
        "description" : "Retrieve complete provider infomation like name,specialization,experience",
         "parameters": {
            "type": "object",
            "properties": {
                 "providerName": {
                    "type": "string",
                    
                    "description": "Optional. Filter according to provider name"
                }
            }
        }
       
        
    },

    {
        "name":"get_appointment_by_mobile",
        "description":"Retrieve patient appointment information which also contains doctor info and patient mobile",
        "parameters":{
            "type":"object",
            "properties":{
                "mobile":{"type":"string","description":"The mobile number of patient"}
            },
            "required":["mobile"]
        }
    },
    {
        "name":"send_location",
        "description": "Retrieve location of hospital,reach hospital,reach us ",
        "parameters" : {
            "type":"object",
            "properties":{
                "area":{"type":"string","description":"give the area name or location name"}
            },
            "required":["area"]
        }
    },
    {
        "name":"get_doctor_availabililty",
        "description":"Retrieve if doctor is available or not which also contains doctor information and available timings",
        "parameters":{
            "type":"object",
            "properties":{
                "doctorname":{"type":"string","description":"The name of doctor or provider"},
                "location":{"type":"string","description":"The name of location"},
                
            }
            
        }

    }
    
]


def conversationalAi(prompt):
    
    manager = ChatCompletionManager(functions=function_descriptions)
    manager.clear_history()

    # Check if the system message has already been added
    initial_messages = manager.view_history()
    if not initial_messages or initial_messages[0]["role"] != "system":
        # Add the system message if it's not in the chat history
        manager.add_message(
            "system",
            """You are an Ai patient assistant working in an hospital with great doctors. You are answering questions that the patient may have about the doctors
            in the hospital, about meals, about appointments, etc. Your job is to be the patient's caretaker. Be understanding about their problems
            and try to offer a positive outlook while answering any questions they have. You should also be as prompt with your responses as possible.
            Start by introducing yourself as Amy and ask the patient what they would like help with. It is important that you dont
            mention to the patient that you received the patient_id."""
        )
        manager.process_and_continue()

    # Retrieve the initial system and assistant messages
    initial_messages = manager.view_history()
    

    user_message = prompt
    user_message_with_patient_id = user_message 

    manager.add_message('user', user_message_with_patient_id)

    manager.process_and_continue()

    messages_to_send = []

    latest_message = manager.view_history()[-1]
    role = latest_message.get('role')

    if role == 'function':
        function_name = latest_message.get('name')
        function_output = latest_message.get('content')
        function_info = f'Name: {function_name}, Output: {function_output}'
        messages_to_send.append({'content': function_info, 'role': 'function'})

        # Process the conversation again to get the assistant's response
        manager.process_and_continue()

    latest_message = manager.view_history()[-1]
    assistant_response = latest_message.get('content')
    messages_to_send.append({'content': assistant_response, 'role': 'assistant'})
    return assistant_response

API_TOKEN='''
EAAHizBobRpoBAKe1hy91XwmG8l4SmWCt7I98QBr0s3jTZBIaDQtNx7ZC81YML46lTi0sVSNalyqtOuqZCbSeIhtTzZAJp
8fnNPTM50PJMwbZBqNLpvVI2hgr7mmxC8fZBZCZBIRM15UZAUc34PYfT28ijv6PokXUGjo75OqtibSAW18Kdf1XEQaTbaM44n3qmS8fpyQlBZAxcDwQZDZD
'''.replace("\n","")

metaUrl='https://graph.facebook.com/v16.0/105391989199319/messages'

@app.route("/webhook",methods=["GET","POST"])
def function_webhook():
    if request.method == "GET":
        myResponse = make_response(request.args['hub.challenge'])
        myResponse.status_code = 200
        myResponse.content_type ='application/json'
        return myResponse
    
    if request.method=="POST":
        
        try:
            headers = {
                'Authorization': f"Bearer {API_TOKEN}",
                'Content-Type': 'application/json'
                    }
            
            data = request.get_json() #getting  information from webhook
            
            #print(data['entry'][0]['changes'][0])
            body=data['entry'][0]['changes'][0]['value']
            if 'messages' in body:
              
                clientMessage = body['messages'][0]['text']['body']
                mobile=body['contacts'][0]['wa_id']
                name = data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
                clientMessage = f"Hi my name is  {name}  and my mobile number is {mobile[2:]}. "+ clientMessage 
                print("Message: %s", clientMessage)
                    
                result = conversationalAi(clientMessage)
                print("The model output is : ",result)

                payload=json.dumps({
                        "messaging_product" :"whatsapp",
                        "to":f"{mobile}",
                        "text":{"body":f"{result}"}
                    })
                headers = {
            
                'Authorization': f"Bearer {API_TOKEN}",
                'Content-Type': 'application/json'
                    }
                response = requests.request("POST", metaUrl, headers=headers, data=payload)
        except Exception as e:
            print("The error occured : ",str(e)) 

        return "success",200
    
if __name__ == "__main__":
    app.run(debug=True)