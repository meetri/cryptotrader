-- Table: markets.trades

-- DROP DATABASE crypto;
CREATE DATABASE crypto;
-- USE crypto;
CREATE SCHEMA markets;

CREATE TABLE markets.orders
(
    id serial,
    assoc_id numeric,
    ref_id character varying(64),
    exchange character varying(20) COLLATE pg_catalog."default" NOT NULL,
    market character varying(20) COLLATE pg_catalog."default",
    order_type character varying(10) COLLATE pg_catalog."default",
    qty numeric,
    rate numeric,
    status numeric DEFAULT 0,
    created_by character varying(32),    
    created_ts timestamp with time zone DEFAULT now(),
    modified_ts timestamp with time zone DEFAULT now(),
    disabled boolean DEFAULT FALSE,
    meta jsonb,
    
    CONSTRAINT morder_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE markets.orders
    OWNER to postgres;

-- OBSOLETE --
CREATE TABLE markets.trades
(
    id SERIAL,
    exchange character varying(20) COLLATE pg_catalog."default" NOT NULL,
    market character varying(20) COLLATE pg_catalog."default",
    quantity numeric,
    price numeric,
    trade_type character varying(10) COLLATE pg_catalog."default",
    order_type character varying(10) COLLATE pg_catalog."default",
    status character varying(32) COLLATE pg_catalog."default",
    active boolean,
    managed_by character varying(20) COLLATE pg_catalog."default",
    created_by character varying(20) COLLATE pg_catalog."default",
    modified_by character varying(20) COLLATE pg_catalog."default",
    created_ts timestamp with time zone DEFAULT now(),
    modified_ts timestamp with time zone DEFAULT now(),
    meta jsonb,
    CONSTRAINT mtrades_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE markets.trades
    OWNER to postgres;
