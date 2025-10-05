# Lead Processing Dashboard 🚀  
A powerful, modern web application for processing and filtering lead data with advanced data cleaning, validation, and filtering capabilities.  

# Deployment
- Powered by Flask & hosted seamlessly on Microsoft Azure App Service.
- https://validleads.azurewebsites.net

![Version](https://img.shields.io/badge/Version-2.0.0-blue)  ![Python](https://img.shields.io/badge/Python-3.8%252B-green)  ![Flask](https://img.shields.io/badge/Flask-2.3.3-red)  ![Pandas](https://img.shields.io/badge/Pandas-2.0.3-orange)  

---

## 📋 Overview
The **Lead Processing Dashboard** is a sophisticated web application designed to handle large-scale lead data processing.  
It provides:  
- Intelligent data cleaning  
- Duplicate removal  
- Email validation  
- Advanced role-based filtering  

⚡ **Performance Optimized**: Can process files up to **2GB** efficiently.  

---

## ✨ Features

### 🎯 Core Functionalities
| Feature | Description |
|---------|-------------|
| **Valid Leads Processing** | Remove duplicate and invalid emails |
| **Smart Filtering** | Advanced role-based filtering with flexible input |
| **Large File Support** | Process files up to 2GB with optimized memory |
| **Drag & Drop** | Intuitive file upload interface |
| **Responsive Design** | Works seamlessly on all devices |

### 🔧 Advanced Capabilities
| Capability | Description |
|------------|-------------|
| Intelligent Column Mapping | Auto-detect & map column names |
| Case-Insensitive Deduplication | Remove duplicates ignoring case |
| Real-time Preview | Dynamic data preview (10–1000 rows) |
| Bulk Role Filtering | Multiple roles at once |
| Alphabetical Sorting | Sort names automatically |

### 🛡️ Data Validation & Cleaning
| Feature | Description |
|---------|-------------|
| Email Validation | Regex-based verification |
| Duplicate Removal | Case-insensitive deduplication |
| Data Standardization | Normalize column names |
| Missing Value Handling | Clean NaN & empty values |

---

## 🛠️ Technology Stack

### Backend
| Tech | Version | Purpose |
|------|---------|----------|
| Python | 3.8+ | Core language |
| Flask | 2.3.3 | Web framework |
| Pandas | 2.0.3 | Data manipulation |
| OpenPyXL | 3.1.2 | Excel handling |
| xlrd | 2.0.1 | Legacy Excel support |

### Frontend
| Tech | Purpose |
|------|----------|
| HTML5 | Structure |
| CSS3 | Styling |
| JavaScript ES6+ | Client-side logic |
| Bootstrap 5.3.2 | Responsive UI |
| Bootstrap Icons | Modern icons |

---

## 🏠 Home Dashboard

Two main functionalities:
- **Valid Leads** → Clean & validate data  
- **Filter Leads** → Role-based filtering  

---

### ✅ Valid Leads Processing
| Step   | Action |
|--------|--------|
| Step 1 | Upload file (CSV, XLSX, XLS, max 2GB) |
| Step 2 | Auto processing (deduplication, email validation, column mapping) |
| Step 3 | Preview results & download cleaned dataset |

---

### 🎛️ Filter Leads Processing
| Step   | Action |
|--------|--------|
| Step 1 | Upload file & enter roles (textarea input) |
| Step 2 | Flexible case-insensitive matching |
| Step 3 | Preview results & export |

---

## 🔌 API Endpoints

| Method   | Endpoint                                     | Description              |
|----------|----------------------------------------------|--------------------------|
| GET      | `/`                                          | Home dashboard           |
| GET/POST | `/valid_leads`                               | Valid leads processing   |
| GET/POST | `/filter_leads`                              | Role-based filtering     |
| GET      | `/downloads/<filename>`                      | Download processed file  |
| GET      | `/api/preview/<filename>?limit=<rows>`       | Preview dataset          |

---

## 🔄 Data Processing

### Supported Column Names
| Standard | Variations |
|----------|------------|
| Name     | Full Name, Contact Name, Person, First Name, Last Name |
| Email    | Email Address, E-mail, Contact Email |
| Phone    | Mobile, Contact, Phone Number, Telephone, Mobile No |
| Company  | Organization, Firm, Company Name, Employer |
| Title    | Position, Role, Job Title, Designation, Occupation |

---

### Pipeline
1. **File Upload** → Validation, size check, structure verification  
2. **Data Cleaning** → Normalize columns, handle empty values  
3. **Deduplication** → Case-insensitive email handling  
4. **Email Validation** → RFC-compliant regex  
5. **Filtering & Sorting** → Case-insensitive role filtering + alphabetical order  

---

## 🚀 Performance & Scalability

| Feature              | Optimization            |
|----------------------|-------------------------|
| Chunk Processing     | Files up to 2GB         |
| Memory Management    | Auto cleanup            |
| Optimized Pandas Ops | Speed improvements      |
| Progress Indicators  | Real-time feedback      |

### Browser Compatibility
- Chrome 90+  
- Firefox 88+  
- Safari 14+  
- Edge 90+  

---

## 🤝 Contributing
1. Fork repo  
2. Create branch → `git checkout -b feature/amazing-feature`  
3. Commit → `git commit -m "Add amazing feature"`  
4. Push → `git push origin feature/amazing-feature`  
5. Open Pull Request  

---

## 👨‍💻 Author
**Asim Husain**  
- 🌐 Website: https://www.asimhusain.dev)  
- 📧 studyboyasim01@gmail.com  
- 🔗 LinkedIn: https://www.linkedin.com/in/asimhusain1-ai 

---


## 🚀 Installation

### Prerequisites
- Python **3.8+**  
- `pip` package manager  
- Modern browser  

### Step-by-Step Setup
```bash
# Clone repo
git clone https://github.com/asimhusain-ai/Lead-Processing-Dashboard.git
cd lead-processing-dashboard

# Create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Localhost
http://localhost:5000

