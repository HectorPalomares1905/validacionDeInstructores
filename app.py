# -*- coding: utf-8 -*-
import os
import base64
import io
import tempfile
import shutil
import dash
from dash import html, Input, Output, State, dcc
from layout import get_layout
from funciones import cargar_excel, cargar_nombres_pdf, procesar_pdfs, crear_zip

app = dash.Dash(__name__)
server = app.server
app.layout = get_layout()

archivos_subidos = {}

@app.callback(
    [Output('upload-status', 'children'),
     Output('btn-generar', 'disabled')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def guardar_archivos(list_of_contents, list_of_names):
    if list_of_contents is None:
        return "", True
    
    temp_dir = tempfile.mkdtemp()
    archivos_subidos.clear()
    archivos_subidos['temp_dir'] = temp_dir
    
    excel_encontrado = False
    sello_encontrado = False
    pdfs_encontrados = 0
    
    for content, name in zip(list_of_contents, list_of_names):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        file_path = os.path.join(temp_dir, name)
        
        with open(file_path, 'wb') as f:
            f.write(decoded)
        
        if name == 'nombre-folio.xlsx':
            excel_encontrado = True
            archivos_subidos['excel'] = file_path
        elif name == 'SELLO.png':
            sello_encontrado = True
            archivos_subidos['sello'] = file_path
        elif name.endswith('.pdf'):
            pdfs_encontrados += 1
    
    status_messages = []
    if excel_encontrado:
        status_messages.append("✅ Excel cargado")
    else:
        status_messages.append("❌ Falta nombre-folio.xlsx")
    
    if sello_encontrado:
        status_messages.append("✅ Sello cargado")
    else:
        status_messages.append("❌ Falta SELLO.png")
    
    status_messages.append(f"📄 {pdfs_encontrados} PDFs cargados")
    
    todos_listos = excel_encontrado and sello_encontrado and pdfs_encontrados > 0
    
    return html.Div([html.P(msg, style={'margin': '2px 0'}) for msg in status_messages]), not todos_listos

@app.callback(
    [Output('output-mensaje', 'children'),
     Output('output-mensaje', 'style'),
     Output('btn-descargar', 'style')],
    Input('btn-generar', 'n_clicks'),
    prevent_initial_call=True
)
def generar_pdfs(n_clicks):
    estilo_visible = {'display': 'block', 'margin-top': '30px', 'padding': '20px', 'border-radius': '6px', 'background': '#ecf0f1'}
    estilo_boton_visible = {'display': 'block', 'margin': '20px auto', 'padding': '12px 30px', 'background': '#27ae60', 'color': 'white', 'border': 'none', 'border-radius': '6px', 'font-size': '16px', 'cursor': 'pointer', 'font-weight': 'bold'}
    estilo_boton_oculto = {'display': 'none'}
    
    if 'temp_dir' not in archivos_subidos:
        return html.Div("❌ Primero debes subir los archivos", style={'color': 'red'}), estilo_visible, estilo_boton_oculto
    
    try:
        temp_dir = archivos_subidos['temp_dir']
        ruta_excel = archivos_subidos['excel']
        ruta_sello = archivos_subidos['sello']
        
        carpeta_salida = os.path.join(temp_dir, "PDF_generados")
        os.makedirs(carpeta_salida, exist_ok=True)
        
        df = cargar_excel(ruta_excel)
        df["nombre"] = cargar_nombres_pdf(temp_dir)
        archivos = procesar_pdfs(df, temp_dir, ruta_sello, carpeta_salida)
        
        ruta_zip = os.path.join(temp_dir, "PDFs_Sellados.zip")
        crear_zip(carpeta_salida, ruta_zip)
        
        archivos_subidos['zip_path'] = ruta_zip
        
        return html.Div([
            html.H3("✅ PROCESO COMPLETADO", style={'color': 'green', 'margin-bottom': '10px'}),
            html.P(f"Total de archivos procesados: {len(archivos)}", style={'margin': '5px 0', 'color': '#555'}),
            html.P("✅ Los archivos están listos para descargar", style={'margin': '5px 0', 'color': '#2ecc71', 'font-weight': 'bold'}),
            html.P("👇 Presiona el botón verde de abajo para descargar", style={'margin': '10px 0', 'color': '#555', 'font-size': '0.9em'})
        ]), estilo_visible, estilo_boton_visible
        
    except Exception as e:
        import traceback
        error_detallado = traceback.format_exc()
        return html.Div([
            html.P(f"❌ Error: {str(e)}", style={'color': 'red', 'font-weight': 'bold'}),
            html.Pre(error_detallado, style={
                'background': '#f8f8f8', 
                'padding': '10px', 
                'border-radius': '4px', 
                'font-size': '0.75em', 
                'overflow': 'auto',
                'max-height': '300px'
            })
        ]), estilo_visible, estilo_boton_oculto

@app.callback(
    Output('download-zip', 'data'),
    Input('btn-descargar', 'n_clicks'),
    prevent_initial_call=True
)
def descargar_zip(n_clicks):
    if 'zip_path' not in archivos_subidos:
        return None
    
    try:
        ruta_zip = archivos_subidos['zip_path']
        
        if not os.path.exists(ruta_zip):
            return None
        
        with open(ruta_zip, 'rb') as f:
            zip_bytes = f.read()
        
        zip_base64 = base64.b64encode(zip_bytes).decode()
        
        return dict(
            content=zip_base64,
            filename="PDFs_Sellados.zip",
            base64=True
        )
    except Exception as e:
        print(f"Error en descarga: {str(e)}")
        return None

@app.callback(
    [Output('output-mensaje', 'children', allow_duplicate=True),
     Output('output-mensaje', 'style', allow_duplicate=True),
     Output('btn-descargar', 'style', allow_duplicate=True)],
    Input('btn-limpiar', 'n_clicks'),
    prevent_initial_call=True
)
def limpiar(n_clicks):
    if 'temp_dir' in archivos_subidos:
        shutil.rmtree(archivos_subidos['temp_dir'], ignore_errors=True)
        archivos_subidos.clear()
    
    return "", {'display': 'none'}, {'display': 'none'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port, debug=False)
