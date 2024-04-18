from flask import Flask, render_template, request, send_file
import requests
import pandas as pd
import csv
import tempfile
import os
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', result_file=None)

@app.route('/get-details', methods=['POST'])
def get_details():
    if request.method == 'POST':
        if 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                # Use temporary file
                print("here1")
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                    uploaded_file.save(temp_file)
                    temp_file_name = temp_file.name
                    print("here1",temp_file_name)
                    if os.stat(temp_file_name).st_size == 0:
                        return 'Empty file'
                    # Read CSV file into pandas DataFrame
                    df = pd.read_csv(temp_file_name)
                    print("df",df)
                    # Add new columns for emails and phone numbers from API
                    df['EmailsFromApi'] = ''
                    df['PhoneNumbersFromApi'] = ''
                    # Iterate over rows to fetch data from API and update DataFrame
                    for index, row in df.iterrows():
                        linkedin_url = row['LinkedIn Profile']
                        details = get_linkedin_details(linkedin_url)
                        print(details,"details")
                        df.at[index, 'EmailsFromApi'] = ", ".join(details.get('emails', []))
                        df.at[index, 'PhoneNumbersFromApi'] = ", ".join(details.get('phoneNumbers', []))
                        print("row",row)
                    result_file_path = os.path.join(tempfile.gettempdir(), 'results.csv')
                    # Write DataFrame back to CSV file
                    df.to_csv(result_file_path, index=False)
                return send_file(result_file_path, as_attachment=True)
    return 'Invalid request'

def get_linkedin_details(linkedin_url):
    start_time = time.time()
    api_endpoint = f"https://pulse.aptask.com/api/2.0/linkedin/get-details-from-linkedin-url?linkedInUrl={linkedin_url}"
    response = requests.get(api_endpoint)
    end_time = time.time() 
    time_taken = end_time - start_time  # Calculate time taken
    print("API call took", time_taken, "seconds")
    if response.status_code == 200:
        return response.json()
    return {'emails': [], 'phoneNumbers': []}  # Return empty emails and phone numbers if API request fails

if __name__ == '__main__':
    app.run(debug=True)
