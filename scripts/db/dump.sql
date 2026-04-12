CREATE TYPE event_type_enum AS ENUM (
    'login_success',
    'login_failed'
);

CREATE TYPE user_enum AS ENUM (
    'admin',
    'member'
);

CREATE TYPE alert_type_enum AS ENUM (
    'brute_force_detected',
    'suspicious'
);

CREATE TYPE severity_type_enum AS ENUM (
    'low',
    'medium',
    'high'
);

CREATE TABLE IF NOT EXISTS public.events
(
    id SERIAL PRIMARY KEY,
    event_type event_type_enum,
    user_type user_enum,
    ip_address VARCHAR,
    datetime TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.alerts
(
    id SERIAL PRIMARY KEY,
    alert_type alert_type_enum,
    severity severity_type_enum,
    ip_address VARCHAR,
    created_at TIMESTAMP,
    event_id INTEGER NOT NULL,
    CONSTRAINT alerts_event_id_fkey FOREIGN KEY (event_id)
        REFERENCES public.events (id)
        ON DELETE NO ACTION
);