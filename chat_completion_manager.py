import openai
import json
import os
import psycopg2
import requests
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_token():
    
    payload=json.dumps({

    "DeviceId":"",
    "DeviceType":"Web",
    "DeviceToken" :"",
    "LocationId":2,
    "Username":"vikas",
    "Password":"123456"
})
    res=requests.request("POST",url="https://qa.careaxes.net/careaxes-qa-api/api/account/authenticate", headers={'accept':"application/json",'Content-Type': 'application/json'},data=payload)
    
    
    return res.json()['token']

def connect_to_db():
    return psycopg2.connect(
        host = os.getenv('PG_HOST'),
        database = os.getenv('PG_DB'),
        user = os.getenv('PG_USERNAME'),
        password = os.getenv('PG_PASSWORD')
    )

# Get meal details for a specific date and time_of_day
def get_meals_by_time(patient_id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT MenuDetails FROM Meals 
    """)
    meals = cur.fetchall()
    cur.close()
    conn.close()
    return meals

# Get appointment details for a specific patient, optionally after a given time
def get_appointments_by_patient(patient_id, time_after=None):
    conn = connect_to_db()
    cur = conn.cursor()
    if time_after:
        cur.execute("""
            SELECT DateTime, Type FROM Appointments 
            WHERE PatientID = %s AND DateTime > %s
        """, (patient_id, time_after))
    else:
        cur.execute("""
            SELECT DateTime, Type FROM Appointments 
            WHERE PatientID = %s
        """, (patient_id,))
    appointments = cur.fetchall()
    cur.close()
    conn.close()
    return appointments

# Get the name and specialty of the attending physician for a specific patient
def get_providers_by_patient(patient_id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT Physicians.Name, Physicians.Specialty FROM Physicians
        INNER JOIN Patients ON Physicians.PhysicianID = Patients.AttendingPhysicianID
        WHERE Patients.PatientID = %s
    """, (patient_id,))
    physician = cur.fetchone()
    cur.close()
    conn.close()
    return physician

# Get nurse details for a specific ward
def get_nurses_by_ward(ward_name):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT Name FROM Nurses WHERE AssignedWard = %s", (ward_name,))
    nurses = cur.fetchall()
    cur.close()
    conn.close()
    return nurses

