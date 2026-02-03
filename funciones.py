# -*- coding: utf-8 -*-
import os
import zipfile
import pandas as pd
import fitz

def cargar_excel(ruta_excel):
    df = pd.read_excel(ruta_excel)
    df["Fecha"] = df["Fecha"].ffill()
    return df

def cargar_nombres_pdf(carpeta_pdf):
    return [f.split('.')[0] for f in os.listdir(carpeta_pdf) if f.endswith(".pdf")]

def procesar_pdfs(df, carpeta_pdfs, ruta_sello, carpeta_salida):
    archivos = []
    df['num_folio'] = df['num_folio'].astype(str)
    
    for idx, (index, row) in enumerate(df.iterrows()):
        nombre_pdf = row["nombre"]
        num_folio = "0" + row["num_folio"]
        fecha = str(row["Fecha"])
        
        pdf_path = os.path.join(carpeta_pdfs, f'{nombre_pdf}.pdf')
        
        if not os.path.exists(pdf_path):
            continue
        
        texto_despues_slash = pdf_path.split(os.sep)[-1]
        texto_desp_slash = texto_despues_slash.split('-', 1)[1]
        texto_final = texto_desp_slash.split('.')[0]
        nom_archivo = "Sellado-" + texto_final + ".pdf"
        output_pdf_path = os.path.join(carpeta_salida, nom_archivo)
        
        pdf = fitz.open(pdf_path)
        page = pdf[0]
        
        page.insert_text((415, 82), num_folio, fontname="Helvetica", fontsize=18, fill=(0, 0, 0))
        page.insert_text((120, 663), fecha, fontname="Helvetica", fontsize=10, fill=(0, 0, 0))
        
        if os.path.exists(ruta_sello):
            img = fitz.Pixmap(ruta_sello)
            rect = fitz.Rect(90, 600, 210, 720)
            page.insert_image(rect, pixmap=img)
        
        pdf.save(output_pdf_path)
        pdf.close()
        
        archivos.append(nom_archivo)
    
    return archivos

def crear_zip(carpeta_pdfs, ruta_zip):
    with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for archivo in os.listdir(carpeta_pdfs):
            if archivo.endswith('.pdf'):
                ruta_completa = os.path.join(carpeta_pdfs, archivo)
                zipf.write(ruta_completa, archivo)
    return ruta_zip
