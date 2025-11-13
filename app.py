from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change in production

# Mock data
clients = [
    {'id': 1, 'name': 'Juan Pérez', 'email': 'juan@example.com', 'phone': '123-456-7890', 'address': 'Calle 1, Ciudad'},
    {'id': 2, 'name': 'María García', 'email': 'maria@example.com', 'phone': '098-765-4321', 'address': 'Calle 2, Ciudad'},
]

orders = [
    {'id': 1, 'code': 'ORD001', 'client': 'Juan Pérez', 'vehicle': 'ABC-123', 'tech': 'Técnico 1', 'status': 'En Diagnóstico', 'total': 150.00, 'items': ['Producto A', 'Producto B']},
    {'id': 2, 'code': 'ORD002', 'client': 'María García', 'vehicle': 'DEF-456', 'tech': 'Técnico 2', 'status': 'En Progreso', 'total': 200.00, 'items': ['Producto C']},
]

invoices = [
    {'id': 1, 'order_id': 1, 'date': '2023-10-01', 'total': 150.00, 'status': 'Pagada', 'no': 'F001', 'order': 'ORD001', 'client': 'Juan Pérez', 'emit': '2023-10-01', 'due': '2023-10-15', 'subtotal': 125.00, 'vat': 25.00},
    {'id': 2, 'order_id': 2, 'date': '2023-10-02', 'total': 200.00, 'status': 'Pendiente', 'no': 'F002', 'order': 'ORD002', 'client': 'María García', 'emit': '2023-10-02', 'due': '2023-10-16', 'subtotal': 166.67, 'vat': 33.33},
]

inventory = [
    {'id': 1, 'name': 'Producto A', 'quantity': 50, 'price': 10.00, 'code': 'P001', 'category': 'Aceites', 'brand': 'Marca A', 'minmax': '10/100', 'loc': 'Estante 1', 'status': 'Normal'},
    {'id': 2, 'name': 'Producto B', 'quantity': 30, 'price': 20.00, 'code': 'P002', 'category': 'Filtros', 'brand': 'Marca B', 'minmax': '5/50', 'loc': 'Estante 2', 'status': 'Normal'},
    {'id': 3, 'name': 'Producto C', 'quantity': 20, 'price': 25.00, 'code': 'P003', 'category': 'Baterías', 'brand': 'Marca C', 'minmax': '2/20', 'loc': 'Estante 3', 'status': 'Bajo Stock'},
]

agenda = [
    {'id': 1, 'date': '2023-10-05', 'time': '10:00', 'client': 'Juan Pérez', 'description': 'Reunión inicial'},
    {'id': 2, 'date': '2023-10-06', 'time': '14:00', 'client': 'María García', 'description': 'Seguimiento'},
]

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Has cerrado sesión con éxito.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    total_clients = len(clients)
    total_orders = len(orders)
    total_invoices = sum(inv['total'] for inv in invoices)
    pending_orders = len([o for o in orders if o['status'] == 'Pendiente'])
    metrics = {
        'vehicles_today': 5,  # Mock value
        'day_income': 1500.00,  # Mock value
        'pending_approval': pending_orders
    }
    return render_template('dashboard.html', total_clients=total_clients, total_orders=total_orders, total_invoices=total_invoices, pending_orders=pending_orders, metrics=metrics, orders=orders)

@app.route('/clientes')
def clientes():
    if 'user' not in session:
        return redirect(url_for('login'))
    totals = {
        'total': len(clients),
        'active': len([c for c in clients if 'Activo' in str(c)]),  # Mock
        'vehicles': 10  # Mock
    }
    # Add mock fields to clients
    for c in clients:
        c['vehicles'] = 2  # Mock
        c['orders'] = 5  # Mock
        c['last'] = '2023-10-01'  # Mock
        c['state'] = 'Activo'  # Mock
    return render_template('clientes.html', clients=clients, totals=totals)

