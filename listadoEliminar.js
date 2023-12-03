const URL = "http://127.0.0.1:5000/"
const app = Vue.createApp({
    data() {
        return {
        productos: []
        }
    },

methods: {
    obtenerProductos() {
        fetch(URL + 'productos')
            .then(response => {
                if (response.ok) { return response.json(); }
            })
            .then(data => {
                this.productos = data;
            })
            .catch(error => {
                console.log('Error:', error);
                alert('Error al obtener los productos.');
            });
    },
    eliminarProducto(codigo) {
        if (confirm('¿Estás seguro de que quieres eliminar este producto?')) {
            fetch(URL + `productos/${codigo}`, { method: 'DELETE' })
                .then(response => {
                    if (response.ok) {
                        this.productos = this.productos.filter(producto => producto.codigo !== codigo);
                        alert('Producto eliminado correctamente.');
                    }
                })
                .catch(error => {
                    alert(error.message);
                 });
            }
       }
    },
    mounted() {
    this.obtenerProductos();
}});
app.mount('body');