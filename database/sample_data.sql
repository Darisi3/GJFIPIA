USE ocr_db;
GO


INSERT INTO roles (role_name, created_at) 
VALUES 
    ('superadmin', SYSDATETIME()),
    ('admin', SYSDATETIME()),
    ('user', SYSDATETIME()),
    ('editor', SYSDATETIME());
GO


INSERT INTO permissions (permission_name, description) 
VALUES 
    ('delete_user', 'Mund të fshij përdorues'),
    ('delete_project', 'Mund të fshij projekte'),
    ('delete_image', 'Mund të fshij imazhe'),
    ('create_project', 'Mund të krijoj projekte'),
    ('edit_project', 'Mund të modifikoj projekte'),
    ('view_history', 'Mund të shoh historik'),
    ('manage_users', 'Mund të menaxhoj përdorues'),
    ('generate_content', 'Mund të gjeneroj përmbajtje');
GO


INSERT INTO role_permissions (role_id, permission_id) 
VALUES 
    ((SELECT id FROM roles WHERE role_name='superadmin'), (SELECT id FROM permissions WHERE permission_name='delete_user')),
    ((SELECT id FROM roles WHERE role_name='superadmin'), (SELECT id FROM permissions WHERE permission_name='delete_project')),
    ((SELECT id FROM roles WHERE role_name='superadmin'), (SELECT id FROM permissions WHERE permission_name='delete_image')),
    ((SELECT id FROM roles WHERE role_name='superadmin'), (SELECT id FROM permissions WHERE permission_name='manage_users')),
    ((SELECT id FROM roles WHERE role_name='admin'), (SELECT id FROM permissions WHERE permission_name='delete_project')),
    ((SELECT id FROM roles WHERE role_name='admin'), (SELECT id FROM permissions WHERE permission_name='delete_image')),
    ((SELECT id FROM roles WHERE role_name='admin'), (SELECT id FROM permissions WHERE permission_name='create_project')),
    ((SELECT id FROM roles WHERE role_name='admin'), (SELECT id FROM permissions WHERE permission_name='edit_project')),
    ((SELECT id FROM roles WHERE role_name='user'), (SELECT id FROM permissions WHERE permission_name='create_project')),
    ((SELECT id FROM roles WHERE role_name='user'), (SELECT id FROM permissions WHERE permission_name='view_history')),
    ((SELECT id FROM roles WHERE role_name='user'), (SELECT id FROM permissions WHERE permission_name='generate_content'));
GO


INSERT INTO users (role_id, username, password, email, created_at, last_login) 
VALUES 
    ((SELECT id FROM roles WHERE role_name='superadmin'), 'superadmin', 'hashed_password_123', 'superadmin@uni-gjilan.net', SYSDATETIME(), DATEADD(DAY, -1, SYSDATETIME())),
    ((SELECT id FROM roles WHERE role_name='admin'), 'admin', 'hashed_password_456', 'admin@uni-gjilan.net', SYSDATETIME(), DATEADD(HOUR, -3, SYSDATETIME())),
    ((SELECT id FROM roles WHERE role_name='user'), 'daris', 'hashed_password_789', 'daris.abdyli@uni-gjilan.net', DATEADD(DAY, -5, SYSDATETIME()), DATEADD(HOUR, -12, SYSDATETIME())),
    ((SELECT id FROM roles WHERE role_name='user'), 'artiola', 'hashed_password_101', 'artiola.hajdari@uni-gjilan.net', DATEADD(DAY, -7, SYSDATETIME()), DATEADD(DAY, -1, SYSDATETIME())),
    ((SELECT id FROM roles WHERE role_name='user'), 'eron', 'hashed_password_112', 'eron.ismajli@uni-gjilan.net', DATEADD(DAY, -10, SYSDATETIME()), DATEADD(HOUR, -6, SYSDATETIME())),
    ((SELECT id FROM roles WHERE role_name='editor'), 'bleonda', 'hashed_password_113', 'bleonda.halimi@uni-gjilan.net', DATEADD(DAY, -3, SYSDATETIME()), SYSDATETIME());
GO


