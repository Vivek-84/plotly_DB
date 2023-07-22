from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Read data from CSV
try:
    df = pd.read_csv('C://Users//vivek//Downloads//data12a.csv')
except FileNotFoundError as e:
    logging.error(f"error connecting to file extraction from web: {e}")
    df = None

# MongoDB connection
try:
    client = MongoClient("mongodb+srv://reinvest:8826974617@cluster0.z3aqnwq.mongodb.net/?retryWrites=true&w=majority")
    db = client['customer']
    collection = db['user_searches']
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    collection = None

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            selected_city = request.form['city']
            selected_sector = request.form['sector']
            selected_type = request.form['type']
            name = request.form['name']
            contact = request.form['contact']
            email = request.form['email']
            street = request.form['street']
            sqft = request.form['sqft']
            date = request.form['date']
            price = request.form['price']
            interest= request.form['interest']
            status= request.form['status']
            restype = request.form['restype']
            ##
            # Filter the data based on the selected city, sector, and type
            filtered_df = df[(df['City'] == selected_city) & (df['Sector'] == selected_sector) & (df['Type'] == selected_type)]
            
            # Calculate the average Price by Year
            avg_price = filtered_df.groupby('Year')['Price'].mean().reset_index()
            
            # Create line chart
            fig = px.line(avg_price, x='Year', y='Price', title=f'Average Price Trend(Lakh) - {selected_city} - {selected_sector} - {selected_type}')
            
            # Set the layout to show a linear trendline
            fig.update_traces(mode='lines+markers')
            
            # Convert the figure to JSON for rendering in the template
            graphJSON = fig.to_json()

            # Store the user search data in MongoDB
            user_search = {
                'city' : selected_city,
                'sector': selected_sector,
                'type': selected_type,
                'name' : name,
                'contact': contact,
                'email': email,
                'street': street,
                'sqft': sqft,
                'date' : date,
                'price' : price,
                'interest' : interest,
                'status'  : status,
                'restype' : restype,
                
            }
            collection.insert_one(user_search)
            
            return render_template('index.html', citys=df['City'].unique(), sectors=df['Sector'].unique(), types=df['Type'].unique(), graphJSON=graphJSON, selected_city=selected_city, selected_sector=selected_sector, selected_type=selected_type)
        
    # Render the initial page with the Sector and Type filter options
        return render_template('index.html', citys=df['City'].unique(), sectors=df['Sector'].unique(), types=df['Type'].unique(), graphJSON=None)

        
    except Exception as e:
        error_message = f"Error connecting with fetching data from Dashboard Templates: {e}"
        logging.error(error_message)
        #return render_template('error.html', error_message=error_message)

@app.route('/update-sectors', methods=['GET'])
def update_sectors():
    try:
        # Rest of your existing code
        selected_city = request.args.get('city')
        sectors = df[df['City'] == selected_city]['Sector'].unique()
        return jsonify({'sectors': sectors.tolist()})

    except Exception as e:
        error_message = f"Error connecting with dependency of City and updating Sector: {e}"
        logging.error(error_message)
        return jsonify({'error': error_message})

@app.route('/update-types', methods=['GET'])
def update_types():
    try:
        # Rest of your existing code
        selected_city = request.args.get('city')
        selected_sector = request.args.get('sector')
        types = df[(df['City'] == selected_city) & (df['Sector'] == selected_sector)]['Type'].unique()
        return jsonify({'types': types.tolist()})


    except Exception as e:
        error_message = f"Error connecting with dependency of City, Sector and updating Type: {e}"
        logging.error(error_message)
        return jsonify({'error': error_message})


if __name__ == '__main__':
    app.run(debug=True)
