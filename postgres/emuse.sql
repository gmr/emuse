CREATE DATABASE emuse;

\c emuse;

CREATE TABLE accounts (
    id             UUID PRIMARY KEY,
    first_name     TEXT NOT NULL,
    surname        TEXT NOT NULL,
    display_name   TEXT NOT NULL,
    email          TEXT NOT NULL,
    password       TEXT NOT NULL,
    date_of_birth  DATE,
    locale         TEXT NOT NULL DEFAULT 'en_US',
    timezone       TEXT NOT NULL DEFAULT 'UTC',
    activated      BOOLEAN NOT NULL DEFAULT FALSE,
    locked         BOOLEAN NOT NULL DEFAULT FALSE,
    memorial       BOOLEAN NOT NULL DEFAULT FALSE,
    administrator  BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX ON accounts (email);