INSERT INTO projects (user_id, name, description, source_url, created_at) 
VALUES 
    (3, 'Analiza Mediale Janar 2025', 'Analizë e lajmeve për muajin janar', 'https://example.com/janar2025', DATEADD(DAY, -30, SYSDATETIME())),
    (3, 'Ekskluzive Politike', 'Analizë e artikujve politikë', 'https://example.com/politike', DATEADD(DAY, -15, SYSDATETIME())),
    (4, 'Sporti Shqiptar', 'Analizë lajmesh sportive', 'https://example.com/sport', DATEADD(DAY, -20, SYSDATETIME())),
    (5, 'Kulturi dhe Arte', 'Artikuj mbi kulturën shqiptare', 'https://example.com/kulture', DATEADD(DAY, -10, SYSDATETIME())),
    (6, 'Ekonomi dhe Biznes', 'Analizë e artikujve ekonomikë', 'https://example.com/ekonomi', DATEADD(DAY, -5, SYSDATETIME()));
GO


INSERT INTO producers (name, type, model, created_at) 
VALUES 
    ('Scanner Canon', 'scanner', 'Canon DR-C240', SYSDATETIME()),
    ('Camera Sony', 'camera', 'Sony Alpha 7', DATEADD(DAY, -30, SYSDATETIME())),
    ('Scanner Fujitsu', 'scanner', 'Fujitsu fi-7160', DATEADD(DAY, -60, SYSDATETIME())),
    ('Mobile Phone', 'mobile', 'iPhone 15 Pro', DATEADD(DAY, -10, SYSDATETIME()));
GO


INSERT INTO languages (lang_code, lang_name, created_at) 
VALUES 
    ('sq', 'Shqip', SYSDATETIME()),
    ('en', 'Anglisht', SYSDATETIME()),
    ('sr', 'Serbisht', SYSDATETIME()),
    ('mk', 'Maqedonisht', SYSDATETIME()),
    ('it', 'Italisht', SYSDATETIME());
GO


INSERT INTO tags (name, description) 
VALUES 
    ('Politike', 'Artikuj politikë'),
    ('Sport', 'Lajme sportive'),
    ('Ekonomi', 'Lajme ekonomike'),
    ('Kulturë', 'Art dhe kulturë'),
    ('Teknologji', 'Teknologji dhe inovacion'),
    ('Shëndetësi', 'Shëndetësi dhe mjekësi'),
    ('Arsim', 'Arsim dhe edukim'),
    ('Ndërkombëtar', 'Lajme ndërkombëtare');
GO


INSERT INTO images (user_id, project_id, producer_id, file_name, file_path, file_type, file_size, resolution_width, resolution_height, uploaded_at, processed_at) 
VALUES 
    (3, 1, 1, 'gazeta_janar.jpg', '/uploads/gazeta_janar.jpg', 'image/jpeg', 2456789, 1920, 1080, DATEADD(DAY, -30, SYSDATETIME()), DATEADD(HOUR, 1, DATEADD(DAY, -30, SYSDATETIME()))),
    (3, 2, 2, 'politike_feb.jpg', '/uploads/politike_feb.jpg', 'image/jpeg', 1890456, 1600, 1200, DATEADD(DAY, -15, SYSDATETIME()), DATEADD(HOUR, 2, DATEADD(DAY, -15, SYSDATETIME()))),
    (4, 3, 3, 'sport_mars.jpg', '/uploads/sport_mars.jpg', 'image/png', 3123456, 2048, 1536, DATEADD(DAY, -20, SYSDATETIME()), DATEADD(HOUR, 1, DATEADD(DAY, -20, SYSDATETIME()))),
    (5, 4, 4, 'kulture_prill.jpg', '/uploads/kulture_prill.jpg', 'image/jpeg', 2789012, 1200, 1800, DATEADD(DAY, -10, SYSDATETIME()), DATEADD(HOUR, 3, DATEADD(DAY, -10, SYSDATETIME()))),
    (6, 5, 1, 'ekonomi_maj.jpg', '/uploads/ekonomi_maj.jpg', 'image/jpeg', 1987654, 1440, 900, DATEADD(DAY, -5, SYSDATETIME()), DATEADD(HOUR, 1, DATEADD(DAY, -5, SYSDATETIME())));
