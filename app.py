from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd

app = Flask(__name__)
db_path = 'inventario.db'

def leer_hojas():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tablas

def leer_datos(tabla):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f'SELECT * FROM "{tabla}"', conn)
    conn.close()
    return df

def actualizar_datos(tabla, df):
    conn = sqlite3.connect(db_path)
    df.to_sql(tabla, conn, if_exists='replace', index=False)
    conn.close()

@app.route('/')
def index():
    hoja_actual = request.args.get('hoja')
    hojas = leer_hojas()
    if hoja_actual not in hojas:
        hoja_actual = hojas[0]
    datos = leer_datos(hoja_actual)
    return render_template('index.html', datos={hoja_actual: datos}, hojas=hojas, hoja_actual=hoja_actual)

@app.route('/buscar')
def buscar():
    query = request.args.get('q', '').lower().strip()
    hojas = leer_hojas()
    resultados = {}
    stopwords = {"de", "la", "el", "y", "a", "en", "con", "para", "por", "que", "un", "una", "los", "las", "del"}

    palabras = [p for p in query.split() if p not in stopwords]

    if not palabras:
        return redirect(url_for('index'))

    for hoja in hojas:
        df = leer_datos(hoja)
        df_str = df.astype(str).apply(lambda x: x.str.lower())

        def fila_coincide(fila):
            count = 0
            for palabra in palabras:
                if any(palabra in celda for celda in fila):
                    count += 1
            return count / len(palabras) >= 0.6

        mask = df_str.apply(fila_coincide, axis=1)
        coincidencias = df[mask]

        if not coincidencias.empty:
            resultados[hoja] = coincidencias

    return render_template('index.html', datos=resultados, hojas=hojas, hoja_actual=None, busqueda=query)

@app.route('/editar/<hoja>/<int:indice>', methods=['GET', 'POST'])
def editar(hoja, indice):
    hojas = leer_hojas()
    if hoja not in hojas:
        return "Hoja no encontrada", 404
    df = leer_datos(hoja)
    if indice < 0 or indice >= len(df):
        return "Refacción no encontrada", 404

    fila_encontrada = df.iloc[indice].copy()

    if request.method == 'POST':
        nueva_hoja = request.form.get('nueva_hoja', hoja)

        # Actualizamos los valores del formulario
        for columna in df.columns:
            valor_form = request.form.get(columna)
            if valor_form is not None:
                fila_encontrada[columna] = valor_form

        if nueva_hoja == hoja:
            # Si sigue en la misma hoja, actualizamos en el mismo lugar
            df.iloc[indice] = fila_encontrada
            actualizar_datos(hoja, df)
        else:
            # Si cambia de hoja, lo movemos
            df = df.drop(index=indice).reset_index(drop=True)
            actualizar_datos(hoja, df)

            # Agregar en la nueva hoja
            df_nueva = leer_datos(nueva_hoja)
            df_nueva = pd.concat([df_nueva, pd.DataFrame([fila_encontrada])], ignore_index=True)
            actualizar_datos(nueva_hoja, df_nueva)

        return redirect(url_for('index', hoja=nueva_hoja))

    return render_template('editar.html', ref=fila_encontrada, columnas=df.columns, hoja=hoja, indice=indice, hojas=hojas)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    hojas = leer_hojas()
    if request.method == 'POST':
        hoja = request.form.get('hoja')
        df = leer_datos(hoja)
        nueva_fila = {col: request.form.get(col, '') for col in df.columns}
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        actualizar_datos(hoja, df)
        return redirect(url_for('index'))

    return render_template('agregar.html', hojas=hojas, columnas=leer_datos(hojas[0]).columns)

@app.route('/eliminar/<hoja>/<int:indice>')
def eliminar(hoja, indice):
    hojas = leer_hojas()
    if hoja not in hojas:
        return "Hoja no encontrada", 404
    df = leer_datos(hoja)
    if 0 <= indice < len(df):
        df = df.drop(index=indice).reset_index(drop=True)
        actualizar_datos(hoja, df)
    return redirect(url_for('index', hoja=hoja))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
