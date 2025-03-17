CREATE DATABASE emuse;

\c emuse;

DROP SCHEMA v1 CASCADE;

CREATE SCHEMA v1;

SET search_path=v1;

CREATE TABLE v1.accounts (
    id             UUID PRIMARY KEY,
    signup_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at  TIMESTAMP WITH TIME ZONE,
    first_name     TEXT NOT NULL,
    surname        TEXT NOT NULL,
    display_name   TEXT NOT NULL,
    email          TEXT NOT NULL,
    password       TEXT NOT NULL,
    salt           BYTEA NOT NULL,
    date_of_birth  DATE,
    locale         TEXT NOT NULL DEFAULT 'en_US',
    timezone       TEXT NOT NULL DEFAULT 'UTC',
    activated      BOOLEAN NOT NULL DEFAULT FALSE,
    locked         BOOLEAN NOT NULL DEFAULT FALSE,
    memorial       BOOLEAN NOT NULL DEFAULT FALSE,
    administrator  BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX ON v1.accounts (email);

CREATE TYPE v1.privacy_level AS ENUM ('public', 'logged-in-only', 'friends-only', 'private');

CREATE TABLE IF NOT EXISTS v1.poetry (
    id             UUID PRIMARY KEY,
    owner          UUID REFERENCES v1.accounts (id) ON DELETE CASCADE ON UPDATE CASCADE,
    title          TEXT,
    created_at     DATE  DEFAULT CURRENT_DATE,
    posted_at      TIMESTAMP WITH TIME ZONE  DEFAULT CURRENT_TIMESTAMP,
    language       TEXT,
    explicit       BOOLEAN,
    privacy_level  privacy_level  DEFAULT 'public',
    content        TEXT,
    notes          TEXT,
    tags           TEXT[]
);
