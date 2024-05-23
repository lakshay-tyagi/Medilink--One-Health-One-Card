from flask import Flask, render_template, request 
import sqlite3
import base64
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from sklearn.metrics import f1_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
import joblib

app = Flask(__name__)

global user

model_path2 = 'model/Xception.h5' 

# Define the list of symptoms
l1=['back_pain','constipation','abdominal_pain','diarrhoea','mild_fever','yellow_urine',
'yellowing_of_eyes','acute_liver_failure','fluid_overload','swelling_of_stomach',
'swelled_lymph_nodes','malaise','blurred_and_distorted_vision','phlegm','throat_irritation',
'redness_of_eyes','sinus_pressure','runny_nose','congestion','chest_pain','weakness_in_limbs',
'fast_heart_rate','pain_during_bowel_movements','pain_in_anal_region','bloody_stool',
'irritation_in_anus','neck_pain','dizziness','cramps','bruising','obesity','swollen_legs',
'swollen_blood_vessels','puffy_face_and_eyes','enlarged_thyroid','brittle_nails',
'swollen_extremeties','excessive_hunger','extra_marital_contacts','drying_and_tingling_lips',
'slurred_speech','knee_pain','hip_joint_pain','muscle_weakness','stiff_neck','swelling_joints',
'movement_stiffness','spinning_movements','loss_of_balance','unsteadiness',
'weakness_of_one_body_side','loss_of_smell','bladder_discomfort','foul_smell_of urine',
'continuous_feel_of_urine','passage_of_gases','internal_itching','toxic_look_(typhos)',
'depression','irritability','muscle_pain','altered_sensorium','red_spots_over_body','belly_pain',
'abnormal_menstruation','dischromic _patches','watering_from_eyes','increased_appetite','polyuria','family_history','mucoid_sputum',
'rusty_sputum','lack_of_concentration','visual_disturbances','receiving_blood_transfusion',
'receiving_unsterile_injections','coma','stomach_bleeding','distention_of_abdomen',
'history_of_alcohol_consumption','fluid_overload','blood_in_sputum','prominent_veins_on_calf',
'palpitations','painful_walking','pus_filled_pimples','blackheads','scurring','skin_peeling',
'silver_like_dusting','small_dents_in_nails','inflammatory_nails','blister','red_sore_around_nose',
'yellow_crust_ooze']

disease=['Fungal infection','Allergy','GERD','Chronic cholestasis','Drug Reaction',
'Peptic ulcer diseae','AIDS','Diabetes','Gastroenteritis','Bronchial Asthma','Hypertension',
' Migraine','Cervical spondylosis',
'Paralysis (brain hemorrhage)','Jaundice','Malaria','Chicken pox','Dengue','Typhoid','hepatitis A',
'Hepatitis B','Hepatitis C','Hepatitis D','Hepatitis E','Alcoholic hepatitis','Tuberculosis',
'Common Cold','Pneumonia','Dimorphic hemmorhoids(piles)',
'Heartattack','Varicoseveins','Hypothyroidism','Hyperthyroidism','Hypoglycemia','Osteoarthristis',
'Arthritis','(vertigo) Paroymsal  Positional Vertigo','Acne','Urinary tract infection','Psoriasis',
'Impetigo']

custom_objects = {
    'f1_score': f1_score,
    'recall_m': recall_score,
    'precision_m': precision_score
}

loaded_model = joblib.load('dis_model.pkl')
model = load_model(model_path2, custom_objects=custom_objects)

def isDoctorExists(username):
    connection = sqlite3.connect('signup.db')
    cursor = connection.cursor()
    
    qry = "SELECT * FROM doctor WHERE username = ?"
    cursor.execute(qry, (username,))
    record = cursor.fetchone()
    
    connection.close()
    
    
    return bool(record)


@app.route('/DoctorRegisterAction', methods=['GET', 'POST'])
def DoctorRegisterAction():
    if request.method == 'POST':
        username = request.form.get('t1')
        password = request.form.get('t2')
        contact = request.form.get('t3')
        email = request.form.get('t4')
        address = request.form.get('t5')
        desc = request.form.get('t6')
        
        record = isDoctorExists(username)
        
        if not record:
            connection = sqlite3.connect('signup.db')
            cursor = connection.cursor()
            
            qry = "INSERT INTO doctor(username, password, phone_no, email, address, description) VALUES (?, ?, ?, ?, ?, ?)"
            values = (username, password, contact, email, address, desc)
            cursor.execute(qry, values)
            connection.commit()
            
            if cursor.rowcount == 1:
                data = "Signup Done! You can login now"
            else:
                data = "Error in signup process"
            
            connection.close()
        else:
            data = f"Given {username} already exists"
        
        return render_template('DoctorRegister.html', data=data)

    return render_template('DoctorRegister.html')



