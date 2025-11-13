import pytest
from app import app, clients, orders, invoices, inventory, agenda

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_redirect(client):
    response = client.get('/')
    assert response.status_code == 302
    assert b'/login' in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_dashboard_authenticated(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_clients_page(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/clientes')
    assert response.status_code == 200
    assert b'Clientes' in response.data

def test_orders_page(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/ordenes')
    assert response.status_code == 200
    assert b'\xc3\x93rdenes' in response.data

def test_invoices_page(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/facturacion')
    assert response.status_code == 200
    assert b'Facturaci\xc3\xb3n' in response.data

def test_inventory_page(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/inventario')
    assert response.status_code == 200
    assert b'Inventario' in response.data

def test_agenda_page(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/agenda')
    assert response.status_code == 200
    assert b'Agenda' in response.data

def test_data_integrity():
    assert len(clients) == 2
    assert len(orders) == 2
    assert len(invoices) == 2
    assert len(inventory) == 3
    assert len(agenda) == 2

def test_client_data():
    client = clients[0]
    assert client['name'] == 'Juan Pérez'

def test_login_post(client):
    response = client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    assert response.status_code == 302
    assert '/dashboard' in response.location

def test_logout(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/logout')
    assert response.status_code == 302
    assert '/login' in response.location

def test_unauthenticated_access(client):
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.location

def test_forgot_password_page(client):
    response = client.get('/olvide-contrasena')
    assert response.status_code == 200
    assert b'En Construccion' in response.data

def test_new_order_form(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/nueva-orden')
    assert response.status_code == 200
    assert b'Nueva Orden' in response.data

def test_new_invoice_form(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/nueva-factura')
    assert response.status_code == 200
    assert b'Nueva Factura' in response.data

def test_add_product_form(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/agregar-producto')
    assert response.status_code == 200
    assert b'Agregar Producto' in response.data

def test_new_appointment_form(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.get('/agendar-cita')
    assert response.status_code == 200
    assert b'Nueva Cita' in response.data

def test_post_new_order(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.post('/nueva-orden', data={
        'client_id': 1,
        'vehicle': 'ABC-123',
        'tech': 'T\xc3\xa9cnico 1',
        'total': 150.00,
        'items': 'Producto A, Producto B'
    })
    assert response.status_code == 302
    assert len(orders) == 3

def test_post_new_invoice(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.post('/nueva-factura', data={
        'order_id': 1,
        'total': 150.00
    })
    assert response.status_code == 302
    assert len(invoices) == 3

def test_post_add_product(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.post('/agregar-producto', data={
        'name': 'Producto C',
        'quantity': 20,
        'price': 25.00
    })
    assert response.status_code == 302
    assert len(inventory) == 4

def test_post_new_appointment(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    response = client.post('/agendar-cita', data={
        'date': '2023-10-10',
        'time': '10:00',
        'client': 'Juan P\xc3\xa9rez',
        'description': 'Revisi\xc3\xb3n'
    })
    assert response.status_code == 302
    assert len(agenda) == 3