@app.route('/cliente/<int:id>')
def cliente_detalle(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    client = next((c for c in clients if c['id'] == id), None)
    if not client:
        flash('Cliente no encontrado', 'error')
        return redirect(url_for('clientes'))
    return render_template('cliente_detalle.html', client=client)

@app.route('/ordenes')
def ordenes():
    if 'user' not in session:
        return redirect(url_for('login'))
    totals = {
        'total': len(orders),
        'progress': len([o for o in orders if o['status'] == 'En Progreso']),
        'completed': len([o for o in orders if o['status'] == 'Completada']),
        'pending': len([o for o in orders if o['status'] == 'Pendiente'])
    }
    return render_template('ordenes.html', orders=orders, clients=clients, totals=totals)

@app.route('/orden/<int:id>')
def orden_detalle(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    order = next((o for o in orders if o['id'] == id), None)
    if not order:
        flash('Orden no encontrada', 'error')
        return redirect(url_for('ordenes'))
    client = next((c for c in clients if c['name'] == order['client']), None)
    return render_template('orden_detalle.html', order=order, client=client)

@app.route('/facturacion')
def facturacion():
    if 'user' not in session:
        return redirect(url_for('login'))
    summary = {
        'total': sum(inv['total'] for inv in invoices),
        'paid': len([inv for inv in invoices if inv['status'] == 'Pagada']),
        'due': len([inv for inv in invoices if inv['status'] == 'Pendiente']),
        'overdue': len([inv for inv in invoices if inv['status'] == 'Vencida'])
    }
    invoices_list = [{'id': inv['id'], 'no': inv['no'], 'order': inv['order'], 'client': inv['client'], 'emit': inv['emit'], 'due': inv['due'], 'subtotal': f"${inv['subtotal']:.2f}", 'vat': f"${inv['vat']:.2f}", 'total': f"${inv['total']:.2f}", 'state': inv['status']} for inv in invoices]
    return render_template('facturacion.html', invoices=invoices_list, summary=summary)

@app.route('/factura/<int:id>')
def factura_detalle(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    invoice = next((i for i in invoices if i['id'] == id), None)
    if not invoice:
        flash('Factura no encontrada', 'error')
        return redirect(url_for('facturacion'))
    order = next((o for o in orders if o['id'] == invoice['order_id']), None)
    client = next((c for c in clients if c['name'] == order['client']), None)
    return render_template('factura_detalle.html', invoice=invoice, order=order, client=client)

@app.route('/factura/<int:id>/pdf')
def factura_pdf(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    invoice = next((i for i in invoices if i['id'] == id), None)
    if not invoice:
        flash('Factura no encontrada', 'error')
        return redirect(url_for('facturacion'))
    order = next((o for o in orders if o['id'] == invoice['order_id']), None)
    client = next((c for c in clients if c['name'] == order['client']), None)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Factura", styles['Title']))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Factura ID: {invoice['id']}", styles['Normal']))
    story.append(Paragraph(f"Fecha: {invoice['date']}", styles['Normal']))
    story.append(Paragraph(f"Cliente: {client['name']}", styles['Normal']))
    story.append(Paragraph(f"Total: ${invoice['total']:.2f}", styles['Normal']))
    story.append(Spacer(1, 12))

    data = [['Producto', 'Cantidad', 'Precio']]
    for item in order['items']:
        # Mock quantities and prices
        data.append([item, '1', '$10.00'])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BORDERS', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'factura_{id}.pdf', mimetype='application/pdf')

@app.route('/inventario')
def inventario():
    if 'user' not in session:
        return redirect(url_for('login'))
    totals = {
        'count': len(inventory),
        'value': sum(p['quantity'] * p['price'] for p in inventory),
        'low': len([p for p in inventory if p.get('status') == 'Bajo Stock']),
        'cats': len(set(p['category'] for p in inventory))
    }
    items = [{'code': p['code'], 'product': p['name'], 'category': p['category'], 'brand': p['brand'], 'qty': p['quantity'], 'minmax': p['minmax'], 'price': f"${p['price']:.2f}", 'loc': p['loc'], 'status': p.get('status', 'Normal')} for p in inventory]
    return render_template('inventario.html', items=items, totals=totals)

@app.route('/agenda')
def agenda_view():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Sort agenda by date and time
    sorted_agenda = sorted(agenda, key=lambda x: (x['date'], x['time']))
    return render_template('agenda.html', agenda=sorted_agenda)

@app.route('/nuevo-cliente', methods=['GET', 'POST'])
def nuevo_cliente():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        new_id = max(c['id'] for c in clients) + 1 if clients else 1
        clients.append({'id': new_id, 'name': name, 'email': email, 'phone': phone, 'address': address})
        flash('Cliente agregado exitosamente', 'success')
        return redirect(url_for('clientes'))
    return render_template('form_nuevo_cliente.html')

@app.route('/nueva-orden', methods=['GET', 'POST'])
def nueva_orden():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        client_id = int(request.form['client_id'])
        items = request.form.getlist('items')
        total = float(request.form['total'])
        new_id = max(o['id'] for o in orders) + 1 if orders else 1
        orders.append({'id': new_id, 'client_id': client_id, 'date': datetime.now().strftime('%Y-%m-%d'), 'status': 'Pendiente', 'total': total, 'items': items})
        flash('Orden creada exitosamente', 'success')
        return redirect(url_for('ordenes'))
    return render_template('form_nueva_orden.html', clients=clients)

@app.route('/nueva-factura', methods=['GET', 'POST'])
def nueva_factura():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        order_id = int(request.form['order_id'])
        total = float(request.form['total'])
        new_id = max(i['id'] for i in invoices) + 1 if invoices else 1
        order = next((o for o in orders if o['id'] == order_id), None)
        client = next((c for c in clients if c['name'] == order['client']), None)
        invoices.append({'id': new_id, 'order_id': order_id, 'date': datetime.now().strftime('%Y-%m-%d'), 'total': total, 'status': 'Pendiente', 'no': f'F{new_id:03d}', 'order': order['code'], 'client': client['name'], 'emit': datetime.now().strftime('%Y-%m-%d'), 'due': (datetime.now().replace(day=15)).strftime('%Y-%m-%d'), 'subtotal': total * 0.8333, 'vat': total * 0.1667})
        flash('Factura creada exitosamente', 'success')
        return redirect(url_for('facturacion'))
    return render_template('form_nueva_factura.html', orders=orders)

@app.route('/agregar-producto', methods=['GET', 'POST'])
def agregar_producto():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        new_id = max(p['id'] for p in inventory) + 1 if inventory else 1
        inventory.append({'id': new_id, 'name': name, 'quantity': quantity, 'price': price, 'code': f'P{new_id:03d}', 'category': 'General', 'brand': 'Marca Genérica', 'minmax': '5/50', 'loc': 'Estante Nuevo', 'status': 'Normal'})
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('inventario'))
    return render_template('form_agregar_producto.html')

@app.route('/agendar-cita', methods=['GET', 'POST'])
def nueva_cita():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        client = request.form['client']
        description = request.form['description']
        new_id = max(a['id'] for a in agenda) + 1 if agenda else 1
        agenda.append({'id': new_id, 'date': date, 'time': time, 'client': client, 'description': description})
        flash('Cita agregada exitosamente', 'success')
        return redirect(url_for('agenda_view'))
    return render_template('form_nueva_cita.html')

@app.route('/olvide-contrasena')
def forgot_password_in_progress():
    return render_template('en_construccion.html')

if __name__ == '__main__':
    app.run(debug=True)
