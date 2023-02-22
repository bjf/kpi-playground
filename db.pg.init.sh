set -e

psql -v ON_ERROR_STOP=1 --username "kpis" --dbname "kpis" <<-EOSQL
    CREATE DATABASE kpis;
    CREATE USER kpis with ENCRYPTED PASSWORD 'kpis';
    GRANT ALL PRIVILEGES ON DATABASE kpis TO kpis;
EOSQL
