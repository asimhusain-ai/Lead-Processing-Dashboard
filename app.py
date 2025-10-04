from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import pandas as pd
import os
from datetime import datetime
import re
import uuid
import gc
import io

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xls', 'xlsx'}
REQUIRED_COLUMNS = {'Name', 'Email', 'Phone', 'Company', 'Title'}

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Roles / Decision-maker tokens
ROLE_TOKENS = [
    'Founder', 'CEO', 'CTO', 'COO', 'Director', 'Head',
    'Manager', 'Owner', 'President', 'Vice President', 'VP', 'Chief'
]
ROLE_PATTERN = re.compile('|'.join(ROLE_TOKENS), flags=re.IGNORECASE)

# Enhanced email regex
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=lambda c: c.strip())


def validate_email_address(email: str) -> bool:
    if pd.isna(email):
        return False
    email = str(email).strip()
    return bool(EMAIL_REGEX.match(email))


def generate_timestamped_filename(prefix: str, ext: str = 'csv') -> str:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_prefix = re.sub(r'[^A-Za-z0-9_-]', '_', prefix)
    return f"{safe_prefix}_{ts}.{ext}"


def map_columns(df):
    """Map common column names to standard required columns"""
    column_mapping = {}
    
    # Name mappings
    name_keywords = ['name', 'full name', 'contact name', 'person', 'fullname', 'first name', 'last name']
    column_mapping['Name'] = find_column(df, name_keywords)
    
    # Email mappings
    email_keywords = ['email', 'e-mail', 'email address', 'contact email', 'e mail']
    column_mapping['Email'] = find_column(df, email_keywords)
    
    # Phone mappings
    phone_keywords = ['phone', 'mobile', 'contact', 'phone number', 'telephone', 'mobile no', 'contact number', 'phone no']
    column_mapping['Phone'] = find_column(df, phone_keywords)
    
    # Company mappings
    company_keywords = ['company', 'organization', 'firm', 'company name', 'employer', 'organisation', 'workplace']
    column_mapping['Company'] = find_column(df, company_keywords)
    
    # Title mappings
    title_keywords = ['title', 'position', 'role', 'job title', 'designation', 'occupation', 'job role', 'job position']
    column_mapping['Title'] = find_column(df, title_keywords)
    
    return column_mapping


def find_column(df, keywords):
    """Find column that matches any of the keywords"""
    for col in df.columns:
        col_lower = col.lower().strip()
        for keyword in keywords:
            if keyword in col_lower:
                return col
    return None


def process_large_file(filepath, file_ext, chunk_size=10000):
    """Process large files in chunks to handle 1GB+ files efficiently"""
    chunks = []
    total_rows = 0
    
    try:
        if file_ext in ['xls', 'xlsx']:
            df = pd.read_excel(filepath, dtype=str)
            if len(df.columns) > 5:
                df = df.iloc[:, :5]
            chunks.append(df)
            total_rows = len(df)
        else:
            for chunk in pd.read_csv(filepath, dtype=str, chunksize=chunk_size, usecols=range(5)):
                chunks.append(chunk)
                total_rows += len(chunk)
                
        return chunks, total_rows
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")


@app.route('/')
def index():
    return render_template('index.html')


# ----------------- VALID LEADS -----------------
@app.route('/valid_leads', methods=['GET', 'POST'])
def valid_leads():
    file_uploaded = False
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('valid_leads'))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('valid_leads'))
        if file and allowed_file(file.filename):
            # Generate unique filename to avoid conflicts
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            try:

                if os.path.getsize(filepath) > 100 * 1024 * 1024: 
                    chunks, total_rows = process_large_file(filepath, file_ext)
                    df = pd.concat(chunks, ignore_index=True)
                else:
                    if file_ext in ['xls', 'xlsx']:
                        df = pd.read_excel(filepath, dtype=str)
                        if len(df.columns) > 5:
                            df = df.iloc[:, :5]
                    else:
                        df = pd.read_csv(filepath, dtype=str, usecols=range(5))
                    total_rows = len(df)
                    
                df = df.fillna('')
                df = clean_column_names(df)

                column_mapping = map_columns(df)
                missing = [col for col, mapped_col in column_mapping.items() if mapped_col is None]

                if missing:
                    flash(f'Could not find columns for: {", ".join(missing)}. Looking for columns like Name, Email, Phone, Company, Title', 'danger')
                    return redirect(url_for('valid_leads'))

                # Rename columns to standard names
                df = df.rename(columns={v: k for k, v in column_mapping.items() if v is not None})

                # Deduplicate emails
                df['Email'] = df['Email'].astype(str).str.strip()
                df['Email_lower'] = df['Email'].str.lower()
                before_count = len(df)
                df = df.drop_duplicates(subset=['Email_lower'])
                after_dedup_count = len(df)

                # Validate emails
                df['is_valid_email'] = df['Email'].apply(validate_email_address)
                clean_df = df[df['is_valid_email']].copy()
                clean_count = len(clean_df)

                # Sort by names alphabetically (case-insensitive)
                clean_df = clean_df.sort_values('Name', key=lambda x: x.str.lower())

                clean_df = clean_df.drop(columns=['Email_lower', 'is_valid_email'])
                clean_filename = generate_timestamped_filename('valid_leads')
                clean_df.to_csv(os.path.join(app.config['OUTPUT_FOLDER'], clean_filename), index=False)

                preview = clean_df.head(10).to_dict(orient='records')

                flash(
                    f'Successfully Processed: {before_count} Records | {before_count - after_dedup_count} Duplicate Emails Removed | {after_dedup_count - clean_count} Invalid Emails Removed | {clean_count} Valid Emails',
                    'success'
                )
                
                # Clean up memory
                del df, clean_df
                gc.collect()
                
                file_uploaded = True
                return render_template('valid_leads.html', preview=preview, file_path=clean_filename, 
                                      total_rows=clean_count, preview_count=min(10, clean_count),
                                      file_uploaded=file_uploaded)
                
            except Exception as e:
                flash(f'Failed to process file: {e}', 'danger')
                return redirect(url_for('valid_leads'))
        else:
            flash('Invalid file type.', 'danger')
            return redirect(url_for('valid_leads'))

    # GET request
    return render_template('valid_leads.html', preview=[], file_path='', total_rows=0, preview_count=0, file_uploaded=file_uploaded)


