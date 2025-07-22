import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

EXCEL_FILE = 'INVENTARIO.xlsx'  # Pon aquí el nombre y ruta de tu archivo Excel

def cargar_datos():
    # Leer todas las hojas y concatenarlas
    xls = pd.ExcelFile(EXCEL_FILE)
    hojas = xls.sheet_names
    df_list = []
    for hoja in hojas:
        df = pd.read_excel(xls, hoja)
        df['Categoria'] = hoja  # Añadir columna para saber la hoja original
        df_list.append(df)
    df_total = pd.concat(df_list, ignore_index=True)
    return df_total

# Cargamos los datos inicialmente (puedes mejorar para que se actualice dinámicamente)
df_refacciones = cargar_datos()

@app.route('/', methods=['GET', 'POST'])
def index():
    global df_refacciones

    query = request.args.get('q', '').lower()

    if query:
        # Filtrar dataframe por cualquier columna que contenga la query
        mask = df_refacciones.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)
        resultados = df_refacciones[mask]
    else:
        resultados = df_refacciones

    return render_template('index.html', refacciones=resultados.to_dict(orient='records'), query=query)

if __name__ == '__main__':
    app.run(debug=True)
