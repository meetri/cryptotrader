-- Table: markets.trades

-- DROP TABLE markets.trades;

CREATE TABLE markets.trades
(
    id integer NOT NULL DEFAULT nextval('markets.trades_id_seq1'::regclass),
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
