# OCR Gazeta Generator - Udhëzime për Lidhjen e Databazës

## 📁 Struktura e Projektit

```
ocr_project/
├── app.py                 # Aplikacioni kryesor Flask
├── config.py              # Konfigurimi
├── run.py                 # Pika e nisjes
├── test_connection.py     # Testimi i lidhjes
├── .env                   # Variablat e mjedisit (NDRYSHO KËTO!)
├── requirements.txt       # Libraritë e nevojshme
│
├── routes/                # Routat API
│   ├── __init__.py
│   ├── auth.py
│   ├── images.py
│   ├── ocr.py
│   ├── search.py
│   ├── download.py
│   ├── health_check.py
│   └── helpers.py
│
├── models/                # Modelet e databazës
│   ├── __init__.py
│   ├── user.py
│   ├── image.py
│   ├── ocr_result.py
│   └── project.py
│
├── services/              # Shërbimet
│   ├── __init__.py
│   ├── ocr_service.py
│   ├── paddle_ocr_service.py
│   ├── scraper_service.py
│   ├── cache_service.py
│   ├── image_processor.py
│   ├── validators.py
│   └── rate_limiter.py
│
├── database/              # Databaza
│   ├── __init__.py
│   ├── database.py
│   ├── setup_database.py
│   ├── schema.sql         # Struktura e databazës
│   └── sample_data.sql    # Të dhëna shembull
│
├── utils/                 # Utilitetet
│   └── __init__.py
│
└── static/                # Frontend files
    ├── index.html
    ├── login.html
    ├── register.html
    ├── about.html
    ├── style.css
    ├── script.js
    └── uploads/
```

## 🚀 Hapat për të Lidhur Databazën

### Hapi 1: Instalo SQL Server

1. Shkarko dhe instalo **SQL Server Express**:
   - https://www.microsoft.com/en-us/sql-server/sql-server-downloads

2. Instalo **SQL Server Management Studio (SSMS)**:
   - https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms

3. Instalo **ODBC Driver 17 for SQL Server**:
   - https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Hapi 2: Krijo Databazën

1. Hap **SQL Server Management Studio**
2. Lidhu me serverin lokal (localhost)
3. Krijo një query të ri
4. Kopjo përmbajtjen e `database/schema.sql`
5. Ekzekuto (F5)

### Hapi 3: Konfiguro Kredencialet

1. Hap fajllin `.env`
2. Ndrysho vlerat:

```env
# Database Configuration
DB_SERVER=localhost
DB_NAME=ocr_db
DB_USER=sa
DB_PASSWORD=YOUR_ACTUAL_PASSWORD_HERE
TRUSTED_CONNECTION=false
```

**Nëse përdor Windows Authentication:**
```env
TRUSTED_CONNECTION=true
```

### Hapi 4: Instalo Libraritë

```bash
pip install -r requirements.txt
```

### Hapi 5: Testo Lidhjen

```bash
python test_connection.py
```

Nëse shfaqet:
```
✅ Lidhja me databazën u krye me sukses!
✅ TË GJITHA TESTET KALUAN!
```

➡️ Lidhja funksionon!

### Hapi 6: Nis Aplikacionin

```bash
python run.py
```

Aplikacioni do të niset në: http://localhost:5000

## 🔧 Zgjidhja e Problemeve

### Problem: "Login failed for user 'sa'"

**Zgjidhja:**
1. Hap SQL Server Management Studio
2. Right-click në server → Properties → Security
3. Zgjidh "SQL Server and Windows Authentication mode"
4. Restart SQL Server
5. Shko te Security → Logins → sa
6. Right-click → Properties
7. Vendos një password të ri
8. Aktivizo "Login" → Enabled

### Problem: "Cannot open database 'ocr_db'"

**Zgjidhja:**
```bash
# Ekzekuto schema.sql në SQL Server Management Studio
```

### Problem: "ODBC Driver 17 not found"

**Zgjidhja:**
Shkarko dhe instalo nga: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Problem: "Network-related error"

**Zgjidhja:**
1. Hap **SQL Server Configuration Manager**
2. Shko te **SQL Server Network Configuration** → **Protocols for MSSQLSERVER**
3. Aktivizo **TCP/IP**
4. Restart SQL Server

## 📞 API Endpoints

| Endpoint | Metoda | Përshkrimi |
|----------|--------|------------|
| `/api/v1/auth/login` | POST | Kyçja |
| `/api/v1/auth/register` | POST | Regjistrimi |
| `/api/v1/images` | GET/POST | Listo/Ngarko imazhe |
| `/api/v1/ocr` | POST | Proceso OCR |
| `/api/v1/search` | GET | Kërko |
| `/health` | GET | Health check |

## 📝 Shënime

- Mos e komito fajllin `.env` në Git!
- Përdor `your_password_here` në vend të password-it real në dokumentacion
- Sigurohu që SQL Server është duke punuar para se të nisësh aplikacionin
