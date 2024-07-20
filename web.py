from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from sqlalchemy import or_

# Инициализация приложения Flask
app = Flask(__name__)

# Настройка подключения к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:3228@localhost/pharmacy_parser'
db = SQLAlchemy(app)

# Определение модели данных для аптек
class Pharmacy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

# Определение модели данных для продуктов
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255))
    name = db.Column(db.String(255), nullable=False)

# Определение модели данных для связи между аптеками и продуктами
class PharmacyProduct(db.Model):
    __tablename__ = 'pharmacyproduct'
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    price = db.Column(db.DECIMAL(10, 2))
    result_url = db.Column(db.String(255))

    pharmacy = db.relationship('Pharmacy', backref='products')
    product = db.relationship('Product', backref='pharmacies')

# Маршрут для главной страницы, отображающий случайные продукты
@app.route('/')
def home():
    products = Product.query.order_by(func.random()).limit(10).all()
    return render_template('index.html', products=products)

# Маршрут для получения подсказок поиска
@app.route('/search_suggestions')
def search_suggestions():
    query = request.args.get('q')
    suggestions = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    return jsonify([{
        'name': product.name, 
        'price': product.pharmacies[0].price, 
        'url': product.pharmacies[0].result_url} 
        for product in suggestions])

# Маршрут для отображения результатов поиска
@app.route('/search_results', methods=['GET'])
def search_results():
    query = request.args.get('q')
    if query:
        # Используем SQLAlchemy для поиска похожих названий
        products = Product.query.filter(or_(Product.name.ilike(f'%{query}%'))).all()
    else:
        products = []
    return render_template('search_results.html', products=products, query=query)

# Маршрут для отображения деталей продукта
@app.route('/product_details', methods=['GET'])
def product_details():
    product_name = request.args.get('product_name')
    product = Product.query.filter(Product.name == product_name).first()
    pharmacies = PharmacyProduct.query.filter(PharmacyProduct.product_id == product.id).all()
    pharmacies_data = [{'pharmacy_name': p.pharmacy.name, 
                        'price': p.price, 'result_url': 
                        p.result_url} 
                        for p in pharmacies]
    return render_template('product_details.html', product=product, pharmacies=pharmacies_data)

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)