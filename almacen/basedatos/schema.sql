CREATE TABLE IF NOT EXISTS Refaccion(
    sku SERIAL PRIMARY KEY,
    codigobarras TEXT,
    nombre VARCHAR(50),
    num_parte VARCHAR(15),
    modelo VARCHAR(15),
    yr SMALLINT,
    descr TEXT,
    url_imagen TEXT
);