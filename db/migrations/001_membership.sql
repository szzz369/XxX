CREATE TABLE member_level (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name VARCHAR(50) NOT NULL,
  growth_threshold INT NOT NULL,
  discount_rate DECIMAL(5, 2) NOT NULL DEFAULT 1.00,
  points_multiplier DECIMAL(5, 2) NOT NULL DEFAULT 1.00,
  free_shipping_threshold DECIMAL(10, 2) DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX member_level_name_unique ON member_level (name);
CREATE UNIQUE INDEX member_level_threshold_unique ON member_level (growth_threshold);

CREATE TABLE user_membership (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_id BIGINT NOT NULL,
  member_level_id BIGINT NOT NULL REFERENCES member_level (id),
  growth_value INT NOT NULL DEFAULT 0,
  valid_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  valid_to TIMESTAMP NULL,
  upgraded_at TIMESTAMP NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX user_membership_user_id_idx ON user_membership (user_id);
CREATE INDEX user_membership_level_idx ON user_membership (member_level_id);

CREATE TABLE user_membership_upgrade (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_id BIGINT NOT NULL,
  from_level_id BIGINT NOT NULL REFERENCES member_level (id),
  to_level_id BIGINT NOT NULL REFERENCES member_level (id),
  growth_value INT NOT NULL,
  reason VARCHAR(100) NOT NULL,
  occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX user_membership_upgrade_user_idx ON user_membership_upgrade (user_id);

CREATE TABLE membership_upgrade_rule (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  member_level_id BIGINT NOT NULL REFERENCES member_level (id),
  rule_type VARCHAR(30) NOT NULL,
  threshold_value DECIMAL(12, 2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX membership_upgrade_rule_level_idx ON membership_upgrade_rule (member_level_id);
CREATE INDEX membership_upgrade_rule_type_idx ON membership_upgrade_rule (rule_type);
