CREATE TABLE delivery_orders (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    provider VARCHAR(32) NOT NULL,
    third_order_id VARCHAR(64) NOT NULL,
    delivery_status VARCHAR(32) NOT NULL,
    fee DECIMAL(10, 2) NOT NULL DEFAULT 0,
    courier_info JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (provider, third_order_id)
);

CREATE TABLE company_delivery_providers (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    company_id VARCHAR(64) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    settlement_policy VARCHAR(64) NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_company_delivery_providers_company_id
    ON company_delivery_providers(company_id);
