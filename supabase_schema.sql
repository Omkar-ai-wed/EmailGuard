
CREATE TABLE users (
	id SERIAL NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	hashed_password VARCHAR(255) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	last_login TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id)
)

;

CREATE INDEX ix_users_id ON users (id);

CREATE UNIQUE INDEX ix_users_username ON users (username);

CREATE UNIQUE INDEX ix_users_email ON users (email);


CREATE TABLE emails (
	id SERIAL NOT NULL, 
	message_id VARCHAR(255), 
	sender_email VARCHAR(255) NOT NULL, 
	sender_domain VARCHAR(100), 
	recipient_email VARCHAR(255), 
	subject VARCHAR(500), 
	body_text TEXT, 
	body_html TEXT, 
	received_at TIMESTAMP WITH TIME ZONE, 
	ingested_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	has_attachments BOOLEAN, 
	link_count INTEGER, 
	risk_score FLOAT, 
	category VARCHAR(20), 
	status VARCHAR(20), 
	is_phishing BOOLEAN, 
	ingested_by_user_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(ingested_by_user_id) REFERENCES users (id)
)

;

CREATE UNIQUE INDEX ix_emails_message_id ON emails (message_id);

CREATE INDEX ix_emails_risk_score ON emails (risk_score);

CREATE INDEX ix_emails_status ON emails (status);

CREATE INDEX ix_emails_id ON emails (id);

CREATE INDEX ix_emails_sender_domain ON emails (sender_domain);

CREATE INDEX ix_emails_sender_email ON emails (sender_email);

CREATE INDEX ix_emails_ingested_at_category ON emails (ingested_at, category);

CREATE INDEX ix_emails_category ON emails (category);

CREATE INDEX ix_emails_sender_domain_status ON emails (sender_domain, status);


CREATE TABLE classifications (
	id SERIAL NOT NULL, 
	email_id INTEGER NOT NULL, 
	method VARCHAR(20) NOT NULL, 
	predicted_category VARCHAR(20), 
	confidence_score FLOAT, 
	rule_triggered VARCHAR(255), 
	ml_score FLOAT, 
	keyword_score FLOAT, 
	reputation_score FLOAT, 
	classified_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	classified_by INTEGER, 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(email_id) REFERENCES emails (id), 
	FOREIGN KEY(classified_by) REFERENCES users (id)
)

;

CREATE INDEX ix_classifications_email_id ON classifications (email_id);

CREATE INDEX ix_classifications_id ON classifications (id);


CREATE TABLE keywords (
	id SERIAL NOT NULL, 
	keyword VARCHAR(100) NOT NULL, 
	weight FLOAT NOT NULL, 
	category_tag VARCHAR(20), 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	hit_count INTEGER, 
	PRIMARY KEY (id)
)

;

CREATE UNIQUE INDEX ix_keywords_keyword ON keywords (keyword);

CREATE INDEX ix_keywords_id ON keywords (id);


CREATE TABLE sender_reputation (
	id SERIAL NOT NULL, 
	sender_email VARCHAR(255), 
	sender_domain VARCHAR(100) NOT NULL, 
	reputation_score FLOAT, 
	category VARCHAR(20), 
	is_blacklisted BOOLEAN, 
	total_emails_received INTEGER, 
	spam_count INTEGER, 
	last_seen TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	notes TEXT, 
	PRIMARY KEY (id)
)

;

CREATE UNIQUE INDEX ix_sender_reputation_sender_domain ON sender_reputation (sender_domain);

CREATE INDEX ix_sender_reputation_sender_email ON sender_reputation (sender_email);

CREATE INDEX ix_sender_reputation_id ON sender_reputation (id);


CREATE TABLE attachments (
	id SERIAL NOT NULL, 
	email_id INTEGER NOT NULL, 
	filename VARCHAR(255), 
	file_type VARCHAR(50), 
	file_size_bytes INTEGER, 
	mime_type VARCHAR(100), 
	is_suspicious BOOLEAN, 
	scan_result VARCHAR(20), 
	scanned_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(email_id) REFERENCES emails (id)
)

;

CREATE INDEX ix_attachments_email_id ON attachments (email_id);

CREATE INDEX ix_attachments_id ON attachments (id);


CREATE TABLE links (
	id SERIAL NOT NULL, 
	email_id INTEGER NOT NULL, 
	url VARCHAR(2000), 
	domain VARCHAR(255), 
	is_suspicious BOOLEAN, 
	is_phishing_url BOOLEAN, 
	redirect_count INTEGER, 
	scan_result VARCHAR(20), 
	scanned_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(email_id) REFERENCES emails (id)
)

;

CREATE INDEX ix_links_email_id ON links (email_id);

CREATE INDEX ix_links_id ON links (id);


CREATE TABLE alerts (
	id SERIAL NOT NULL, 
	email_id INTEGER, 
	alert_type VARCHAR(50) NOT NULL, 
	severity VARCHAR(20) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	description TEXT NOT NULL, 
	is_resolved BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	resolved_at TIMESTAMP WITH TIME ZONE, 
	resolved_by INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(email_id) REFERENCES emails (id), 
	FOREIGN KEY(resolved_by) REFERENCES users (id)
)

;

CREATE INDEX ix_alerts_email_id ON alerts (email_id);

CREATE INDEX ix_alerts_id ON alerts (id);


CREATE TABLE performance_metrics (
	id SERIAL NOT NULL, 
	model_version VARCHAR(50), 
	accuracy FLOAT NOT NULL, 
	precision_score FLOAT NOT NULL, 
	recall_score FLOAT NOT NULL, 
	f1_score FLOAT NOT NULL, 
	auc_roc FLOAT, 
	true_positives INTEGER, 
	false_positives INTEGER, 
	true_negatives INTEGER, 
	false_negatives INTEGER, 
	training_samples INTEGER, 
	recorded_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
)

;

CREATE INDEX ix_performance_metrics_id ON performance_metrics (id);