def isPatient(username):
    connection = sqlite3.connect('signup.db')
    cursor = connection.cursor()
    
    qry = "SELECT * FROM patient WHERE username = ?"
    cursor.execute(qry, (username,))
    record = cursor.fetchone()
    
    connection.close()
    
    
    return bool(record)


@app.route('/PatientRegisterAction', methods=['GET', 'POST'])
def PatientRegisterAction():
    if request.method == 'POST':
        username = request.form.get('t1')
        password = request.form.get('t2')
        contact = request.form.get('t3')
        email = request.form.get('t4')
        address = request.form.get('t5')
        desc = request.form.get('t6')
        
        record = isPatient(username)
        
        if not record:
            connection = sqlite3.connect('signup.db')
            cursor = connection.cursor()
            
            qry = "INSERT INTO patient(username, password, phone_no, email, address, description) VALUES (?, ?, ?, ?, ?, ?)"
            values = (username, password, contact, email, address, desc)
            cursor.execute(qry, values)
            connection.commit()
            
            if cursor.rowcount == 1:
                data = "Signup Done! You can login now"
            else:
                data = "Error in signup process"
            
            connection.close()
        else:
            data = f"Given {username} already exists"
        
        return render_template('PatientRegister.html', data=data)

    return render_template('PatientRegister.html')

@app.route("/PatientLoginAction", methods=['POST'])
def PatientLoginAction():
    global user
    mail1 = request.form.get('t1', '')
    password1 = request.form.get('t2', '')
    user = mail1
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("SELECT `username`, `password` FROM patient WHERE `username` = ? AND `password` = ?", (mail1, password1))
    data = cur.fetchone()
    con.close()

    if data is None:
        context = 'Invalid Details.'
        return render_template("PatientLogin.html", data=context)
    
    context = 'Welcome ' + mail1
    return render_template("PatientScreen.html", data=context)

@app.route("/DoctorLoginAction", methods=['POST'])
def DoctorLoginAction():
    global user
    mail1 = request.form.get('t1', '')
    password1 = request.form.get('t2', '')
    user = mail1
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("SELECT `username`, `password` FROM doctor WHERE `username` = ? AND `password` = ?", (mail1, password1))
    data = cur.fetchone()
    con.close()

    if data is None:
        context = 'Invalid Details.'
        return render_template("DoctorLogin.html", data=context)
    
    context = 'Welcome ' + mail1
    return render_template("DoctorScreen.html", data=context)


def get_all_doctors():
    try:
        con = sqlite3.connect('signup.db')  
        cur = con.cursor()
        cur.execute("SELECT `username` FROM doctor")  
        rows = cur.fetchall()
        con.close()

        doctor_names = [row[0] for row in rows]
        
        return doctor_names
    except sqlite3.Error as e:
        
        return []

@app.route('/BookAppointment', methods=['GET'])
def BookAppointment():
    doctor_names = get_all_doctors()
    
    return render_template('BookAppointment.html', doctor_names=doctor_names)



@app.route("/BookAppointmentAction", methods=['POST'])
def BookAppointmentAction():
    global user  

    dname = request.form.get('t1', '')
    des = request.form.get('t2', '')
    date = request.form.get('t3', '')
    
    try:

        connection = sqlite3.connect('signup.db')
        cursor = connection.cursor()
                
        qry = "INSERT INTO appointment(user, name, description, date) VALUES (?, ?, ?, ?)"
        values = (user, dname, des, date)
        cursor.execute(qry, values)
        connection.commit()

        if cursor.rowcount == 1:
            data = "Appointment Booked"
        else:
            data = "Error in process"

    except sqlite3.Error as e:
        
        data = f"Error: {str(e)}"
    except Exception as e:
        
        data = f"An error occurred: {str(e)}"
    finally:
        connection.close()

    return render_template("BookAppointment.html", data=data)



