CREATE SCHEMA content;

ALTER ROLE app SET search_path TO content,public;

CREATE TABLE IF NOT EXISTS content.users (
    id UUID PRIMARY KEY,
    login VARCHAR(255),
    password VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS content.roles (
    id UUID PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS content.permissions (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    description TEXT
);

CREATE TABLE IF NOT EXISTS content.user_roles (
    user_id UUID REFERENCES content.users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES content.roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS content.role_permissions (
    role_id UUID REFERENCES content.roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES content.permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);


CREATE TABLE IF NOT EXISTS content.user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID,
    auth_date TIMESTAMP,
    last_date TIMESTAMP,
    creation_date TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES content.users(id) ON DELETE CASCADE
);

CREATE INDEX role_permissions_idx ON content.role_permissions(role_id, permission_id);
CREATE INDEX user_sessions_idx ON content.user_sessions(user_id);
CREATE UNIQUE INDEX users_idx ON content.users (id);