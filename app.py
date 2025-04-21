from flask import Flask, render_template, request, send_from_directory
import os
from werkzeug.utils import secure_filename
from utils.merge import merge_pdfs, allowed_file, MAX_FILE_SIZE, MAX_TOTAL_SIZE
from utils.split import split_pdf
from utils.convert import convert_image_to_pdf
from utils.compress import compress_pdf
from config import config

def create_app(config_name='production'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure the upload and result folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/merge', methods=['POST'])
    def merge():
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return "No files selected", 400

        # Validate total size
        total_size = sum(len(file.read()) for file in files)
        for file in files:
            file.seek(0)  # Reset file pointers after reading
        
        if total_size > MAX_TOTAL_SIZE:
            return "Total file size too large", 400

        # Save uploaded PDFs
        file_paths = []
        try:
            for file in files:
                if not allowed_file(file.filename):
                    return "Invalid file type. Only PDFs are allowed.", 400
                
                # Check individual file size
                if len(file.read()) > MAX_FILE_SIZE:
                    return f"File {file.filename} is too large", 400
                file.seek(0)
                    
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_paths.append(file_path)

            # Output file path
            output_filename = 'merged.pdf'
            output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)

            # Merge files
            merge_pdfs(file_paths, output_path)

            return render_template('result.html', filename=output_filename)

        except Exception as e:
            return f"An error occurred: {str(e)}", 500
        finally:
            # Clean up uploaded files
            for path in file_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    app.logger.error(f"Error cleaning up file {path}: {str(e)}")

    @app.route('/split', methods=['POST'])
    def split():
        if 'file' not in request.files:
            return "No file selected", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400

        if not allowed_file(file.filename):
            return "Invalid file type. Only PDFs are allowed.", 400

        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            page_number = int(request.form.get('page', 1))
            output_files = split_pdf(file_path, page_number)

            # Clean up input file
            os.remove(file_path)

            return render_template('result.html', filenames=output_files)

        except ValueError as e:
            return str(e), 400
        except Exception as e:
            return f"An error occurred: {str(e)}", 500

    @app.route('/convert', methods=['POST'])
    def convert():
        if 'image' not in request.files:
            return "No image selected", 400

        file = request.files['image']
        if file.filename == '':
            return "No file selected", 400

        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            output_filename = os.path.splitext(filename)[0] + '.pdf'
            output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)

            # Convert image to PDF
            with open(output_path, 'wb') as output_file:
                pdf_bytes = convert_image_to_pdf(file_path)
                output_file.write(pdf_bytes)

            # Clean up input file
            os.remove(file_path)

            return render_template('result.html', filename=output_filename)

        except Exception as e:
            return f"An error occurred: {str(e)}", 500

    @app.route('/compress', methods=['POST'])
    def compress():
        if 'file' not in request.files:
            return "No file selected", 400

        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400

        if not allowed_file(file.filename):
            return "Invalid file type. Only PDFs are allowed.", 400

        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            output_filename = 'compressed_' + filename
            output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)

            # Compress PDF
            writer = compress_pdf(file_path)
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            # Clean up input file
            os.remove(file_path)

            return render_template('result.html', filename=output_filename)

        except Exception as e:
            return f"An error occurred: {str(e)}", 500

    @app.route('/download/<filename>')
    def download_file(filename):
        return send_from_directory(app.config['RESULT_FOLDER'], filename, as_attachment=True)

    return app

# Create the application instance
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run()