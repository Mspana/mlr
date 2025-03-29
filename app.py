import os
import json
import uuid
import shutil
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.utils import secure_filename
from pdf_processor import PDFProcessor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

# Configure upload folders
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
TEMP_FOLDER = os.path.join(UPLOAD_FOLDER, 'temp')
REPORTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
SAMPLES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'samples')

# Print directory paths for debugging
print(f"UPLOAD_FOLDER: {UPLOAD_FOLDER}")
print(f"SAMPLES_FOLDER: {SAMPLES_FOLDER}")
print(f"Samples directory exists: {os.path.exists(SAMPLES_FOLDER)}")
if os.path.exists(SAMPLES_FOLDER):
    print(f"Samples directory contents: {os.listdir(SAMPLES_FOLDER)}")

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)
os.makedirs(SAMPLES_FOLDER, exist_ok=True)  # Ensure samples directory exists

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

# Initialize PDF processor
pdf_processor = PDFProcessor(UPLOAD_FOLDER, TEMP_FOLDER)

# Add current date to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Add sample PDFs to all templates
@app.context_processor
def inject_samples():
    samples = []
    if os.path.exists(SAMPLES_FOLDER):
        for file in os.listdir(SAMPLES_FOLDER):
            if file.lower().endswith('.pdf'):
                samples.append(file)
    return {'sample_pdfs': samples}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/sample/<path:filename>')
def view_sample(filename):
    """Serve a sample PDF file for preview"""
    try:
        # Print debug information
        print(f"Requested sample file: {filename}")
        
        # Construct the file path
        file_path = os.path.join(SAMPLES_FOLDER, filename)
        print(f"Full file path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            flash(f'Sample file not found: {filename}')
            return redirect(url_for('index'))
        
        # Serve the file
        return send_file(file_path, mimetype='application/pdf')
    except Exception as e:
        print(f"Error serving sample file: {str(e)}")
        flash(f'Error serving sample file: {str(e)}')
        return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    # Check if a file was uploaded
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    # Check if the file is allowed
    if file and allowed_file(file.filename):
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        try:
            # Process the PDF
            results = pdf_processor.process_pdf(file_path)
            
            # Store the results in the session
            session['analysis_results'] = results
            session['pdf_filename'] = filename
            
            # Redirect to the results page
            return redirect(url_for('results'))
        
        except Exception as e:
            flash(f'Error processing PDF: {str(e)}')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload a PDF file.')
        return redirect(url_for('index'))

@app.route('/use_sample', methods=['POST'])
def use_sample():
    """Handle sample PDF selection"""
    try:
        sample_file = request.form.get('sample_file')
        print(f"Selected sample file: {sample_file}")
        
        if not sample_file:
            flash('No sample file selected')
            return redirect(url_for('index'))
        
        # Ensure the sample file exists
        sample_path = os.path.join(SAMPLES_FOLDER, sample_file)
        print(f"Sample path: {sample_path}")
        print(f"Sample file exists: {os.path.exists(sample_path)}")
        
        if not os.path.exists(sample_path):
            flash(f'Sample file not found: {sample_file}')
            return redirect(url_for('index'))
        
        # Copy the sample file to the uploads folder
        dest_filename = secure_filename(sample_file)
        dest_path = os.path.join(UPLOAD_FOLDER, dest_filename)
        print(f"Destination path: {dest_path}")
        
        shutil.copy2(sample_path, dest_path)
        print(f"File copied successfully")
        
        # Process the PDF
        results = pdf_processor.process_pdf(dest_path)
        
        # Store the results in the session
        session['analysis_results'] = results
        session['pdf_filename'] = dest_filename
        
        # Redirect to the results page
        return redirect(url_for('results'))
    
    except Exception as e:
        print(f"Error processing sample PDF: {str(e)}")
        flash(f'Error processing sample PDF: {str(e)}')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    """Display the analysis results"""
    # Check if results exist in the session
    if 'analysis_results' not in session:
        flash('No analysis results found. Please upload a PDF file.')
        return redirect(url_for('index'))
    
    # Get the results from the session
    results = session['analysis_results']
    filename = session.get('pdf_filename', 'Unknown file')
    
    return render_template('results.html', results=results, filename=filename)

@app.route('/update_suggestion', methods=['POST'])
def update_suggestion():
    """Update a suggestion (accept/reject)"""
    data = request.json
    page_id = data.get('page_id')
    issue_type = data.get('issue_type')
    issue_index = data.get('issue_index')
    action = data.get('action')
    
    # Get the results from the session
    results = session.get('analysis_results', {})
    
    # Update the suggestion status
    if page_id in results.get('results', {}):
        issues = results['results'][page_id]['analysis'].get(issue_type, [])
        if 0 <= issue_index < len(issues):
            issues[issue_index]['status'] = action
            
            # Update the session
            session['analysis_results'] = results
            
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid request'})

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate a summary report"""
    # Get the results from the session
    results = session.get('analysis_results', {})
    filename = session.get('pdf_filename', 'Unknown file')
    
    if not results:
        flash('No analysis results found. Please upload a PDF file.')
        return redirect(url_for('index'))
    
    # Generate a unique report filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"report_{timestamp}.json"
    report_path = os.path.join(REPORTS_FOLDER, report_filename)
    
    # Prepare the report data
    report_data = {
        'filename': filename,
        'timestamp': timestamp,
        'total_pages': results.get('total_pages', 0),
        'pages': {}
    }
    
    # Compile the report data
    for page_id, page_data in results.get('results', {}).items():
        analysis = page_data.get('analysis', {})
        
        # Count issues by status
        spelling_grammar_issues = analysis.get('spelling_grammar_issues', [])
        formatting_issues = analysis.get('formatting_issues', [])
        
        # Add status if not present
        for issue in spelling_grammar_issues + formatting_issues:
            if 'status' not in issue:
                issue['status'] = 'pending'
        
        report_data['pages'][page_id] = {
            'text_extracted': analysis.get('text_extracted', ''),
            'spelling_grammar_issues': spelling_grammar_issues,
            'formatting_issues': formatting_issues
        }
    
    # Save the report
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    # Return the report file
    return send_file(report_path, as_attachment=True)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up temporary files and session data"""
    # Get the session ID from the results
    results = session.get('analysis_results', {})
    session_id = results.get('session_id')
    
    # Clean up temporary files
    if session_id:
        pdf_processor.cleanup_session(session_id)
    
    # Clear session data
    session.pop('analysis_results', None)
    session.pop('pdf_filename', None)
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True) 