-- CareCloud AI Engineer Assessment
-- Supabase / PostgreSQL schema for the patient registration API
--
-- Run this entire file in:
-- Supabase Dashboard -> SQL Editor -> New query -> Run
--
-- This schema is safe to run on a fresh assessment database.
-- It creates the pgcrypto extension and the patients table.

create extension if not exists "pgcrypto";

create table if not exists patients (
    patient_id uuid primary key default gen_random_uuid(),

    first_name varchar(50) not null,
    last_name varchar(50) not null,
    date_of_birth date not null,
    sex varchar(20) not null,
    phone_number varchar(10) not null,

    email varchar(255),

    address_line_1 text not null,
    address_line_2 text,
    city varchar(100) not null,
    state varchar(2) not null,
    zip_code varchar(10) not null,

    insurance_provider text,
    insurance_member_id text,
    preferred_language varchar(100) default 'English',

    emergency_contact_name text,
    emergency_contact_phone varchar(10),

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    deleted_at timestamptz
);

-- Helpful indexes for the API filters and duplicate-phone lookup.
create index if not exists idx_patients_last_name
    on patients (last_name);

create index if not exists idx_patients_date_of_birth
    on patients (date_of_birth);

create index if not exists idx_patients_phone_number
    on patients (phone_number);

-- Partial index keeps deleted records out of the active phone lookup path.
create index if not exists idx_patients_active_phone
    on patients (phone_number)
    where deleted_at is null;
