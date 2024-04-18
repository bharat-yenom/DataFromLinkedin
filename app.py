from flask import Flask, request, make_response,render_template, request, send_file
import pandas as pd
import requests
import io
import time
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_csv', methods=['POST'])
def process_csv():
    # Get the uploaded CSV file
    csv_file = request.files['file']

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Check if the 'LinkedIn Profile' column exists
    if 'LinkedIn Profile' not in df.columns:
        return 'Error: The CSV file does not have a "LinkedIn Profile" column.', 400

    # Create empty lists to store the emails and phone numbers
    emails = []
    phone_numbers = []

    # Loop through each LinkedIn profile URL and fetch the details
    for url in df['LinkedIn Profile']:
        try:
            start_time = time.time()
            api_url = f'https://pulse.aptask.com/api/2.0/linkedin/get-details-from-linkedin-url?linkedInUrl={url}'
            response = requests.get(api_url).json()
            end_time = time.time() 
            time_taken = end_time - start_time  # Calculate time taken
            print("API call took", time_taken, "seconds")
            email_str = ', '.join(response.get('emails', []))
            email_str = email_str.replace('::, ', ', ')  # Replace '::' with a comma
            phone_number_str = ', '.join(response.get('phoneNumbers', []))
            phone_number_str = phone_number_str.replace('::, ', ', ')  # Replace '::' with a comma
            emails.append(email_str)
            phone_numbers.append(phone_number_str)
        except Exception as e:
            print(f'Error fetching details for {url}: {e}')
            emails.append('')
            phone_numbers.append('')

    # Add the new columns to the DataFrame
    df['emailsApi'] = emails
    df['phoneNumbersApi'] = phone_numbers

    # Convert the DataFrame back to a CSV file
    csv_data = df.to_csv(index=False)

    # Create a response with the CSV file
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename=processed_data.csv'
    response.headers['Content-Type'] = 'text/csv'

    return response

if __name__ == '__main__':
    app.run(debug=True)