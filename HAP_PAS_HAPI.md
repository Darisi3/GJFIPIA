# 📝 Hapat për të Lidhur Databazën - OCR Gazeta Generator

## ✅ Çfarë u rregullua automatikisht:

1. **U krijua struktura e folderëve:**
   - `routes/` - për routat API
   - `models/` - për modelet e databazës
   - `services/` - për shërbimet
   - `database/` - për lidhjen me databazën
   - `utils/` - për utilitete
   - `static/` - për frontend files

2. **U krijuan fajllat `__init__.py`** për çdo package

3. **U rregullua `config.py`** - u shtua `trusted_connection`

4. **U krijua `.env`** - template për kredencialet

5. **U rregullua `database/setup_database.py`** - importet e sakta

6. **U krijua `test_connection.py`** - për testimin e lidhjes

7. **U krijua `requirements.txt`** - libraritë e nevojshme

---

## 🔧 Çfarë duhet të bësh TI:

### HAPI 1: Krijo Databazën në SQL Server

1. Hap **SQL Server Management Studio (SSMS)**
2. Lidhu me `localhost`
3. Krijo një **New Query**
4. Kopjo përmbajtjen e fajllit `database/schema.sql`
5. Shtyp **F5** (Execute)

**Ose ekzekuto direkt:**
```sql
-- Krijo databazën
CREATE DATABASE ocr_db;
GO

USE ocr_db;
GO

-- Ekzekuto të gjitha CREATE TABLE statements nga schema.sql
```

### HAPI 2: Konfiguro Kredencialet

1. Hap fajllin `.env` në një editor teksti
2. Ndrysho vlerat:

```env
# NDRYSHO KËTO:
DB_PASSWORD=your_actual_password_here
```

**Shembull:**
```env
DB_PASSWORD=MySecurePassword123!
```

### HAPI 3: Instalo Libraritë

Hap **Command Prompt** ose **PowerShell** në folderin e projektit:

```bash
cd C:\path\to\ocr_project
pip install -r requirements.txt
```

### HAPI 4: Testo Lidhjen

```bash
python test_connection.py
```

**Nëse shfaqet:**
```
✅ Lidhja me databazën u krye me sukses!
✅ TË GJITHA TESTET KALUAN!
```

➡️ **Shkojmë në hapin 5!**

**Nëse shfaqet:**
```
❌ LIDHJA DËSHTOI!
```

➡️ **Shiko seksionin "Zgjidhja e Problemeve" më poshtë**

### HAPI 5: Nis Aplikacionin

```bash
python run.py
```

Hap shfletuesin dhe shko te: **http://localhost:5000**

---

## 🔴 Zgjidhja e Problemeve të Zakonshme

### 1. "Login failed for user 'sa'"

**Problemi:** SQL Server nuk e pranon login me username/password

**Zgjidhja:**
```
1. Hap SQL Server Management Studio
2. Right-click në server name (localhost) → Properties
3. Shko te "Security"
4. Zgjidh: "SQL Server and Windows Authentication mode"
5. Click OK
6. Restart SQL Server:
   - Shko te SQL Server Configuration Manager
   - SQL Server Services → Right-click SQL Server → Restart
7. Shko te Security → Logins → sa
8. Right-click → Properties
9. Vendos një password të ri
10. Shko te "Status" → Login: Enabled
11. Click OK
```

### 2. "Cannot open database 'ocr_db'"

**Problemi:** Databaza nuk ekziston

**Zgjidhja:**
```sql
-- Ekzekuto këtë në SQL Server Management Studio
CREATE DATABASE ocr_db;
GO
```

Pastaj ekzekuto `database/schema.sql`

### 3. "ODBC Driver 17 not found"

**Problemi:** Mungon driver-i ODBC

**Zgjidhja:**
Shkarko dhe instalo: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### 4. "Network-related error"

**Problemi:** SQL Server nuk po dëgjon në portin TCP/IP

**Zgjidhja:**
```
1. Hap SQL Server Configuration Manager
2. SQL Server Network Configuration → Protocols for MSSQLSERVER
3. Right-click TCP/IP → Enable
4. Restart SQL Server
```

### 5. "No module named 'pyodbc'"

**Problemi:** Libraritë nuk janë instaluar

**Zgjidhja:**
```bash
pip install pyodbc
```

---

## 📋 Kontroll-lista e Shpejtë

| Hapi | Veprimi | Statusi |
|------|---------|---------|
| ☐ | SQL Server është instaluar | |
| ☐ | ODBC Driver 17 është instaluar | |
| ☐ | Databaza `ocr_db` është krijuar | |
| ☐ | Fajlli `.env` është konfiguruar | |
| ☐ | Libraritë janë instaluar (`pip install`) | |
| ☐ | Testi i lidhjes kaloi | |
| ☐ | Aplikacioni niset | |

---

## 📞 Ndihmë Shtesë

Nëse ke ende probleme, kontrollo:
1. `README.md` - udhëzime më të detajuara
2. `database/schema.sql` - struktura e databazës
3. `test_connection.py` - për diagnostikim

**Suksese! 🎉**
