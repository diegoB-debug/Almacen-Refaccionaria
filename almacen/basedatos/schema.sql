CREATE TABLE IF NOT EXISTS Refaccion(
    codigo SERIAL PRIMARY KEY,
    codigobarras TEXT,
    articulo VARCHAR(50),
    num_parte VARCHAR(15),
    marca VARCHAR(15),
    categoria VARCHAR(20),
    precio FLOAT4,
    existencia INT DEFAULT 0,
    apartado INT DEFAULT 0,
    minimo INT,
    ubicacion VARCHAR(15),
    Estado VARCHAR(10) DEFAULT 'Agotado'
);