GO


INSERT INTO ocr_results (image_id, extracted_text, confidence_score, language_id, created_at) 
VALUES 
    (1, 'Presidenti i Republikës vizitoi rajonin e Veriut...', 94.50, 1, DATEADD(HOUR, 1, DATEADD(DAY, -30, SYSDATETIME()))),
    (2, 'Kuvendi miratoi ligjin e ri për investimet e huaja...', 89.75, 1, DATEADD(HOUR, 2, DATEADD(DAY, -15, SYSDATETIME()))),
    (3, 'Shqipëria fitoi medalje ari në kampionatin evropian...', 96.20, 1, DATEADD(HOUR, 1, DATEADD(DAY, -20, SYSDATETIME()))),
    (4, 'Festivali i Këngës tradicionale u zhvillua me sukses...', 87.30, 1, DATEADD(HOUR, 3, DATEADD(DAY, -10, SYSDATETIME()))),
    (5, 'Rritja e BNP-së për tremujorin e parë është 4.5%...', 92.10, 1, DATEADD(HOUR, 1, DATEADD(DAY, -5, SYSDATETIME())));
GO


INSERT INTO image_tags (image_id, tag_id) 
VALUES 
    (1, 1), (1, 8), 
    (2, 1),          
    (3, 2),          
    (4, 4), (4, 7),  
    (5, 3);          
GO


INSERT INTO preprocessing_logs (image_id, step_name, parameters, created_at) 
VALUES 
    (1, 'grayscale_conversion', '{"method": "luminosity"}', DATEADD(MINUTE, 5, DATEADD(DAY, -30, SYSDATETIME()))),
    (1, 'noise_reduction', '{"kernel": 3, "sigma": 1.5}', DATEADD(MINUTE, 10, DATEADD(DAY, -30, SYSDATETIME()))),
    (2, 'rotation_correction', '{"angle": 2.5}', DATEADD(MINUTE, 8, DATEADD(DAY, -15, SYSDATETIME()))),
    (3, 'contrast_adjustment', '{"alpha": 1.2, "beta": 10}', DATEADD(MINUTE, 12, DATEADD(DAY, -20, SYSDATETIME()))),
    (5, 'binarization', '{"threshold": 128}', DATEADD(MINUTE, 7, DATEADD(DAY, -5, SYSDATETIME())));
GO


INSERT INTO audit_logs (user_id, action_type, description, created_at) 
VALUES 
    (2, 'login', 'Përdoruesi admin u kyç në sistem', DATEADD(HOUR, -3, SYSDATETIME())),
    (3, 'project_create', 'U krijua projekti "Analiza Mediale Janar 2025"', DATEADD(DAY, -30, SYSDATETIME())),
    (4, 'image_upload', 'U ngarkua imazhi "sport_mars.jpg"', DATEADD(DAY, -20, SYSDATETIME())),
    (5, 'ocr_process', 'U përpunua OCR për imazhin "kulture_prill.jpg"', DATEADD(DAY, -10, SYSDATETIME())),
    (6, 'report_generate', 'U gjenerua raport për projektin "Ekonomi dhe Biznes"', DATEADD(DAY, -2, SYSDATETIME()));
GO


PRINT '==============================';
PRINT 'TË DHËNAT U FUTËN ME SUKSES';
PRINT '==============================';
PRINT '1. Roles: ' + CAST((SELECT COUNT(*) FROM roles) AS NVARCHAR) + ' rreshta';
PRINT '2. Permissions: ' + CAST((SELECT COUNT(*) FROM permissions) AS NVARCHAR) + ' rreshta';
PRINT '3. Users: ' + CAST((SELECT COUNT(*) FROM users) AS NVARCHAR) + ' rreshta';
PRINT '4. Projects: ' + CAST((SELECT COUNT(*) FROM projects) AS NVARCHAR) + ' rreshta';
PRINT '5. Images: ' + CAST((SELECT COUNT(*) FROM images) AS NVARCHAR) + ' rreshta';
PRINT '6. OCR Results: ' + CAST((SELECT COUNT(*) FROM ocr_results) AS NVARCHAR) + ' rreshta';
PRINT '==============================';
GO