# ----------------- FILTER LEADS -----------------
@app.route('/filter_leads', methods=['GET', 'POST'])
def filter_leads():
    options = ROLE_TOKENS 
    selected = []
    preview = []
    file_path = ''
    total_rows = 0
    preview_count = 0
    file_uploaded = False

    if request.method == 'POST':
        roles_text = request.form.get('roles_text', '')
        selected = request.form.getlist('roles')
        
        if roles_text and not selected:
            selected = [role.strip() for role in roles_text.split('\n') if role.strip()]
        
        if not selected:
            flash('Please enter at least one role to filter by.', 'warning')
            return redirect(url_for('filter_leads'))
            
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('filter_leads'))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('filter_leads'))
        if file and allowed_file(file.filename): 
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            try:
                if os.path.getsize(filepath) > 100 * 1024 * 1024: 
                    chunks, total_rows_uploaded = process_large_file(filepath, file_ext)
                    df = pd.concat(chunks, ignore_index=True)
                else:
                    if file_ext in ['xls', 'xlsx']:
                        df = pd.read_excel(filepath, dtype=str)
                        if len(df.columns) > 5:
                            df = df.iloc[:, :5]
                    else:
                        df = pd.read_csv(filepath, dtype=str, usecols=range(5))
                    total_rows_uploaded = len(df)

                df = df.fillna('')
                df = clean_column_names(df)

                # Map columns to standard names
                column_mapping = map_columns(df)
                missing = [col for col, mapped_col in column_mapping.items() if mapped_col is None]

                if missing:
                    flash(f'Could not find columns for: {", ".join(missing)}. Looking for columns like Name, Email, Phone, Company, Title', 'danger')
                    return redirect(url_for('filter_leads'))

                df = df.rename(columns={v: k for k, v in column_mapping.items() if v is not None})

                # Deduplicate emails
                df['Email'] = df['Email'].astype(str).str.strip()
                df['Email_lower'] = df['Email'].str.lower()
                df = df.drop_duplicates(subset=['Email_lower'])

                # Validate emails
                df['is_valid_email'] = df['Email'].apply(validate_email_address)
                clean_df = df[df['is_valid_email']].copy()

                def matches_role(title: str):
                    if not isinstance(title, str) or not title.strip():
                        return False
                    
                    title_clean = title.lower().strip()
                    
                    for role in selected:
                        if not role or not role.strip():
                            continue
                            
                        role_clean = role.lower().strip()
                        
                        
                        if title_clean == role_clean:
                            return True
                            
                        if role_clean in title_clean:
                            return True
                            
                        if title_clean in role_clean:
                            return True
                            
                        if re.search(r'\b' + re.escape(role_clean) + r'\b', title_clean):
                            return True
                    
                    return False

                clean_df['Title'] = clean_df['Title'].astype(str)
                filtered_df = clean_df[clean_df['Title'].apply(matches_role)].copy()

                filtered_df = filtered_df.sort_values('Name', key=lambda x: x.str.lower())

                file_path = generate_timestamped_filename('filtered_leads')
                filtered_df.to_csv(os.path.join(app.config['OUTPUT_FOLDER'], file_path), index=False)
                
                total_rows = len(filtered_df)
                preview_count = min(10, total_rows)
                preview = filtered_df.head(preview_count).to_dict(orient='records')

                flash(f'Filtered {total_rows} Records From {total_rows_uploaded} Uploaded File After Removing {total_rows_uploaded - total_rows} Non-matching Records.', 'success')
                
                # Clean up memory
                del df, clean_df, filtered_df
                gc.collect()
                
                file_uploaded = True
                
            except Exception as e:
                flash(f'Failed to process file: {e}', 'danger')
                return redirect(url_for('filter_leads'))
        else:
            flash('Invalid file type.', 'danger')
            return redirect(url_for('filter_leads'))

    return render_template('filter_leads.html', options=options, selected=selected, 
                          preview=preview, file_path=file_path, total_rows=total_rows, 
                          preview_count=preview_count, file_uploaded=file_uploaded)


# ----------------- DOWNLOAD FILE -----------------
@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)


# ----------------- API FOR PREVIEW -----------------
@app.route('/api/preview/<path:filename>')
def api_preview(filename):
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        limit = request.args.get('limit', 10, type=int)
        
        if filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath, dtype=str, nrows=limit)
        else:
            df = pd.read_csv(filepath, dtype=str, nrows=limit)
        
        preview = df.fillna('').to_dict(orient='records')
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)