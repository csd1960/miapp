#--------------------------------------------------------------------
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename
import os
import time
#-------------------------------------------------------------------
app = Flask(__name__)
CORS(app) 

class Catalogo:

    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
            
        )
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
codigo INT,
descripcion VARCHAR(255) NOT NULL,
cantidad INT NOT NULL,
precio DECIMAL(10, 2) NOT NULL,
imagen_url VARCHAR(255),
proveedor INT)''')
        self.conn.commit()
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)
#----------------------------------------------------------------
    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos")
        productos = self.cursor.fetchall()
        return productos
    def consultar_producto(self, codigo):
        self.cursor.execute(f"SELECT * FROM productos WHERE codigo = {codigo}")
        return self.cursor.fetchone()
    def mostrar_producto(self, codigo):
        producto = self.consultar_producto(codigo)
        if producto:
            print("-" * 40)
            print(f"Código.....: {producto['codigo']}")
            print(f"Descripción: {producto['descripcion']}")
            print(f"Cantidad...: {producto['cantidad']}")
            print(f"Precio.....: {producto['precio']}")
            print(f"Imagen.....: {producto['imagen_url']}")
            print(f"Proveedor..: {producto['proveedor']}")
            print("-" * 40)
        else:
            print("Producto no encontrado.")

    def agregar_producto(self, codigo, descripcion, cantidad, precio, imagen, proveedor):
        self.cursor.execute(f"SELECT * FROM productos WHERE codigo = {codigo}")
        producto_existe = self.cursor.fetchone()
        if producto_existe:
            return False
        sql = "INSERT INTO productos (codigo, descripcion, cantidad, precio, imagen_url, proveedor) VALUES (%s, %s, %s, %s, %s, %s)"
        valores = (codigo, descripcion, cantidad, precio, imagen, proveedor)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return True
    
    def modificar_producto(self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor):
        sql = "UPDATE productos SET descripcion = %s, cantidad = %s, precio = %s, imagen_url = %s, proveedor = %s WHERE codigo = %s"
        valores = (nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def eliminar_producto(self, codigo):
        self.cursor.execute(f"DELETE FROM productos WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0

#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
#catalogo = Catalogo(host = 'localhost', user='root',password='',database='miapp')
catalogo = Catalogo(host='leonimariana60.mysql.pythonanywhere-services.com', user='leonimariana60', password='emi6264feli', database='leonimariana60$miapp')
#ruta_destino='static/img/'
ruta_destino = '/home/leonimariana60/mysite/static/img/'
# --------------------------------------------------------------------
@app.route("/productos", methods=["GET"])
def listar_productos():
    productos = catalogo.listar_productos()
    return jsonify(productos)

@app.route("/productos/<int:codigo>", methods=["GET"])
def mostrar_producto(codigo):
    producto = catalogo.consultar_producto(codigo)
    if producto:
        return jsonify(producto)
    else:
        return "Producto no encontrado", 404

@app.route("/productos", methods=["POST"])
def agregar_producto():
    codigo = request.form['codigo']
    descripcion = request.form['descripcion']
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    proveedor = request.form['proveedor'] 
    imagen = request.files['imagen']
    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen)
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
    imagen.save(os.path.join(ruta_destino, nombre_imagen))
    if catalogo.agregar_producto(codigo, descripcion, cantidad, precio, nombre_imagen, proveedor):
        return jsonify({"mensaje": "Producto agregado"}), 201
    else:
        return jsonify({"mensaje": "Producto ya existe"}), 400

@app.route("/productos/<int:codigo>", methods=["DELETE"])
def eliminar_producto(codigo):
    producto = catalogo.consultar_producto(codigo)
    if producto:
        ruta_imagen = os.path.join(ruta_destino, producto['imagen_url'])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        if catalogo.eliminar_producto(codigo):
            return jsonify({"mensaje": "Producto eliminado"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404

@app.route("/productos/<int:codigo>", methods=["PUT"])
def modificar_producto(codigo):
    nueva_descripcion = request.form.get("descripcion")
    nueva_cantidad = request.form.get("cantidad")
    nuevo_precio = request.form.get("precio")
    nuevo_proveedor = request.form.get("proveedor")
    imagen = request.files['imagen']
    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen)
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
    imagen.save(os.path.join(ruta_destino, nombre_imagen))
    
    if catalogo.modificar_producto(codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nombre_imagen, nuevo_proveedor):
        return jsonify({"mensaje": "Producto modificado"}), 200
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True)


