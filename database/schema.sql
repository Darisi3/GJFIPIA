IF DB_ID('ocr_db') IS NOT NULL
    DROP DATABASE ocr_db;
GO

CREATE DATABASE ocr_db;
GO

USE ocr_db;
GO


CREATE TABLE roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    role_name NVARCHAR(50) NOT NULL,
    created_at DATETIME2 DEFAULT SYSDATETIME()
);
GO


CREATE TABLE permissions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    permission_name NVARCHAR(100) NOT NULL,
    description NVARCHAR(MAX)
);
GO


CREATE TABLE role_permissions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);
GO


CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    role_id INT NOT NULL,
    username NVARCHAR(50) UNIQUE NOT NULL,
    password NVARCHAR(255) NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    created_at DATETIME2 DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NULL,
    last_login DATETIME2 NULL,
    is_deleted BIT DEFAULT 0,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);
GO


CREATE TABLE projects (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    name NVARCHAR(100) NOT NULL,
    description NVARCHAR(MAX),
    source_url NVARCHAR(255),    
    created_at DATETIME2 DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NULL,
    is_deleted BIT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
GO


CREATE TABLE producers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100),
    type NVARCHAR(50),
    model NVARCHAR(50),
    created_at DATETIME2 DEFAULT SYSDATETIME()
);
GO


CREATE TABLE images (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    project_id INT NULL,
    producer_id INT NULL,
    file_name NVARCHAR(255),
    file_path NVARCHAR(255),
    file_type NVARCHAR(50),
    file_size INT,
    resolution_width INT,
    resolution_height INT,
    uploaded_at DATETIME2 DEFAULT SYSDATETIME(),
    processed_at DATETIME2 NULL,
    is_deleted BIT DEFAULT 0,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (producer_id) REFERENCES producers(id)
);
GO


CREATE TABLE languages (
    id INT IDENTITY(1,1) PRIMARY KEY,
    lang_code NVARCHAR(10),
    lang_name NVARCHAR(50),
    created_at DATETIME2 DEFAULT SYSDATETIME()
);
GO


CREATE TABLE ocr_results (
    id INT IDENTITY(1,1) PRIMARY KEY,
    image_id INT NOT NULL,
    extracted_text NVARCHAR(MAX),
    confidence_score DECIMAL(5,2),
    language_id INT,
    created_at DATETIME2 DEFAULT SYSDATETIME(),
    is_deleted BIT DEFAULT 0,

    FOREIGN KEY (image_id) REFERENCES images(id),
    FOREIGN KEY (language_id) REFERENCES languages(id)
);
GO


CREATE TABLE tags (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(50) NOT NULL,
    description NVARCHAR(MAX)
);
GO


CREATE TABLE image_tags (
    id INT IDENTITY(1,1) PRIMARY KEY,
    image_id INT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (image_id) REFERENCES images(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
GO


CREATE TABLE preprocessing_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    image_id INT NOT NULL,
    step_name NVARCHAR(100),
    parameters NVARCHAR(MAX),
    created_at DATETIME2 DEFAULT SYSDATETIME(),
    FOREIGN KEY (image_id) REFERENCES images(id)
);
GO


CREATE TABLE error_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    image_id INT NULL,
    error_message NVARCHAR(MAX),
    error_code NVARCHAR(50),
    created_at DATETIME2 DEFAULT SYSDATETIME(),
    FOREIGN KEY (image_id) REFERENCES images(id)
);
GO


CREATE TABLE audit_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NULL,
    action_type NVARCHAR(100),
    description NVARCHAR(MAX),
    created_at DATETIME2 DEFAULT SYSDATETIME(),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
GO


CREATE TABLE delete_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    deleted_by_user_id INT NOT NULL,
    target_table NVARCHAR(50) NOT NULL,
    target_id INT NOT NULL,
    reason NVARCHAR(MAX) NULL,
    deleted_at DATETIME2 DEFAULT SYSDATETIME(),
    FOREIGN KEY (deleted_by_user_id) REFERENCES users(id)
);
GO

INSERT INTO roles (role_name) VALUES ('admin');
INSERT INTO roles (role_name) VALUES ('superadmin');
GO


INSERT INTO permissions (permission_name, description)
VALUES
('delete_user', 'Mund të fshij administratorë'),
('delete_project', 'Mund të fshij projekte'),
('delete_image', 'Mund të fshij imazhe');
GO


DECLARE @admin_id INT = (SELECT id FROM roles WHERE role_name='admin');
DECLARE @superadmin_id INT = (SELECT id FROM roles WHERE role_name='superadmin');


INSERT INTO role_permissions (role_id, permission_id)
SELECT @admin_id, id
FROM permissions
WHERE permission_name IN ('delete_project','delete_image');

INSERT INTO role_permissions (role_id, permission_id)
SELECT @superadmin_id, id FROM permissions;
GO