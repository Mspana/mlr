# PDF Promo Material Checker

A Python-based prototype that processes PDF promotional materials for spellchecking, grammar checks, and basic formatting consistency using Google's Gemini API for multimodal (text + image) analysis.

## Features

- Upload PDF promotional materials
- Analyze each page for spelling/grammar errors and formatting issues
- Review flagged issues in a web UI
- Accept or reject suggestions
- Generate a summary report

## Setup

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd pdf-promo-checker
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download Poppler binaries for Windows:
   - Download from https://github.com/oschwartz10612/poppler-windows/releases/
   - Extract the contents to the `bin` directory in the project
   - The application will automatically find the binaries in the correct location
   - No need to add to PATH as the application will use the local binaries
   
   **Note**: The application is configured to use Poppler binaries from the `bin/poppler-24.08.0/Library/bin` directory. If you download a different version, you may need to update the path in `pdf_processor.py`.

4. Create a `.env` file in the project root with your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

### Running the Application

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Upload a PDF file using the web interface
2. Wait for the analysis to complete
3. Review the flagged issues
4. Accept or reject suggestions
5. Generate a summary report

## Project Structure

- `app.py`: Main Flask application
- `pdf_processor.py`: PDF to image conversion and processing
- `gemini_api.py`: Google Gemini API integration
- `templates/`: HTML templates for the web interface
- `static/`: Static files (CSS, JS, images)
- `bin/`: Contains Poppler binaries for PDF processing
- `uploads/`: Temporary storage for uploaded PDFs and generated images
- `reports/`: Generated summary reports 