@app.route('/ViewDoctor', methods=['GET'])
def view_doctor():
    connection = sqlite3.connect('signup.db')
    cursor = connection.cursor()

    cursor.execute("SELECT username, phone_no, email, address, description FROM doctor")
    doctors = cursor.fetchall()

    connection.close()

    return render_template('ViewDoctor.html', doctors=doctors)


@app.route('/ViewAppointments', methods=['GET'])
def view_appointments():
    global user  
    
    connection = sqlite3.connect('signup.db')
    cursor = connection.cursor()

    cursor.execute("SELECT user, name, description, date FROM appointment WHERE name = ?", (user,))
    appointments = cursor.fetchall()

    connection.close()

    return render_template('ViewAppointments.html', appointments=appointments)


def get_all_users():
    try:
        con = sqlite3.connect('signup.db')  
        cur = con.cursor()
        cur.execute("SELECT user, name, description, date FROM appointment WHERE name = ?", (user,)) 
        rows = cur.fetchall()
        con.close()

        doctor_names = [row[0] for row in rows]
        
        return doctor_names
    except sqlite3.Error as e:
        
        return []


@app.route('/GivePrescription', methods=['GET'])
def GivePrescription():
    username_names = get_all_users()
   
    return render_template('GivePrescription.html', username_names=username_names)

@app.route("/GivePrescriptionAction", methods=['POST'])
def GivePrescriptionAction():
    global user

    uname = request.form.get('t1', '')  
    des = request.form.get('t2', '')   
    

    try:
        
        connection = sqlite3.connect('signup.db')
        cursor = connection.cursor()
        
        
        qry = "INSERT INTO prescription(uname, user, des, file) VALUES (?, ?, ?, ?)"
        values = (uname, user, des, request.files['t3'].read()) 
        cursor.execute(qry, values)
        connection.commit()

        if cursor.rowcount == 1:
            data = "Prescription Added Successfully"
        else:
            data = "Error in process"

    except sqlite3.Error as e:
        data = f"Error: {str(e)}"
    except Exception as e:
        data = f"An error occurred: {str(e)}"
    finally:
        connection.close()

    return render_template("GivePrescription.html", data=data)



@app.route('/ViewPrescriptions', methods=['GET'])
def ViewPrescriptions():
    global user  
    
    connection = sqlite3.connect('signup.db')
    cursor = connection.cursor()

    cursor.execute("SELECT uname, user, des, file FROM prescription WHERE uname = ?", (user,))
    prescriptions = cursor.fetchall()

    modified_prescriptions = []  

    for prescription in prescriptions:
        image_data = prescription[3]
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        modified_prescription = list(prescription)  
        modified_prescription[3] = encoded_image  
        modified_prescriptions.append(tuple(modified_prescription))  

    connection.close()

    return render_template('ViewPrescriptions.html', prescriptions=modified_prescriptions)


@app.route('/Prediction', methods=['GET'])
def Prediction():
    username_names = get_all_users()
    
    return render_template('Prediction.html', username_names=username_names)

@app.route('/PredictionAction', methods=['POST'])
def PredictionAction():
    global user

    uname = request.form.get('t1', '')

    if 'files' in request.files:
        image_file = request.files['files']
        if image_file.filename != '':
            image_path = 'temp_image.jpg'
            image_file.save(image_path)

            image = load_img(image_path, target_size=(224, 224))
            image = img_to_array(image)
            image = image / 255
            image = np.expand_dims(image, axis=0)

            result = np.argmax(model.predict(image))

            result_mapping = {0: 'Brain Glioma', 1: 'Brain Menin', 2: 'Brain tumor', 3: 'Breast Benign', 4: 'Breast Malignant', 5: 'Fractured', 6: 'Glioma', 7: 'Kidney Normal', 8: 'Kidney Tumor', 9: 'Meningioma', 10: 'Not fractured', 11: 'No Tumor', 12: 'Oral Normal', 13: 'Oral squamous cell carcinoma', 14: 'Pituitary'}
            if result in result_mapping:
                disease = result_mapping[result]
            else:
                disease = "Unknown"

            try:
                connection = sqlite3.connect('signup.db')
                cursor = connection.cursor()

                qry = "INSERT INTO result(uname, user, dia, file) VALUES (?, ?, ?, ?)"
                with open(image_path, 'rb') as file:
                    file_data = file.read()
                values = (uname, user, disease, file_data)
                cursor.execute(qry, values)
                connection.commit()

                if cursor.rowcount == 1:
                    data = "Diagnosis Completed Successfully and result is " + disease
                else:
                    data = "Error in process"

            except sqlite3.Error as e:
                data = f"Error: {str(e)}"
            except Exception as e:
                data = f"An error occurred: {str(e)}"
            finally:
                connection.close()

            return render_template("Prediction.html", data=data)

    return "No file uploaded."



