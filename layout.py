# -*- coding: utf-8 -*-
from dash import dcc, html

def get_layout():
    return html.Div([
        html.Div([
            html.H1("Sistema de Validación y Sellado de PDFs"),
            
            html.Div([
                html.Label("Sube los archivos necesarios:"),
                html.P("Debes subir:", style={'margin': '5px 0 5px 20px', 'font-size': '0.9em', 'color': '#666'}),
                html.Ul([
                    html.Li("Archivo Excel (nombre-folio.xlsx)"),
                    html.Li("Imagen del sello (SELLO.png)"),
                    html.Li("Todos los PDFs a procesar")
                ], style={'margin': '0 0 10px 40px', 'font-size': '0.9em', 'color': '#666'}),
                
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Arrastra archivos aquí o ',
                        html.A('selecciona archivos')
                    ]),
                    style={
                        'width': '100%',
                        'height': '100px',
                        'lineHeight': '100px',
                        'borderWidth': '2px',
                        'borderStyle': 'dashed',
                        'borderRadius': '8px',
                        'borderColor': '#3d5a96',
                        'textAlign': 'center',
                        'backgroundColor': '#f8f9fa',
                        'cursor': 'pointer'
                    },
                    multiple=True
                ),
                html.Div(id='upload-status', style={'margin-top': '10px', 'font-size': '0.9em'})
            ], className='input-group'),
            
            html.Div([
                html.Button('Generar PDFs', id='btn-generar', className='btn-primary', n_clicks=0, disabled=True),
                html.Button('Limpiar', id='btn-limpiar', className='btn-secondary', n_clicks=0)
            ], className='button-group'),
            
            html.Div(id='output-mensaje', style={'display': 'none'}),
            
            html.Button(
                '📥 DESCARGAR ZIP', 
                id='btn-descargar', 
                n_clicks=0,
                style={'display': 'none'}
            ),
            
            dcc.Download(id='download-zip')
            
        ], className='container')
    ])
