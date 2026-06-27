-- Phase F: one shared Postgres cluster for the whole Studio.
-- POSTGRES_DB already created the Coding (ACE) database. Here we add the Policy
-- (P2R) database in the same instance, and ensure pgvector exists in both.
-- Runs once, only when the data volume is first initialized.

CREATE EXTENSION IF NOT EXISTS vector;          -- in the default (coding/ace) database

CREATE DATABASE p2r;
\connect p2r
CREATE EXTENSION IF NOT EXISTS vector;           -- in the policy (p2r) database
