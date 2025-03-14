import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import base64
import sys

sys.path.insert(0, 'libs')

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Mô hình User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), default='default.png')
    avatar_bit = db.Column(db.LargeBinary)  # Thêm cột này để lưu trữ ảnh dạng bit
    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Mô hình Task
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Completed
    created = db.Column(db.DateTime, default=datetime.utcnow)
    finished = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
# Mô hình Category: phân loại công việc   
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Kiểm tra định dạng file hợp lệ
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Đăng ký bộ lọc b64encode
@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

# Hàm chuyển đổi timestamp thành định dạng ngày tháng
def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Đăng ký hàm này như một bộ lọc Jinja2
@app.template_filter('timestamp_to_date')
def register_timestamp_to_date_filter(_):
    return timestamp_to_date

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Tên đăng nhập hoặc mật khẩu không đúng!')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']  # Lấy giá trị xác nhận mật khẩu

        # Kiểm tra xác nhận mật khẩu
        if password != confirm_password:
            flash("Mật khẩu và xác nhận mật khẩu không khớp!")
            return redirect(url_for('register'))

        # Kiểm tra tên đăng nhập đã tồn tại chưa
        if User.query.filter_by(username=username).first():
            flash("Tên đăng nhập đã tồn tại!")
            return redirect(url_for('register'))
        
        # Mặc định avatar
        avatar_file = 'default.png'
        
        # Kiểm tra nếu có file avatar được tải lên
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                avatar_file = filename
        
        new_user = User(username=username, avatar=f"uploads/{avatar_file}")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Đăng ký thành công! Vui lòng đăng nhập.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'avatar_bit' in request.files:
            file = request.files['avatar_bit']
            if file and file.filename != '' and allowed_file(file.filename):
                # Đọc file ảnh và chuyển đổi thành dạng bit
                avatar_bit = file.read()
                current_user.avatar_bit = avatar_bit
                db.session.commit()
                flash("Ảnh đại diện đã được cập nhật dưới dạng bit!")
                
        return redirect(url_for('profile'))
    return render_template('profile.html')

@app.route('/dashboard')
@login_required 
def dashboard():
    category_id = request.args.get('category_id', type=int)
    
    # Lấy danh sách công việc trễ hạn
    overdue_tasks = Task.query.filter(
        Task.finished == None, 
        Task.created < datetime.utcnow(), 
        Task.user_id == current_user.id
    ).count()
    
    # Lọc công việc theo danh mục nếu có
    if category_id:
        tasks = Task.query.filter_by(user_id=current_user.id, category_id=category_id).all()
        selected_category = category_id
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        selected_category = None
    
    # Lấy tất cả danh mục để hiển thị trong filter
    categories = Category.query.all()
    
    return render_template(
        'dashboard.html', 
        tasks=tasks, 
        overdue_tasks=overdue_tasks, 
        categories=categories,
        selected_category=selected_category
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Route cho Category
@app.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        # Kiểm tra xem danh mục đã tồn tại chưa
        if Category.query.filter_by(name=name).first():
            flash("Danh mục này đã tồn tại!")
            return redirect(url_for('add_category'))
            
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash("Đã thêm danh mục thành công!")
        return redirect(url_for('categories'))
    return render_template('add_category.html')

@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form['name']
        # Kiểm tra xem danh mục mới đã tồn tại chưa
        existing = Category.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash("Danh mục này đã tồn tại!")
            return redirect(url_for('edit_category', id=id))
            
        category.name = name
        db.session.commit()
        flash("Đã cập nhật danh mục thành công!")
        return redirect(url_for('categories'))
    return render_template('edit_category.html', category=category)

@app.route('/delete_category/<int:id>')
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Cập nhật các task sử dụng danh mục này
    Task.query.filter_by(category_id=id).update({Task.category_id: None})
    
    db.session.delete(category)
    db.session.commit()
    flash("Đã xóa danh mục thành công!")
    return redirect(url_for('categories'))

# Route cho Task
@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        category_id = request.form.get('category_id')
        
        # Nếu không chọn danh mục, category_id sẽ là None
        if category_id:
            category_id = int(category_id)
        else:
            category_id = None
            
        new_task = Task(
            title=title,
            user_id=current_user.id,
            category_id=category_id
        )
        db.session.add(new_task)
        db.session.commit()
        flash("Đã thêm công việc thành công!")
        return redirect(url_for('dashboard'))
        
    categories = Category.query.all()
    return render_template('add_task.html', categories=categories)

@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    
    # Kiểm tra xem công việc có thuộc về người dùng hiện tại không
    if task.user_id != current_user.id:
        flash("Bạn không có quyền chỉnh sửa công việc này!")
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        task.title = request.form['title']
        category_id = request.form.get('category_id')
        
        # Nếu không chọn danh mục, category_id sẽ là None
        if category_id:
            task.category_id = int(category_id)
        else:
            task.category_id = None
            
        db.session.commit()
        flash("Đã cập nhật công việc thành công!")
        return redirect(url_for('dashboard'))
        
    categories = Category.query.all()
    return render_template('edit_task.html', task=task, categories=categories)

@app.route('/delete_task/<int:id>')
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    
    # Kiểm tra xem công việc có thuộc về người dùng hiện tại không
    if task.user_id != current_user.id:
        flash("Bạn không có quyền xóa công việc này!")
        return redirect(url_for('dashboard'))
        
    db.session.delete(task)
    db.session.commit()
    flash("Đã xóa công việc thành công!")
    return redirect(url_for('dashboard'))

@app.route('/complete_task/<int:id>')
@login_required
def complete_task(id):
    task = Task.query.get_or_404(id)
    
    # Kiểm tra xem công việc có thuộc về người dùng hiện tại không
    if task.user_id != current_user.id:
        flash("Bạn không có quyền cập nhật công việc này!")
        return redirect(url_for('dashboard'))
        
    task.status = 'Completed'
    task.finished = datetime.utcnow()
    db.session.commit()
    flash("Đã đánh dấu công việc hoàn thành!")
    return redirect(url_for('dashboard'))

# Tạo database nếu chưa có
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)