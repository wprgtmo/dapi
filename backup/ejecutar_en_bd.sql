
ALTER TABLE IF EXISTS federations.clubs
ADD COLUMN siglas character varying;
UPDATE federations.clubs SET siglas='CFD' WHERE id=1;
UPDATE federations.clubs SET siglas='DBT' WHERE id=2;
UPDATE federations.clubs SET siglas='DKG' WHERE id=3;
UPDATE federations.clubs SET siglas='KDC' WHERE id=4;
UPDATE federations.clubs SET siglas='AUD' WHERE id=5;
UPDATE federations.clubs SET siglas='RUM' WHERE id=6;
UPDATE federations.clubs SET siglas='N/S' WHERE id=7;
UPDATE federations.clubs SET siglas='TAM' WHERE id=8;
UPDATE federations.clubs SET siglas='TEM' WHERE id=9;
UPDATE federations.clubs SET siglas='GUS' WHERE id=10;