# Get medication details for a specific patient
def get_medications_by_patient(patient_id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT Medications.Name, Medications.SideEffects FROM Medications
        INNER JOIN PatientMedications ON Medications.MedicationID = PatientMedications.MedicationID
        WHERE PatientMedications.PatientID = %s
    """, (patient_id,))
    medications = cur.fetchall()
    cur.close()
    conn.close()
    return medications

def get_complete_provider_information(providerName = None):

    conn = psycopg2.connect(
        host = os.getenv('PG_HOST'),
        database = "Careaxes_qa",
        user = os.getenv('PG_USERNAME'),
        password = os.getenv('PG_PASSWORD')
    )
    cur = conn.cursor()
    query = f''' select distinct pr."FullName" , sp1."SpecializationName",pr."Experience" from "DoctorSpecializationMap" sp
            join "Provider" pr on  sp."ProviderId" = pr."ProviderId"
            join "Specialization" sp1 on sp."SpecializationId" = sp1."SpecializationId" '''
    if providerName:
        query += f'''where pr."FullName" ilike '%{providerName}%' '''
    
    cur.execute(query)
    data =  cur.fetchall()
    cur.close()
    conn.close()
    print("the data is : ",data)
    providerinformation = '''  '''
    if len(data)>0:
        for i in data:
            providerinformation += f'''. Provider Name : {i[0]}  specialization : {i[1]}  experience : {int(i[2])}\n'''
    else:
        providerinformation = "Sorry we could not find any information"

    return providerinformation

def send_location(area):

    return "To reach us follow the map route https://maps.app.goo.gl/yUinRz4Wpy3QpBZT6"

def get_appointment_by_mobile(mobile):
    print("The mobile number is : ",mobile)

    conn = psycopg2.connect(
        host = "192.168.7.106",
        database = "fernandez_qa_08_May_2023",
        user = "emruser",
        password = "emruser123!"
    )
    cur = conn.cursor()

    query =f'''select ap."CreatedDate" as "AppointmentDate",
 pt."FullName" as "PatientName",pt."Mobile" as "PatientMobile",
    pr."FullName" as "ProviderName"  from "Appointment" ap
    join "Patient" pt on pt."PatientId" = ap."PatientId"
    join "Provider" pr on pr."ProviderId" = ap."ProviderId" where pt."Mobile" = '{mobile}' '''

    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()

    return data

def get_doctor_availabililty(doctorname=None,specialization=None,location =None):

    if not doctorname :
        return [{"_":"please provide doctorname and specialization for more information"}]
    

    conn = psycopg2.connect(
        host = "192.168.7.106",
        database = "fernandez_qa_08_May_2023",
        user = "emruser",
        password = "emruser123!"
    )
    cur = conn.cursor()
    # select "ProviderId" from "Provider" where lower("FullName") ilike lower('%{doctorname}%') limit 1 '''

    cur.execute(f'''SELECT "ProviderId" FROM "Provider" WHERE "FullName" ilike '%{doctorname}%' ; ''')
    data = cur.fetchall()
    if len(data)<1:
        return [{"_":"provider does not exists "}]
    
    print("The data is : ",data)
    providerId = data[0][0]


    import requests,json
    from datetime import datetime
    current_time = datetime.now().time()


    payload =json.dumps({
    "providerId": providerId,
    "patientId": 8164,
    "slotDate": "2023-11-16",
    "visitTypeId": 11,
    "offset": "+05:30",
    "timeZone": "Indian Standard Time",
    "time": "",
    "specializationId": 54,
    "locationId": 2,
    "consultationTypeId": 1,
    "providerAvailabilityId": 1139,
    "chargeTypesId": 42,
    "fromDate": "null"
    
    })

    headers2={
                    'Content-Type': 'application/json'                    
                        }
    res =  requests.post(r"https://uat.careaxes.net/uat-qa-api/api/provider-locations/fetch-new-slots",data= payload,headers=headers2)
    if res.json():
        data = res.json()['data']
        temp = []
        for i in data:
            formatted_time = datetime.strptime(i['slotName'], "%I:%M %p").time()

            if i['status']=='Available' and formatted_time>= current_time:
                temp.append({"slot time":i['slotName']})
    print(payload)
    return temp



class ChatCompletionManager:
    # Initialize the manager with a model and optional list of functions
    def __init__(self, model="gpt-3.5-turbo-0613", functions=None):
        self.model = model  # The model to use for completions
        self.messages = []  # Stores the conversation history
        self.functions = functions if functions else []  # Function descriptions

    # Add a message to the conversation history
    def add_message(self, role, content=None, function_name=None, function_data=None):
        message = {"role": role}  # Role can be 'system', 'user', or 'function'
        if content:  # Textual content of the message
            message["content"] = content
        if function_name and function_data:  # For function calls
            message["name"] = function_name
            message["content"] = json.dumps(function_data, default=str)
        self.messages.append(message)



    # Process a completion and decide whether to continue the conversation
    def process_and_continue(self):
        completion = self.make_completion()  # Get a completion from the API
        message = completion.choices[0].message  # Extract the message from the completion
        role = message.get('role', 'assistant')  # Default role is 'assistant'
        content = message.get('content')  # The content of the message

        function_call = message.get('function_call')  # Check for function calls in the message
        if function_call:  # If a function call is present
            function_name = function_call.get('name')  # Get the function name
            function_args = json.loads(function_call.get('arguments'))  # Get the arguments
            function_to_call = eval(function_name)  # Find the function (make sure this is safe!)
            function_result = function_to_call(**function_args)  # Call the function
            json_function_result = json.dumps(function_result, default=str)  # Convert result to JSON
            self.add_message("function", function_name=function_name, function_data=json_function_result)  # Add to history
        else:  # If no function call, just add the message to the history
            self.add_message(role, content=content)

    # Generate a completion using the OpenAI API
    def make_completion(self, auto_function_call=True):
        return openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            functions=self.functions,
            function_call="auto" if auto_function_call else None
        )

    # View the current conversation history
    def view_history(self):
        return self.messages

    # Print the conversation history in a human-readable format
    def print_history(self):
        for i, message in enumerate(self.messages):
            print(f"Message {i+1}: {message}")

    # Clear the conversation history
    def clear_history(self):
        self.messages = []
