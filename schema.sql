CREATE TABLE IF NOT EXISTS inventario(
    id_producto INTEGER PRIMARY KEY,
    existencia INTEGER NOT NULL DEFAULT 0
        CHECK(existencia>=0)
);