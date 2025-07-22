import pandas as pd
import sqlite3

archivo_excel = "INVENTARIO.xlsx"
hojas = pd.read_excel(archivo_excel, sheet_name=None)

conn = sqlite3.connect("refacciones.db")
todo = []

for nombre_hoja, df in hojas.items():
    df.columns = [col.strip() for col in df.columns]  # Elimina espacios
    df["categoria"] = nombre_hoja.strip()

    # Limpia columna PRECIO (quita '$' si lo tiene)
    if "PRECIO" in df.columns:
        df["PRECIO"] = df["PRECIO"].astype(str).str.replace("$", "").str.strip()
        df["PRECIO"] = pd.to_numeric(df["PRECIO"], errors="coerce").fillna(0)

    # Llena vacíos con valores vacíos o por defecto
    df = df.fillna({
        "MARCA": "",
        "MODELO": "",
        "No. SKU": "",
        "PRODUCTO": "",
        "PRECIO": 0,
        "QTY": 0
    })

    todo.append(df)

refacciones = pd.concat(todo, ignore_index=True)
refacciones.to_sql("refacciones", conn, if_exists="replace", index=False)
conn.close()

print("Base de datos creada: refacciones.db")
