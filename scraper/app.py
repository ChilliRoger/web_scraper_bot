from flask import Flask, render_template, request, send_file, jsonify, flash
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import tempfile
from io import StringIO

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Headers for web scraping
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_data():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Your exact scraping logic
        page = requests.get(url, headers=HEADERS)
        page.raise_for_status()
        
        data = []
        soup = BeautifulSoup(page.text, 'html.parser')
        
        # Find all tables and get the 5th one (index 4)
        tables = soup.find_all("table")
        if len(tables) < 5:
            return jsonify({'error': 'Expected table not found (need at least 5 tables)'}), 400
        
        list_header = []
        header = tables[4].find("tr")
        
        for items in header:
            try:
                list_header.append(items.get_text())
            except:
                continue
        
        # Remove elements from index 6 onwards
        del list_header[6:]
        
        # Extract data from remaining rows
        HTML_data = tables[4].find_all("tr")[1:]
        
        for element in HTML_data:
            sub_data = []
            x = 0
            for sub_element in element:
                try:
                    if x != 9:
                        sub_data.append(sub_element.get_text())
                        x += 1
                    else:
                        x = 0
                        break
                except:
                    continue
            
            if sub_data:
                sub_data.pop()
                del sub_data[-2:]
                data.append(sub_data)
        
        # Remove first 2 data rows
        del data[0:2]
        
        if not data:
            return jsonify({'error': 'No data found in the table'}), 400
        
        # Create DataFrame
        dft = pd.DataFrame(data=data, columns=list_header)
        
        # Set specific categories
        if len(dft) >= 5:
            dft.iloc[0, 0] = "Promoter"
            dft.iloc[1, 0] = "Public"
            dft.iloc[2, 0] = "Others"
            dft.iloc[3, 0] = "Others"
            dft.iloc[4, 0] = "Others"
        
        # Select specific columns
        required_columns = [
            'Category of shareholder', 
            'No. of shareholders', 
            'Total no. shares held', 
            'Shareholding as a % of total no. of shares (calculated as per SCRR, 1957)As a % of (A+B+C2)'
        ]
        
        # Check if required columns exist
        missing_columns = [col for col in required_columns if col not in dft.columns]
        if missing_columns:
            return jsonify({'error': f'Missing required columns: {missing_columns}'}), 400
        
        df = dft[required_columns]
        
        # Generate filename like in your original code
        try:
            filename = url.split('=')[1].split('&')[0] + '.csv'
        except:
            filename = 'shareholding_data.csv'
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        df.to_csv(filepath, index=False)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'rows': len(df),
            'message': 'Data scraped successfully'
        })
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing data: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)