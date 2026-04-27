import sys
from sqlalchemy.schema import CreateTable
from database import engine, Base
import models

with open("../supabase_schema.sql", "w") as f:
    for name, table in Base.metadata.tables.items():
        create_stmt = str(CreateTable(table).compile(engine))
        f.write(create_stmt + ";\n\n")

        # Also get indexes
        for index in table.indexes:
            from sqlalchemy.schema import CreateIndex
            idx_stmt = str(CreateIndex(index).compile(engine))
            f.write(idx_stmt + ";\n\n")

print("Schema generated")
