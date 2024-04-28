from flask import Flask, render_template,Blueprint,request,jsonify,session,flash,url_for,redirect,get_flashed_messages,abort
import website.models  
from functools import wraps
from werkzeug.utils import secure_filename
import os
from wtforms import FileField, SubmitField
from flask_wtf.file import FileRequired
from flask_wtf import FlaskForm
import base64
import io
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
import numpy as np 
import website.models
from functools import wraps
from flask import current_app
import pandas as pd 
#from website.datafile import upload_to_db
import sqlite3
import pandas as pd
from flask import request, render_template, jsonify, redirect, flash
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd
import os
from io import BytesIO
from io import TextIOWrapper
ALLOWED_EXTENSIONS = {'csv'}


auth=Blueprint('auth',__name__,template_folder='../Templates')


def is_logged_in(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get('logged_in'):
            return view(*args, **kwargs)
        else:
            abort(403)  # Forbidden
    return wrapped_view

def is_admin(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get('logged_in') and session.get('role') == 'admin':
            return view(*args, **kwargs)
        else:
            abort(403)  # Forbidden
    return wrapped_view

@auth.route("/logout",methods=['GET','POST'])
def logout():
    # Clear the user session
    session.clear()
    # Redirect the user to the login page or any other appropriate page
    return redirect(url_for('auth.login'))



@auth.route("/login",methods=['GET','POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = website.models.authenticate_user(email, password)
        if user is not None:
            
            session['user_id'] = user[0]
            #session['password'] = user[1]
            session['role'] = user[2]
            session['logged_in'] = True
            if user[2] == 'admin':
                # If user is admin, render admin page
                #return render_template("AdminViewUsers.html")
                  #users_data = [{'email': user[0], 'username': user[1], 'role': user[2]} for user in website.models.users()]
                  #return render_template("AllUsers.html", users_data=users_data)
                 return redirect(url_for('auth.admin_home'))
            else:
                # If user is regular user, render user page
                return render_template("User-Page.html")

        else:
                flash('Invalid email or password', 'error')
                return render_template("login.html")
    else:       
                
                return render_template("login.html")

@auth.route("/admin/data", methods=['GET', 'POST'])
@is_admin
def admin_data() : 
     if request.method == 'POST':
        email = request.form['email']
        components = request.form['components']
        date = request.form['date']
        value = request.form['value']
        website.models.insert_data(email, components, date, value)
        flash('Data added successfully!', 'success')  # Flash message
     return render_template("AdminAddData.html")
     
       
     


@auth.route("/admin/Add",methods=['GET','POST'])
@is_admin
def Admin() :
    if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            website.models.admin(email,username,password)
            flash('Account added successfully!', 'success')  # Flash message
            # Redirect to the same page after adding account
    return render_template("AdminAdd.html");
    






@auth.route('/user/usercomponents')
@is_logged_in

def userComponents():
        
        #if 'user_id' in session:
        user_id = session.get('user_id')
             
        components= [{'component': component[0], 'value': component[1], 'date': component[2]} for component in website.models.UserComponents(user_id)]
        #components = [('Component A', 100, '2024-03-28'),('Component B', 200, '2024-03-29'),('Component C', 300, '2024-03-30')]
        return render_template("userComponents.html", components_data=components)


    

@auth.route("/admin/dashboard", methods=['GET', 'POST'])
@is_admin
def admin_dashboard():
    
    users_data = [{'email': user[0], 'username': user[1],'password': user[2], 'role': user[3],'last_login':user[4]  } for user in website.models.users()]
    
    return render_template("AllUsers.html", users_data=users_data)


@auth.route("/admin/home", methods=['GET'])
@is_admin
def admin_home():
    return render_template("admin_home.html")

@auth.route('/admin/UCom')
def AdminUserComponents() : 
      
    user_id = request.args.get('user_id')
    components = [{'component': component[0], 'value': component[1], 'date': component[2]} for component in website.models.UserComponents(user_id)]
    return render_template("userComponents.html", components_data=components)
@auth.route('/admin/graph')
@is_admin
def plot():
    # Sample data
    user_id = request.args.get('user_id')
    components = {
        'Date': [component[2] for component in website.models.UserComponents(user_id)],
        'Value': [component[1] for component in website.models.UserComponents(user_id)],
        'Component': [component[0] for component in website.models.UserComponents(user_id)]
    }

    # Create DataFrame
    df = pd.DataFrame(components)

    # Convert 'Date' column to datetime type
    df['Date'] = pd.to_datetime(df['Date'])

    # Set 'Date' as index
    df.set_index('Date', inplace=True)

    # Filter data for components 'P', 'NA', 'Ph'
    df_components = {}
    for component in ['P', 'NH4', 'Ph']:
        df_component = df[df['Component'] == component]
        df_components[component] = df_component[~df_component.index.duplicated()].resample('M').ffill()

    # Plotting
    plots = []
    for component, df_component in df_components.items():
        plt.figure(figsize=(10, 6))
        plt.plot(df_component.index, df_component['Value'], marker='o', linestyle='-')
        plt.title(f'Component {component} - Value Over Time')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.grid(True)

        # Format date on x-axis
        date_form = DateFormatter("%Y.%m.%d")  # Customize the date format as per your preference
        plt.gca().xaxis.set_major_formatter(date_form)
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

        # Save the plot as a PNG image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        plots.append({'component': component, 'image_base64': image_base64})

    # Render template with plots
    return render_template('AdminGraphs.html', plots=plots)

    
#------------------------------------File Functions----------------------------------------------------------------
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def has_required_columns(file_path):
    try:
        df = pd.read_csv(file_path)
        return len(df.columns) == 5 and set(df.columns) == {'id', 'user_id', 'component', 'value', 'date'}
    except Exception as e:
        print(f"Error checking columns: {e}")
        return False

def readFile(filename):
    print ("Opening the file...")
    f=open("uploads/%s"%filename,'r')
    print ("Reading the file...")
    text=[]
    for line in f:
        text.append(line)
    return render_template('test.html',filename=filename,content=text) 
class UploadFileForm (FlaskForm):
    file = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Upload File')

@auth.route('/uploads', methods=['GET', 'POST'])
@is_logged_in
def upload_to_db():
    form = UploadFileForm()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('website/static', filename)
            file.save(file_path)
            
            try:
                db_file = "user_database.db"  # Update with your actual database file path
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                print('Opened database successfully')
                
                # Open the saved file for reading in binary mode
                with open(file_path, 'rb') as my_file:
                    # Wrap it with BytesIO to make it compatible with pandas
                    file_wrapper = BytesIO(my_file.read())
                    # Skip header row
                    next(file_wrapper)
                    # Read CSV using pandas
                    df = pd.read_csv(file_wrapper, delimiter=';|,')
                    print ("df is open")

                # Handle file

                if not df.empty:
                    insert_query = "INSERT INTO user_components (id, user_id, component, value, date) VALUES (?, ?, ?, ?, ?)"
                    print("df not empty")
            
                    if 'user_id' in session:
                        user_id = session.get('user_id')
                        for _, row in df.iterrows():
                            print(row)
                        # Construct the SQL INSERT query
                  
                        # Get user ID from current user
                      

                            data = (row.iloc[0],user_id , row.iloc[2], row.iloc[3], row.iloc[4])
                        # Execute the INSERT query
                            cursor.execute(insert_query, data)

                    # Commit changes and close the connection
                            conn.commit()
                            print(f'Data uploaded successfully for userid{user_id}')
                   
                        conn.close()
                    return render_template("User-Page.html")  # Render a success page
                else:
                    return jsonify({'error': 'No data found in the CSV file'}), 400
           
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    return render_template("User-Page.html", form=form)
    

@auth.route("/uploads/History", methods=['GET', 'POST'])
@is_logged_in
def user_history():
    if request.method == 'POST':
        if 'user_id' in session:
            user_id = session.get('user_id')
            components = [{'component': component[0], 'value': component[1], 'date': component[2]} for component in website.models.UserComponents(user_id)]
            return render_template("DATA_user.html", components_data=components)


@auth.route("/uploads/History/graph", methods=['GET'])
@is_logged_in
def user_graph():
    # Sample data
    if 'user_id' in session:
        user_id = session.get('user_id')

        components = {
            'Date': [component[2] for component in website.models.UserComponents(user_id)],
            'Value': [component[1] for component in website.models.UserComponents(user_id)],
            'Component': [component[0] for component in website.models.UserComponents(user_id)]
        }

        # Create DataFrame
        df = pd.DataFrame(components)

        # Convert 'Date' column to datetime type
        df['Date'] = pd.to_datetime(df['Date'])

        # Set 'Date' as index
        df.set_index('Date', inplace=True)

        # Filter data for components 'P', 'NH', 'Ph'
        df_components = {}
        for component in ['P', 'NH4', 'Ph']:
            df_component = df[df['Component'] == component]
            df_components[component] = df_component[~df_component.index.duplicated()].resample('M').ffill()

        # Plotting
        plots = []
        for component, df_component in df_components.items():
            plt.figure(figsize=(10, 6))
            plt.plot(df_component.index, df_component['Value'], marker='o', linestyle='-')
            plt.title(f'Component {component} - Value Over Time')
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.grid(True)

            # Format date on x-axis
            date_form = DateFormatter("%Y.%m.%d")  # Customize the date format as per your preference
            plt.gca().xaxis.set_major_formatter(date_form)
            plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

            # Save the plot as a PNG image
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()

            plots.append({'component': component, 'image_base64': image_base64})

        # Render template with plots
        return render_template('userGraphs.html', plots=plots)
from website.prediction import Predictions
@auth.route("/uploads/Prediction", methods=['POST', 'GET'])
def user_prediction():
    if request.method == 'POST':
        if 'user_id' in session:
            user_id = session.get('user_id')
            
            # Assuming website.models.UserComponents returns data in some format
            user_data = [{'component': component[0], 'value': component[1], 'date': component[2]} for component in website.models.UserComponents(user_id)]
            
            if user_data:  # Check if there is valid input data
                # Convert input data to a DataFrame for ARIMA prediction
                user_data_df= pd.DataFrame(user_data)
           
                model=Predictions()
                pred=model.predict(user_data_df, steps=1, dynamic=False)
                
                # Make predictions using the ARIMA model
                #prediction = model.predict(input_df)
                correlation_coefficient = np.corrcoef(pred, user_data_df['value'])[0, 1]
                bias = np.mean(user_data_df['value'] - pred)
                mae = mean_absolute_error(user_data_df['value'], pred)
                mse = mean_squared_error(user_data_df['value'], pred)
                rmse = np.sqrt(mse)
                if pred.empty or mae is not  None or bias is  not None or mse is not  None or correlation_coefficient is  not None:
                    # Render the template with the prediction result
                    return render_template("prediction.html", pred=pred, rmse=rmse, mae=mae, bias=bias, correlation_coefficient=correlation_coefficient)
                else:
                    # Handle the case when no prediction is available
                    return "No prediction available."
            else:
                return "No input data available."
        else:
            return "User not logged in."

@auth.route("/uploads/Prediction/graph", methods=['GET'])
@is_logged_in
def user_graphpred():
    if 'user_id' in session:
        user_id = session.get('user_id')

        components = {
            'Date': [component[2] for component in website.models.UserComponents(user_id)],
            'Value': [component[1] for component in website.models.UserComponents(user_id)],
            'Component': [component[0] for component in website.models.UserComponents(user_id)]
        }
        user_data_df = pd.DataFrame(components, columns=['Component', 'Value', 'Date'])

        # Convert 'Date' column to datetime type
        user_data_df['Date'] = pd.to_datetime(user_data_df['Date'])

        # Filter data for components 'P', 'NH4', 'Ph' and make predictions
        plots = []
        for component in ['P', 'NH4', 'Ph']:
            df_component = user_data_df[user_data_df['Component'] == component]
            if not df_component.empty:
                model = Predictions()
                pred = model.predict(df_component, steps=1, dynamic=False)

                # Plotting
                plt.figure(figsize=(10, 6))
                plt.plot(df_component['Date'], df_component['Value'], label='Actual', marker='o', linestyle='-')
                plt.plot(df_component['Date'], pred, label='Predicted', marker='o', linestyle='-')
                plt.title(f'Component {component} - Value Over Time')
                plt.xlabel('Date')
                plt.ylabel('Value')
                plt.grid(True)

                # Format date on x-axis
                date_form = DateFormatter("%d.%m.%Y")
                plt.gca().xaxis.set_major_formatter(date_form)
                plt.xticks(rotation=45)

                # Save the plot as a PNG image
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                buffer.close()

                plots.append({'component': component, 'image_base64': image_base64})

        # Render template with plots
        return render_template('predictgraph.html', plots=plots)

            