@app.route('/ViewResult', methods=['GET'])
def ViewResult():
    global user  
    
    connection = sqlite3.connect('signup.db')
    cursor = connection.cursor()

    cursor.execute("SELECT uname, user, dia, file FROM result WHERE uname = ?", (user,))
    prescriptions = cursor.fetchall()

    modified_prescriptions = []  

    for prescription in prescriptions:
        image_data = prescription[3]
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        modified_prescription = list(prescription)  
        modified_prescription[3] = encoded_image  
        modified_prescriptions.append(tuple(modified_prescription))  

    connection.close()

    return render_template('ViewResult.html', prescriptions=modified_prescriptions)

@app.route('/ViewResult', methods=['GET', 'POST'])
def ViewResults():
    if request.method == 'GET':
       return render_template('ViewResult.html', msg='')    

@app.route('/ViewPrescriptions', methods=['GET', 'POST'])
def ViewPrescriptionss():
    if request.method == 'GET':
       return render_template('ViewPrescriptions.html', msg='')


@app.route('/Prediction', methods=['GET', 'POST'])
def Predictions():
    if request.method == 'GET':
       return render_template('Prediction.html', msg='')
    

   
@app.route('/DiseasePrediction', methods=['GET', 'POST'])
def diseaseprediction():
    if request.method == 'GET':
       return render_template('DiseasePrediction.html', symptoms=l1)
    if request.method == 'POST':
        try:
        # Get selected symptoms from the form
            selected_symptoms = [request.form[f"symptom{i}"] for i in range(1, 6)]

        # Prepare input data with all symptoms
            input_data = [1 if symptom in selected_symptoms else 0 for symptom in l1]

        # Reshape input data to match model's expected shape
            input_data = np.array(input_data).reshape(1, -1)

        # Make prediction
            prediction = loaded_model.predict(input_data)

        # Get the predicted disease
            predicted_disease = disease[prediction[0]]
        
            return render_template('DiseasePrediction.html', symptoms=l1, predicted_disease=predicted_disease)
        except KeyError:
        # Handle missing keys (e.g., if form data is incomplete)
            return "Error: Incomplete form submission"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
       return render_template('index.html', msg='')

@app.route('/GivePrescription', methods=['GET', 'POST'])
def GivePrescriptions():
    if request.method == 'GET':
       return render_template('GivePrescription.html', msg='')

@app.route('/ViewAppointments', methods=['GET', 'POST'])
def ViewAppointmentss():
    if request.method == 'GET':
       return render_template('ViewAppointments.html', msg='')

@app.route('/ViewDoctor', methods=['GET', 'POST'])
def ViewDoctors():
    if request.method == 'GET':
       return render_template('ViewDoctor.html', msg='')

@app.route('/BookAppointment', methods=['GET', 'POST'])
def BookAppointmentss():
    if request.method == 'GET':
       return render_template('BookAppointment.html', msg='')

@app.route('/PatientLogin', methods=['GET', 'POST'])
def PatientLogin():
    if request.method == 'GET':
       return render_template('PatientLogin.html', msg='')

@app.route('/DoctorLogin', methods=['GET', 'POST'])
def DoctorLogin():
    if request.method == 'GET':
       return render_template('DoctorLogin.html', msg='')

@app.route('/PatientScreen', methods=['GET', 'POST'])
def PatientScreen():
    if request.method == 'GET':
       return render_template('PatientScreen.html', msg='')

@app.route('/DoctorScreen', methods=['GET', 'POST'])
def DoctorScreen():
    if request.method == 'GET':
       return render_template('DoctorScreen.html', msg='')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
       return render_template('index.html', msg='')
 
@app.route('/PatientRegister', methods=['GET', 'POST'])
def PatientRegister():
    if request.method == 'GET':
       return render_template('PatientRegister.html', msg='') 

@app.route('/DoctorRegister', methods=['GET', 'POST'])
def DoctorRegister():
    if request.method == 'GET':
       return render_template('DoctorRegister.html', msg='') 

if __name__ == '__main__':
    app.run()       
