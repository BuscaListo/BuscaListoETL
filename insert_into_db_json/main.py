
import os
import pdb
import json
import time
import random
import string
import urllib
import psycopg2
import pandas as pd
from sys import argv
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Carga las variables del archivo .env
load_dotenv(dotenv_path='../.env')

# Accede a las variables de entorno
namedb = os.getenv('NAMEDB')
userdb = os.getenv('USERDB')
passworddb = os.getenv('PASSWORDDB')
portdb = os.getenv('PORTDB')
db = os.getenv('DB')
name_servicedb = os.getenv('NAME_SERVICEDB')

# Configuracion de directorio
path = os.path.dirname(os.path.abspath(__file__))

def get_db_engine():
    global namedb,userdb,passworddb,portdb,name_servicedb
    """Obtiene la instacia engine para la conexion e interaccion a la base de datos"""
    return create_engine(
        f"postgresql+psycopg2://"
        f"{userdb}:"
        f"{passworddb}@"
        f"{name_servicedb}:"
        f"{portdb}/"
        f"{namedb}"
    )

def gen_product_code(product_name="", category="", prefix="PRD"):
    """
    Función simple para generar código de producto único
    """    
    timestamp = str(int(time.time() * 1000))[-8:]  # Últimos 8 dígitos
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    category_part = category[:3].upper() if category else "GEN"
    name_part = product_name[:3].upper() if product_name else "PRO"
    
    return f"{prefix}{category_part}{name_part}{timestamp}{random_part}"

def insert_into_table(df_insert: pd.DataFrame, connx_eng, table_name):
    """Insert element into table_name given a df_input dataframe"""
    ck_size = int(float(2097 / len(df_insert.columns)))
    df_insert.to_sql(
        table_name,
        schema="public",
        con=connx_eng,
        chunksize=ck_size,
        method="multi",
        index=False,
        if_exists="append",
    )
    print(f"Insertado correctamente: {table_name}.\nRegistros insertados:{len(df_insert)}")

if __name__ == "__main__":
    # Configuración de conexión
    conn = psycopg2.connect(
        dbname=namedb,
        user=userdb,
        password=passworddb,
        host=name_servicedb,
        port=portdb
    )
    # Crear engine de SQLAlchemy
    engine = get_db_engine()
    engine.begin()
    eng = engine.connect()
    # Crear cursor
    curr = conn.cursor()
    print("Conexión exitosa a la base de datos")
    try:
        arg_file = [e for e in argv if '--file=' in e]
        if arg_file:
            file_name = arg_file[0].split('=')[1]
            print("Leyendo:", file_name)
        else:
            print("Falta parametro --file.")

        print('path:', path)
        #Leer archivo JSON
        file_path = os.path.join(path+'/'+'input', file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("Datos leídos del archivo JSON:", len(data))
        # Iterar productos
        productos = []
        # Obtener subcategorias
        df_subcategorias = pd.read_sql_query("SELECT nombre FROM subcategorias where activo = true", eng)
        print("Subcategorías obtenidas:", df_subcategorias.shape[0])
        # Obtener marcas
        df_marcas = pd.read_sql_query("SELECT nombre FROM marcas where activo = true", eng)
        print("Marcas obtenidas:", df_marcas.shape[0])
        # Obtener sucursales
        df_sucursales = pd.read_sql_query("select nombre from sucursales where activo = true", eng)
        print("Sucursales obtenidas:", df_sucursales.shape[0])
        for obj_product in data:
            print("Procesando producto:", obj_product["nombre_producto"]+obj_product["descripcion"])
            # Extract id_sub_categoria
            try:
                id_sub_categoria = df_subcategorias[df_subcategorias['nombre'] == obj_product["sub_categoria"]].index[0] + 1
            except IndexError:
                print(f"Subcategoría '{obj_product['sub_categoria']}' no encontrada.")
                print("Continuando con el siguiente producto...")
                continue
            print("Subcategoría encontrada: OK")
            # Extract id_marca
            try:
                id_marca = df_marcas[df_marcas['nombre'] == obj_product["marca"]].index[0] + 1
            except IndexError:
                print(f"Marca '{obj_product['marca']}' no encontrada.")
                print("Set marca generica")
                id_marca = df_marcas[df_marcas['nombre'] == "Generico"].index[0] + 1
            print("Marca encontrada: OK")
            # Extract id_sucursal
            try:
                id_sucursal = df_sucursales[df_sucursales['nombre'] == obj_product["Sucursal"]].index[0] + 1
            except IndexError:
                print(f"Sucursal '{obj_product['Sucursal']}' no encontrada.")
                print("Continuando con el siguiente producto...")
                continue
            producto = {
                "nombre": obj_product["nombre_producto"],
                "descripcion": obj_product["descripcion"],
                "precio_bs": obj_product["precio_bs"],
                "in_stock": 1 if obj_product["disponible"] is True else 0,
                "id_sub_categoria": id_sub_categoria,
                "id_marca": id_marca,
                "url_supplier": obj_product["url"],
                "views": obj_product["views"],
                "id_sucursal": id_sucursal,
                "activo": 1,
                "creado_por": "admin_script",
                "codigo": gen_product_code(product_name=obj_product["nombre_producto"], category=obj_product["sub_categoria"]),
                "imagenes": obj_product["imagen"]
            }
            productos.append(producto)
            print("Producto procesado para insertar.")
        # Insertar productos
        try:
            df_productos = pd.DataFrame(productos)
            cols_insert = df_productos.columns.tolist()
            cols_insert.remove("imagenes")
            insert_into_table(df_productos[cols_insert], eng, "producto")
            eng.commit()
        except Exception as e_insert:
            print("Error al insertar productos:", e_insert)
        # Insertar imagenes de productos
        try:
            # Obtener productos insertados
            df_productos_insert = pd.read_sql_query("SELECT id id_producto, codigo FROM producto where activo = 1 order by id desc limit "+str(len(df_productos)), eng)
            # Merge datos productos insert + datos imagenes
            df_merge = pd.merge(df_productos, df_productos_insert, on="codigo", how="inner")
            print("Productos/imagenes emparejados:", df_merge.shape[0])
            df_product_image = df_merge.copy()
            df_product_image = df_product_image.explode('imagenes',ignore_index=True)
            df_product_image.rename(columns={"imagenes": "url"}, inplace=True)
            print("Imagenes obtenidas a insertar:",len(df_product_image))
            insert_into_table(df_product_image[["id_producto", "url","creado_por"]], eng, "imagenes")
            eng.commit()
        except Exception as e_insert_img:
            print("Error al obtener productos insertados:", e_insert_img)
    except Exception as e:
        print("Error en el proceso:", e)
    finally:
        curr.close()
        conn.close()
        eng.close()
        print("Conexión cerrada")