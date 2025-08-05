from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)
archivo_excel = 'INVENTARIORG.xlsx'

def leer_datos():
    return pd.read_excel(archivo_excel, sheet_name=None)

def guardar_datos(datos):
    with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='w') as writer:
        for hoja, df in datos.items():
            df.to_excel(writer, sheet_name=hoja, index=False)

@app.route('/')
def index():
    hoja_actual = request.args.get('hoja', default=None)
    datos = leer_datos()
    if hoja_actual not in datos:
        hoja_actual = list(datos.keys())[0]
    datos_filtrados = {hoja_actual: datos[hoja_actual]}
    return render_template('index.html', datos=datos_filtrados, hojas=list(datos.keys()), hoja_actual=hoja_actual)


@app.route('/buscar')
def buscar():
    query = request.args.get('q', '').lower().strip()
    datos = leer_datos()
    resultados = {}

    stopwords = {"de", "la", "el", "y", "a", "en", "con", "para", "por", "que", "un", "una", "los", "las", "del"}

    # Dividir y filtrar stopwords
    palabras = [p for p in query.split() if p not in stopwords]

    if not palabras:
        # Si la búsqueda quedó vacía después de filtrar, mostrar todo o nada
        return redirect(url_for('index'))

    for hoja, df in datos.items():
        df_str = df.astype(str).apply(lambda x: x.str.lower())

        def fila_coincide(fila):
            count = 0
            for palabra in palabras:
                if any(palabra in celda for celda in fila):
                    count += 1
            # Requiere al menos 60% de las palabras encontradas (puedes ajustar)
            return count / len(palabras) >= 0.6

        mask = df_str.apply(fila_coincide, axis=1)
        coincidencias = df[mask]

        if not coincidencias.empty:
            resultados[hoja] = coincidencias

    return render_template('index.html', datos=resultados, hojas=list(datos.keys()), hoja_actual=None, busqueda=query)

@app.route('/editar/<hoja>/<int:indice>', methods=['GET', 'POST'])
def editar(hoja, indice):
    datos = leer_datos()
    if hoja not in datos:
        return "Hoja no encontrada", 404
    df = datos[hoja]
    if indice < 0 or indice >= len(df):
        return "Refacción no encontrada", 404

    fila_encontrada = df.iloc[indice]

    if request.method == 'POST':
        for columna in df.columns:
            valor_form = request.form.get(columna)
            if valor_form is not None:
                df.at[indice, columna] = valor_form
        guardar_datos(datos)
        return redirect(url_for('index', hoja=hoja))

    return render_template('editar.html', ref=fila_encontrada, columnas=df.columns, hoja=hoja, indice=indice)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        datos = leer_datos()
        hoja = request.form.get('hoja')
        nueva_fila = {col: request.form.get(col, '') for col in datos[hoja].columns}
        datos[hoja] = pd.concat([datos[hoja], pd.DataFrame([nueva_fila])], ignore_index=True)
        guardar_datos(datos)
        return redirect(url_for('index'))

    datos = leer_datos()
    return render_template('agregar.html', hojas=list(datos.keys()), columnas=list(datos.values())[0].columns)

@app.route('/eliminar/<hoja>/<int:indice>')
def eliminar(hoja, indice):
    datos = leer_datos()
    if hoja not in datos:
        return "Hoja no encontrada", 404
    df = datos[hoja]
    if 0 <= indice < len(df):
        df = df.drop(index=indice).reset_index(drop=True)
        datos[hoja] = df
        guardar_datos(datos)
    return redirect(url_for('index', hoja=hoja))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

