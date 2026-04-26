CREATE TABLE IF NOT EXISTS zone (
    id VARCHAR(255) PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    type VARCHAR(50), -- ex: residential, commercial, highway
    latitude FLOAT,
    longitude FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS indicateur_trafic (
    event_id VARCHAR(255) PRIMARY KEY,
    zone_id VARCHAR(255) NOT NULL,
    date_heure TIMESTAMP NOT NULL,
    densite FLOAT NOT NULL,
    vitesse_moyenne FLOAT NOT NULL,
    taux_occupation FLOAT NOT NULL,
    etat_trafic VARCHAR(20) NOT NULL,
    CHECK (densite >= 0),
    CHECK (taux_occupation >= 0 AND taux_occupation <= 1),
    CHECK (vitesse_moyenne >= 0),

    FOREIGN KEY (zone_id) REFERENCES zone(id)
);

CREATE TABLE IF NOT EXISTS score_congestion (
    id SERIAL PRIMARY KEY,
    zone_id VARCHAR(255) NOT NULL,
    date_heure TIMESTAMP NOT NULL,
    score FLOAT NOT NULL,
    niveau VARCHAR(20) NOT NULL,
    CHECK (score >= 0 AND score <= 10),

    FOREIGN KEY (zone_id) REFERENCES zone(id)
);

CREATE INDEX idx_zone_date ON indicateur_trafic(zone_id, date_heure);
CREATE INDEX idx_score_zone_date ON score_congestion(zone_id, date_heure);