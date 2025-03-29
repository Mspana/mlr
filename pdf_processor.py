import os
import uuid
import shutil
import platform
import glob
from pdf2image import convert_from_path
from gemini_api import analyze_image

class PDFProcessor:
    def __init__(self, upload_folder, temp_folder):
        """
        Initialize the PDF processor
        
        Args:
            upload_folder (str): Path to store uploaded PDFs
            temp_folder (str): Path to store temporary images
        """
        self.upload_folder = upload_folder
        self.temp_folder = temp_folder
        
        # Create folders if they don't exist
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(temp_folder, exist_ok=True)
        
        # Set path to poppler binaries based on platform
        self.poppler_path = None
        if platform.system() == "Windows":
            # Path to the actual location of the Poppler binaries
            self.poppler_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'poppler-24.08.0', 'Library', 'bin')
            print(f"Using Poppler binaries from: {self.poppler_path}")
    
    def process_pdf(self, pdf_path):
        """
        Process a PDF file: convert to images and analyze each page
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            dict: Analysis results for each page
        """
        # Create a unique folder for this PDF's images
        session_id = str(uuid.uuid4())
        image_folder = os.path.join(self.temp_folder, session_id)
        os.makedirs(image_folder, exist_ok=True)
        
        try:
            # Convert PDF to images
            print(f"Converting PDF to images: {pdf_path}")
            
            # Use local poppler binaries if available
            conversion_kwargs = {
                'pdf_path': pdf_path,
                'dpi': 200,  # Adjust DPI as needed for quality vs. size
                'fmt': "jpeg",
                'output_folder': image_folder,
                'output_file': "page"  # Base filename for output
            }
            
            # Add poppler path if on Windows
            if self.poppler_path and os.path.exists(self.poppler_path):
                conversion_kwargs['poppler_path'] = self.poppler_path
                print(f"Using Poppler binaries from: {self.poppler_path}")
            else:
                print("Poppler binaries not found, using system-wide installation if available")
                
            # Convert PDF to images
            images = convert_from_path(**conversion_kwargs)
            print(f"Converted {len(images)} pages to images in {image_folder}")
            
            # List all files in the directory to see what's actually there
            all_files = os.listdir(image_folder)
            print(f"All files in directory: {all_files}")
            
            # Try to find image files with any extension
            image_files = []
            for ext in ['*.jpeg', '*.jpg', '*.png', '*.tiff', '*.bmp']:
                found_files = glob.glob(os.path.join(image_folder, ext))
                image_files.extend(found_files)
            
            # If no image files found with glob, try listing all files and filtering by extension
            if not image_files:
                print("No image files found with glob, trying direct file listing")
                for file in all_files:
                    file_path = os.path.join(image_folder, file)
                    if os.path.isfile(file_path) and file.lower().endswith(('.jpeg', '.jpg', '.png', '.tiff', '.bmp')):
                        image_files.append(file_path)
            
            # If still no image files found, try to use the images directly from the conversion
            if not image_files and images:
                print("No image files found in directory, using images from conversion directly")
                # Save the images manually
                image_files = []
                for i, img in enumerate(images):
                    img_path = os.path.join(image_folder, f"page_{i+1}.jpeg")
                    img.save(img_path, "JPEG")
                    image_files.append(img_path)
                print(f"Manually saved {len(image_files)} images")
            
            image_files.sort()  # Sort to ensure correct order
            print(f"Found {len(image_files)} image files: {image_files}")
            
            if not image_files:
                raise Exception("No image files found after PDF conversion")
            
            # Process each page
            results = {}
            for i, image_path in enumerate(image_files):
                page_num = i + 1
                print(f"Analyzing page {page_num}: {image_path}")
                
                # Verify the file exists before trying to analyze it
                if not os.path.exists(image_path):
                    print(f"Warning: Image file does not exist: {image_path}")
                    continue
                
                # Analyze the image using Gemini API
                page_result = analyze_image(image_path)
                
                # Store the result
                results[f"page_{page_num}"] = {
                    "image_path": image_path,
                    "analysis": page_result
                }
            
            return {
                "session_id": session_id,
                "total_pages": len(image_files),
                "results": results
            }
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            # Clean up the image folder in case of error
            if os.path.exists(image_folder):
                shutil.rmtree(image_folder)
            raise e
    
    def cleanup_session(self, session_id):
        """
        Clean up temporary files for a session
        
        Args:
            session_id (str): Session ID to clean up
        """
        image_folder = os.path.join(self.temp_folder, session_id)
        if os.path.exists(image_folder):
            shutil.rmtree(image_folder) 