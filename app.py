import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
database_url = os.getenv('DATABASE_URL', 'sqlite:///users.db')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
if database_url and 'postgresql' in database_url and 'sslmode' not in database_url:
    database_url += '?sslmode=require'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'avi', 'mov', 'mkv'}
MEDIA_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_media(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in MEDIA_EXTENSIONS

db = SQLAlchemy(app)

# Custom Jinja2 filter for parsing JSON
@app.template_filter('from_json')
def from_json(value):
    try:
        return json.loads(value or '[]')
    except (json.JSONDecodeError, TypeError):
        return []

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    published = db.Column(db.Boolean, default=False)
    
    modules = db.relationship('Module', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.title}>'

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    
    lessons = db.relationship('Lesson', backref='module', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Module {self.title}>'

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Lesson {self.title}>'

class LandingPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    header_title = db.Column(db.String(200), nullable=False)
    header_subtitle = db.Column(db.Text)
    header_background_image = db.Column(db.String(255))
    header_call_to_action = db.Column(db.Text)
    target_audience = db.Column(db.Text)  # JSON string for target audience cards
    audience_section_title = db.Column(db.String(200), default='Who is this course for?')
    timeline = db.Column(db.Text)  # JSON string for timeline steps
    timeline_section_title = db.Column(db.String(200), default='How does the course work?')
    course_program = db.Column(db.Text)  # JSON string for course program modules
    course_program_section_title = db.Column(db.String(200), default='Course Program')
    faq = db.Column(db.Text)  # JSON string for FAQ items
    faq_section_title = db.Column(db.String(200), default='Frequently Asked Questions')
    topics = db.Column(db.Text)  # JSON string for topics with subitems
    topics_section_title = db.Column(db.String(200), default='Course Topics')
    topics_section_description = db.Column(db.Text)
    cta_title = db.Column(db.String(200))
    cta_text = db.Column(db.Text)
    cta_image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    course = db.relationship('Course', backref=db.backref('landing_page', uselist=False))
    
    def __repr__(self):
        return f'<LandingPage {self.header_title}>'

class AuthorBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200))  # e.g. "Python Expert"
    bio = db.Column(db.Text)
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AuthorBlock {self.name}>'

class ThemeSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primary_color = db.Column(db.String(7), default='#007bff')  # e.g. #007bff
    secondary_color = db.Column(db.String(7), default='#0056b3')  # darker shade
    text_color = db.Column(db.String(7), default='#333333')
    bg_color = db.Column(db.String(7), default='#f8f9fa')
    heading_color = db.Column(db.String(7), default='#333333')
    accent_color = db.Column(db.String(7), default='#ffc107')  # price/highlights
    button_color = db.Column(db.String(7), default='#007bff')
    button_text_color = db.Column(db.String(7), default='#ffffff')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ThemeSettings {self.primary_color}>'

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(200), default='Online Courses')
    site_description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SiteSettings {self.site_name}>'

class HomePage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    header_title = db.Column(db.String(200), nullable=False)
    header_subtitle = db.Column(db.Text)
    header_background_image = db.Column(db.String(255))
    header_call_to_action = db.Column(db.Text)
    features = db.Column(db.Text)  # JSON string for feature cards
    features_section_title = db.Column(db.String(200), default='Our Advantages')
    stats = db.Column(db.Text)  # JSON string for statistics
    stats_section_title = db.Column(db.String(200), default='Numbers and Facts')
    about_text = db.Column(db.Text)  # JSON string for about section
    about_section_title = db.Column(db.String(200), default='About Our School')
    faq = db.Column(db.Text)  # JSON string for FAQ items
    faq_section_title = db.Column(db.String(200), default='Frequently Asked Questions')
    cta_title = db.Column(db.String(200))
    cta_text = db.Column(db.Text)
    cta_image = db.Column(db.String(255))
    chatbot_cta_text = db.Column(db.Text)
    chatbot_button_text = db.Column(db.String(200), default='Chat Bot')
    chatbot_button_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<HomePage {self.header_title}>'

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    media_path = db.Column(db.String(500))
    media_type = db.Column(db.String(10))
    disable_link_preview = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship for child articles
    children = db.relationship('Article', backref=db.backref('parent', remote_side=[id]))

    @property
    def is_root(self):
        return self.parent_id is None

    def __repr__(self):
        return f'<Article {self.title}>'

class BotUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(200))
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BotUser {self.telegram_id}>'

class BotSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_token = db.Column(db.String(500))
    webhook_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<BotSettings active={self.is_active}>'

def create_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: username=admin, password=admin123")

@app.context_processor
def inject_site():
    site = SiteSettings.query.first()
    return {'site_name': site.site_name if site else 'Online Courses', 'site_description': site.site_description if site else ''}

@app.route('/')
def index():
    # Check for active home landing page
    home_landing = HomePage.query.filter_by(is_active=True).first()
    if home_landing:
        theme = ThemeSettings.query.first()
        courses = Course.query.filter_by(published=True, is_active=True).limit(3).all()
        return render_template('home_landing.html', home_landing=home_landing, theme=theme, courses=courses)

    # If no home landing, redirect logged-in users to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/test-page-header')
def test_page_header():
    return render_template('test_page_header.html')

@app.route('/admin/toggle_user/<int:user_id>')
def toggle_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.id != session['user_id']:
        user.is_active = not user.is_active
        db.session.commit()
        flash(f'User {user.username} {"activated" if user.is_active else "deactivated"}')
    else:
        flash('You cannot deactivate yourself')
    
    return redirect(url_for('admin'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if not user.check_password(current_password):
            flash('Current password is incorrect')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('change_password'))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters')
            return redirect(url_for('change_password'))
        
        user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully!')
        return redirect(url_for('dashboard'))
    
    breadcrumbs = [
        {'title': 'Dashboard', 'url': url_for('dashboard')},
        {'title': 'Change Password', 'url': None}
    ]
    return render_template('change_password.html', user=user, breadcrumbs=breadcrumbs)

# Course Management Routes
@app.route('/admin/courses')
def admin_courses():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    courses = Course.query.all()
    return render_template('admin_courses.html', courses=courses)

@app.route('/admin/courses/create', methods=['GET', 'POST'])
def create_course():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form.get('price')
        published = 'published' in request.form
        
        if not title:
            flash('Course name is required')
            return redirect(url_for('create_course'))
        
        # Convert price to float or None
        course_price = None
        if price and price.strip():
            try:
                course_price = float(price)
                if course_price < 0:
                    flash('Price cannot be negative')
                    return redirect(url_for('create_course'))
            except ValueError:
                flash('Invalid price value')
                return redirect(url_for('create_course'))
        
        course = Course(title=title, description=description, price=course_price, published=published)
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create upload directory if it doesn't exist
                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                file.save(os.path.join(upload_dir, filename))
                course.image = filename
        
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!')
        return redirect(url_for('admin_courses'))
    
    return render_template('create_course.html')

@app.route('/admin/courses/<int:course_id>/edit', methods=['GET', 'POST'])
def edit_course(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form.get('price')
        published = 'published' in request.form
        
        if not title:
            flash('Course name is required')
            return redirect(url_for('edit_course', course_id=course_id))
        
        # Convert price to float or None
        course_price = None
        if price and price.strip():
            try:
                course_price = float(price)
                if course_price < 0:
                    flash('Price cannot be negative')
                    return redirect(url_for('edit_course', course_id=course_id))
            except ValueError:
                flash('Invalid price value')
                return redirect(url_for('edit_course', course_id=course_id))
        
        course.title = title
        course.description = description
        course.price = course_price
        course.published = published
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                file.save(os.path.join(upload_dir, filename))
                course.image = filename
        
        db.session.commit()
        flash('Course updated successfully!')
        return redirect(url_for('admin_modules', course_id=course_id))
    
    return render_template('edit_course.html', course=course)

@app.route('/admin/courses/<int:course_id>/delete', methods=['POST'])
def delete_course(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    if course.landing_page:
        db.session.delete(course.landing_page)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!')
    return redirect(url_for('admin_courses'))

@app.route('/admin/courses/<int:course_id>/toggle_published', methods=['POST'])
def toggle_published(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    course.published = not course.published
    db.session.commit()
    
    status = "published" if course.published else "unpublished"
    flash(f'Course "{course.title}" {status}!')
    return redirect(request.referrer or url_for('admin_modules', course_id=course_id))

@app.route('/admin/courses/<int:course_id>/modules')
def admin_modules(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    return render_template('admin_modules.html', course=course, modules=course.modules)

@app.route('/admin/modules/create', methods=['GET', 'POST'])
def create_module():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        course_id = request.form['course_id']
        
        if not title or not course_id:
            flash('Module name and course are required')
            return redirect(url_for('admin_modules', course_id=course_id))
        
        module = Module(title=title, course_id=course_id)
        db.session.add(module)
        db.session.commit()
        flash('Module created successfully!')
        return redirect(url_for('admin_modules', course_id=course_id))
    
    # Redirect to admin_courses if accessed via GET
    return redirect(url_for('admin_courses'))

@app.route('/admin/modules/<int:module_id>/edit', methods=['GET', 'POST'])
def edit_module(module_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    module = Module.query.get_or_404(module_id)
    
    if request.method == 'POST':
        title = request.form['title']
        
        if not title:
            flash('Module name is required')
            return redirect(url_for('edit_module', module_id=module_id))
        
        module.title = title
        db.session.commit()
        flash('Module updated successfully!')
        return redirect(url_for('admin_modules', course_id=module.course_id))
    
    return render_template('edit_module.html', module=module)

@app.route('/admin/modules/<int:module_id>/delete', methods=['POST'])
def delete_module(module_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    module = Module.query.get_or_404(module_id)
    course_id = module.course_id
    db.session.delete(module)
    db.session.commit()
    flash('Module deleted successfully!')
    return redirect(url_for('admin_modules', course_id=course_id))

@app.route('/admin/lessons/create', methods=['GET', 'POST'])
def create_lesson():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        module_id = request.form['module_id']
        
        if not title or not content or not module_id:
            flash('Title, content and module are required')
            return redirect(url_for('create_lesson'))
        
        lesson = Lesson(title=title, content=content, module_id=module_id)
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson created successfully!')
        
        module = Module.query.get(module_id)
        return redirect(url_for('admin_modules', course_id=module.course_id))
    
    modules = Module.query.all()
    selected_module_id = request.args.get('module_id')
    selected_course_id = None
    course_title = None
    breadcrumbs = [
        {'title': 'Dashboard', 'url': url_for('dashboard')},
        {'title': 'Admin Panel', 'url': url_for('admin')},
        {'title': 'Courses', 'url': url_for('admin_courses')}
    ]
    if selected_module_id:
        selected_module = Module.query.get(selected_module_id)
        if selected_module:
            selected_course_id = selected_module.course_id
            course_title = selected_module.course.title
            breadcrumbs.append({'title': course_title, 'url': url_for('admin_modules', course_id=selected_course_id)})
    breadcrumbs.append({'title': 'Create Lesson', 'url': None})
    return render_template('create_lesson.html', modules=modules, selected_module_id=selected_module_id, selected_course_id=selected_course_id, breadcrumbs=breadcrumbs)

@app.route('/admin/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
def edit_lesson(lesson_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title or not content:
            flash('Title and content are required')
            return redirect(url_for('edit_lesson', lesson_id=lesson_id))
        
        lesson.title = title
        lesson.content = content
        db.session.commit()
        flash('Lesson updated successfully!')
        
        return redirect(url_for('admin_modules', course_id=lesson.module.course_id))
    
    breadcrumbs = [
        {'title': 'Dashboard', 'url': url_for('dashboard')},
        {'title': 'Admin Panel', 'url': url_for('admin')},
        {'title': 'Courses', 'url': url_for('admin_courses')},
        {'title': lesson.module.course.title, 'url': url_for('admin_modules', course_id=lesson.module.course_id)},
        {'title': 'Edit Lesson', 'url': None}
    ]
    return render_template('edit_lesson.html', lesson=lesson, breadcrumbs=breadcrumbs)

@app.route('/admin/lessons/<int:lesson_id>/delete', methods=['POST'])
def delete_lesson(lesson_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.module.course_id
    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted successfully!')
    return redirect(url_for('admin_modules', course_id=course_id))

@app.route('/upload-image', methods=['POST'])
def upload_image():
    print(f"Session data: {session}")
    print(f"User ID in session: {'user_id' in session}")
    print(f"Role in session: {session.get('role')}")
    
    if 'user_id' not in session or session.get('role') != 'admin':
        print("Access denied - user not admin or not logged in")
        return jsonify({'error': 'Access denied'}), 403
    
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Add timestamp to filename to avoid conflicts
        import time
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(time.time())}{ext}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file.save(os.path.join(upload_dir, filename))
        
        # Return the URL of the uploaded image
        image_url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({'url': image_url})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload-video', methods=['POST'])
def upload_video():
    print(f"Session data: {session}")
    print(f"User ID in session: {'user_id' in session}")
    print(f"Role in session: {session.get('role')}")
    
    if 'user_id' not in session or session.get('role') != 'admin':
        print("Access denied - user not admin or not logged in")
        return jsonify({'error': 'Access denied'}), 403
    
    if 'video' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file is a video
    allowed_video_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
    def allowed_video(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_video_extensions
    
    if file and allowed_video(file.filename):
        filename = secure_filename(file.filename)
        
        # Add timestamp to filename to avoid conflicts
        import time
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(time.time())}{ext}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file.save(os.path.join(upload_dir, filename))
        
        # Return the URL of the uploaded video
        video_url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({'url': video_url})
    
    return jsonify({'error': 'Invalid file type. Only video files are allowed.'}), 400

@app.route('/courses')
def courses():
    courses = Course.query.filter_by(published=True, is_active=True).all()
    return render_template('courses.html', courses=courses)

@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    # Get published course with modules and lessons
    course = Course.query.filter_by(id=course_id, published=True, is_active=True).first_or_404()
    
    # Check for active landing page
    landing_page = LandingPage.query.filter_by(course_id=course_id, is_active=True).first()
    if landing_page:
        author_block = AuthorBlock.query.filter_by(is_active=True).first()
        theme = ThemeSettings.query.first()
        return render_template('landing.html', course=course, landing_page=landing_page, author_block=author_block, theme=theme)
    
    return render_template('course_detail.html', course=course)

@app.route('/courses/<int:course_id>/content')
def course_content(course_id):
    # Get published course with modules and lessons
    course = Course.query.filter_by(id=course_id, published=True, is_active=True).first_or_404()
    breadcrumbs = [
        {'title': 'Dashboard', 'url': url_for('dashboard')},
        {'title': 'Courses', 'url': url_for('courses')},
        {'title': course.title, 'url': None}
    ]
    return render_template('course_detail.html', course=course, breadcrumbs=breadcrumbs)

@app.route('/courses/<int:course_id>/lessons/<int:lesson_id>')
def lesson_detail(course_id, lesson_id):
    course = Course.query.filter_by(id=course_id, published=True, is_active=True).first_or_404()
    lesson = Lesson.query.filter_by(id=lesson_id).first_or_404()

    if lesson.module.course_id != course.id:
        flash('Lesson not found')
        return redirect(url_for('courses'))

    next_lesson_data = None
    modules = Module.query.filter_by(course_id=course.id).order_by(Module.order).all()
    for i, mod in enumerate(modules):
        mod_lessons = Lesson.query.filter_by(module_id=mod.id).order_by(Lesson.order).all()
        for j, l in enumerate(mod_lessons):
            if l.id == lesson.id:
                if j + 1 < len(mod_lessons):
                    next_lesson_data = {
                        'lesson': mod_lessons[j + 1],
                        'course': course,
                        'module': mod
                    }
                elif i + 1 < len(modules):
                    next_mod = modules[i + 1]
                    next_mod_lessons = Lesson.query.filter_by(module_id=next_mod.id).order_by(Lesson.order).all()
                    if next_mod_lessons:
                        next_lesson_data = {
                            'lesson': next_mod_lessons[0],
                            'course': course,
                            'module': next_mod
                        }
                else:
                    next_course = Course.query.filter(
                        Course.id > course.id,
                        Course.published == True,
                        Course.is_active == True
                    ).order_by(Course.id).first()
                    if next_course:
                        next_mod = Module.query.filter_by(course_id=next_course.id).order_by(Module.order).first()
                        if next_mod:
                            next_lesson = Lesson.query.filter_by(module_id=next_mod.id).order_by(Lesson.order).first()
                            if next_lesson:
                                next_lesson_data = {
                                    'lesson': next_lesson,
                                    'course': next_course,
                                    'module': next_mod
                                }
                break

    breadcrumbs = [
        {'title': 'Dashboard', 'url': url_for('dashboard')},
        {'title': 'Courses', 'url': url_for('courses')},
        {'title': course.title, 'url': url_for('course_content', course_id=course.id)},
        {'title': lesson.title, 'url': None}
    ]
    return render_template('lesson_detail.html', course=course, lesson=lesson,
                           next_lesson_data=next_lesson_data, breadcrumbs=breadcrumbs)

# Landing page routes
@app.route('/admin/courses/<int:course_id>/landing')
def edit_landing(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    landing_page = LandingPage.query.filter_by(course_id=course_id).first()
    
    return render_template('edit_landing.html', course=course, landing_page=landing_page)

@app.route('/admin/courses/<int:course_id>/landing', methods=['POST'])
def save_landing(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    landing_page = LandingPage.query.filter_by(course_id=course_id).first()
    
    if not landing_page:
        landing_page = LandingPage(course_id=course_id)
        
    # Update fields (default to '' so None never appears in templates)
    landing_page.header_title = request.form.get('header_title', course.title) or course.title
    landing_page.header_subtitle = request.form.get('header_subtitle') or ''
    landing_page.header_call_to_action = request.form.get('header_call_to_action') or ''
    landing_page.target_audience = request.form.get('target_audience') or '[]'
    landing_page.audience_section_title = request.form.get('audience_section_title') or 'Who is this course for?'
    landing_page.timeline = request.form.get('timeline') or '[]'
    landing_page.timeline_section_title = request.form.get('timeline_section_title') or 'How does the course work?'
    landing_page.course_program = request.form.get('course_program') or '[]'
    landing_page.course_program_section_title = request.form.get('course_program_section_title') or 'Course Program'
    landing_page.faq = request.form.get('faq') or '[]'
    landing_page.faq_section_title = request.form.get('faq_section_title') or 'Frequently Asked Questions'
    landing_page.topics = request.form.get('topics') or '[]'
    landing_page.topics_section_title = request.form.get('topics_section_title') or 'Course Topics'
    landing_page.topics_section_description = request.form.get('topics_section_description') or ''
    landing_page.cta_title = request.form.get('cta_title') or ''
    landing_page.cta_text = request.form.get('cta_text') or ''
    landing_page.is_active = 'is_active' in request.form
    
    # Handle background image upload
    if 'header_background_image' in request.files and request.files['header_background_image'].filename:
        file = request.files['header_background_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            import time
            name, ext = os.path.splitext(filename)
            filename = f"landing_{course_id}_{int(time.time())}{ext}"
            
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file.save(os.path.join(upload_dir, filename))
            landing_page.header_background_image = filename
    
    # Handle CTA image upload
    if 'cta_image' in request.files:
        file = request.files['cta_image']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            import time
            name, ext = os.path.splitext(filename)
            filename = f"cta_{course_id}_{int(time.time())}{ext}"
            
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            landing_page.cta_image = filename
            print(f"CTA image saved to: {filepath}', size: {os.path.getsize(filepath)}")
    
    db.session.add(landing_page)
    db.session.commit()
    
    flash('Landing page saved successfully!')
    return redirect(url_for('edit_landing', course_id=course_id))

@app.route('/courses/<int:course_id>/landing-header')
def view_landing(course_id):
    course = Course.query.filter_by(id=course_id, published=True, is_active=True).first_or_404()
    landing_page = LandingPage.query.filter_by(course_id=course_id, is_active=True).first()
    author_block = AuthorBlock.query.filter_by(is_active=True).first()
    theme = ThemeSettings.query.first()
    
    if not landing_page:
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('landing.html', course=course, landing_page=landing_page, author_block=author_block, theme=theme)

@app.route('/admin/courses/<int:course_id>/landing-header/preview')
def preview_landing(course_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    landing_page = LandingPage.query.filter_by(course_id=course_id).first()
    
    if not landing_page:
        # Create dummy landing page for preview
        landing_page = LandingPage(
            course_id=course_id,
            header_title=course.title,
            header_subtitle="Landing Page Preview",
            header_call_to_action="This is a preview",
            audience_section_title="Кому подойдёт этот курс?",
            timeline_section_title="Как проходит курс?",
            course_program_section_title="Программа курса",
            faq_section_title="Часто задаваемые вопросы",
            topics_section_title="Темы курса",
            is_active=False
        )
    
    author_block = AuthorBlock.query.filter_by(is_active=True).first()
    theme = ThemeSettings.query.first()
    
    return render_template('landing.html', course=course, landing_page=landing_page, author_block=author_block, theme=theme)

@app.route('/admin/author', methods=['GET', 'POST'])
def edit_author():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    author = AuthorBlock.query.filter_by(is_active=True).first()
    
    if request.method == 'POST':
        if not author:
            author = AuthorBlock(is_active=True)
        
        author.name = request.form.get('name', '')
        author.title = request.form.get('title')
        author.bio = request.form.get('bio')
        
        if 'author_image' in request.files:
            file = request.files['author_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                name, ext = os.path.splitext(filename)
                filename = f"author_{int(time.time())}{ext}"
                
                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                author.image = filename
        
        db.session.add(author)
        db.session.commit()
        flash('Author information saved!')
        return redirect(url_for('edit_author'))
    
    return render_template('edit_author.html', author=author)

@app.route('/admin/theme', methods=['GET', 'POST'])
def edit_theme():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    theme = ThemeSettings.query.first()
    if not theme:
        theme = ThemeSettings()
    
    if request.method == 'POST':
        theme.primary_color = request.form.get('primary_color', '#007bff')
        theme.secondary_color = request.form.get('secondary_color', '#0056b3')
        theme.text_color = request.form.get('text_color', '#333333')
        theme.bg_color = request.form.get('bg_color', '#f8f9fa')
        theme.heading_color = request.form.get('heading_color', '#333333')
        theme.accent_color = request.form.get('accent_color', '#ffc107')
        theme.button_color = request.form.get('button_color', '#007bff')
        theme.button_text_color = request.form.get('button_text_color', '#ffffff')
        
        db.session.add(theme)
        db.session.commit()
        flash('Color scheme saved!')
        return redirect(url_for('edit_theme'))
    
    return render_template('edit_theme.html', theme=theme)

@app.route('/admin/site', methods=['GET', 'POST'])
def edit_site():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))

    site = SiteSettings.query.first()
    if not site:
        site = SiteSettings()

    if request.method == 'POST':
        site.site_name = request.form.get('site_name', 'Online Courses')
        site.site_description = request.form.get('site_description')

        db.session.add(site)
        db.session.commit()
        flash('Site settings saved!')
        return redirect(url_for('edit_site'))

    return render_template('edit_site.html', site=site)

# Home Page Landing routes
@app.route('/admin/home-landing', methods=['GET', 'POST'])
def edit_home_landing():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))

    home_landing = HomePage.query.first()

    if request.method == 'POST':
        if not home_landing:
            home_landing = HomePage()

        home_landing.header_title = request.form.get('header_title') or 'Welcome'
        home_landing.header_subtitle = request.form.get('header_subtitle') or ''
        home_landing.header_call_to_action = request.form.get('header_call_to_action') or ''
        home_landing.features = request.form.get('features') or '[]'
        home_landing.features_section_title = request.form.get('features_section_title') or 'Our Advantages'
        home_landing.stats = request.form.get('stats') or '[]'
        home_landing.stats_section_title = request.form.get('stats_section_title') or 'Numbers and Facts'
        home_landing.about_text = request.form.get('about_text') or '[]'
        home_landing.about_section_title = request.form.get('about_section_title') or 'About Our School'
        home_landing.faq = request.form.get('faq') or '[]'
        home_landing.faq_section_title = request.form.get('faq_section_title') or 'Frequently Asked Questions'
        home_landing.cta_title = request.form.get('cta_title') or ''
        home_landing.cta_text = request.form.get('cta_text') or ''
        home_landing.chatbot_cta_text = request.form.get('chatbot_cta_text') or ''
        home_landing.chatbot_button_text = request.form.get('chatbot_button_text') or 'Chat Bot'
        home_landing.chatbot_button_url = request.form.get('chatbot_button_url') or ''
        home_landing.is_active = 'is_active' in request.form

        # Handle background image upload
        if 'header_background_image' in request.files and request.files['header_background_image'].filename:
            file = request.files['header_background_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                name, ext = os.path.splitext(filename)
                filename = f"home_header_{int(time.time())}{ext}"

                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                file.save(os.path.join(upload_dir, filename))
                home_landing.header_background_image = filename

        # Handle CTA image upload
        if 'cta_image' in request.files:
            file = request.files['cta_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                name, ext = os.path.splitext(filename)
                filename = f"home_cta_{int(time.time())}{ext}"

                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                home_landing.cta_image = filename

        db.session.add(home_landing)
        db.session.commit()
        flash('Home page saved!')
        return redirect(url_for('edit_home_landing'))

    return render_template('edit_home_landing.html', home_landing=home_landing)

@app.route('/admin/bot-mailings', methods=['GET', 'POST'])
def edit_bot_mailings():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        mailing_text = request.form.get('mailing_text', '').strip()
        disable_link_preview = 'disable_link_preview' in request.form

        if not mailing_text:
            flash('Enter mailing text')
            return redirect(url_for('edit_bot_mailings'))

        settings = BotSettings.query.first()
        if not settings or not settings.bot_token or not settings.is_active:
            flash('Bot is not configured or is disabled')
            return redirect(url_for('edit_bot_mailings'))

        import asyncio
        import os
        import time
        from telegram import Bot, InputFile, LinkPreviewOptions
        from telegram.request import HTTPXRequest

        # Save uploaded file (media)
        media_path = None
        media_type = None  # 'photo' or 'video'
        timestamp = str(int(time.time()))

        if 'mailing_media' in request.files:
            media_file = request.files['mailing_media']
            if media_file and media_file.filename:
                filename = media_file.filename.lower()
                if filename.endswith(('.jpg, '.jpeg, '.png, '.gif, '.webp')):
                    media_type = 'photo'
                elif filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    media_type = 'video'
                if media_type:
                    media_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], 'mailing_' + timestamp + '_' + media_file.filename))
                    os.makedirs(os.path.dirname(media_path), exist_ok=True)
                    media_file.save(media_path)

        async def send_mailing():
            request = HTTPXRequest(connect_timeout=120, read_timeout=120, write_timeout=120)
            bot = Bot(token=settings.bot_token, request=request)
            users = BotUser.query.filter_by(is_active=True).all()
            sent = 0
            failed = 0

            for user in users:
                try:
                    if media_path and os.path.exists(media_path):
                        with open(media_path, 'rb') as f:
                            if media_type == 'photo':
                                await bot.send_photo(
                                    chat_id=user.telegram_id,
                                    photo=f,
                                    caption=mailing_text if mailing_text else None,
                                    parse_mode='HTML' if mailing_text else None
                                )
                            else:  # video
                                await bot.send_video(
                                    chat_id=user.telegram_id,
                                    video=f,
                                    caption=mailing_text if mailing_text else None,
                                    parse_mode='HTML' if mailing_text else None
                                )
                    else:
                        if mailing_text:
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=mailing_text,
                                parse_mode='HTML',
                                link_preview_options=LinkPreviewOptions(is_disabled=disable_link_preview)
                            )
                    sent += 1
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to send to {user.telegram_id}: {e}")
                    failed += 1

            # Clean up file
            if media_path and os.path.exists(media_path):
                os.remove(media_path)

            return sent, failed

        try:
            sent, failed = asyncio.run(send_mailing())
            flash(f'Mailing completed! Sent: {sent}, errors: {failed}')
        except Exception as e:
            flash(f'Mailing error: {str(e)}')

        return redirect(url_for('edit_bot_mailings'))

    users_count = BotUser.query.filter_by(is_active=True).count()
    breadcrumbs = [
        {'title': 'Dashboard', 'url': url_for('dashboard')},
        {'title': 'Admin Panel', 'url': url_for('admin')},
        {'title': 'Mailing', 'url': None}
    ]
    return render_template('edit_bot_mailings.html', users_count=users_count, breadcrumbs=breadcrumbs)

@app.route('/admin/articles')
def admin_articles():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))

    # Get root articles
    root_articles = Article.query.filter_by(parent_id=None, is_active=True).order_by(Article.order).all()
    return render_template('admin_articles.html', root_articles=root_articles)

@app.route('/admin/articles/create', methods=['GET', 'POST'])
def create_article():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form.get('content', '')
        parent_id = request.form.get('parent_id')
        disable_link_preview = 'disable_link_preview' in request.form

        if not title:
            flash('Article title is required')
            return redirect(url_for('create_article'))

        article = Article(
            title=title,
            content=content,
            parent_id=int(parent_id) if parent_id else None,
            disable_link_preview=disable_link_preview
        )

        db.session.add(article)
        db.session.flush()  # Flush to get the article ID

        # Handle media upload (image/video for bot display)
        if 'article_media' in request.files:
            media_file = request.files['article_media']
            if media_file and media_file.filename and allowed_media(media_file.filename):
                filename = secure_filename(media_file.filename)
                import time
                name, ext = os.path.splitext(filename)
                ext = ext.lower().lstrip('.')
                filename = f"article_media_{int(time.time())}_{name}.{ext}"

                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                file_path = os.path.join(upload_dir, filename)
                media_file.save(file_path)

                article.media_path = f"uploads/{filename}"
                article.media_type = 'photo' if ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'} else 'video'

        # Handle file attachments
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    name, ext = os.path.splitext(filename)
                    filename = f"article_{int(time.time())}_{name}{ext}"

                    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
                    if not os.path.exists(upload_dir):
                        os.makedirs(upload_dir)

                    file.save(os.path.join(upload_dir, filename))

        db.session.commit()
        flash('Article created!')
        return redirect(url_for('admin_articles'))

    # Get parent articles for dropdown (only root articles; children render via recursion)
    parent_articles = Article.query.filter_by(parent_id=None, is_active=True).order_by(Article.order).all()
    return render_template('create_article.html', parent_articles=parent_articles)

@app.route('/admin/articles/<int:article_id>/edit', methods=['GET', 'POST'])
def edit_article(article_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))

    article = Article.query.get_or_404(article_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form.get('content', '')
        parent_id = request.form.get('parent_id')
        disable_link_preview = 'disable_link_preview' in request.form

        if not title:
            flash('Article title is required')
            return redirect(url_for('edit_article', article_id=article_id))

        article.title = title
        article.content = content
        article.parent_id = int(parent_id) if parent_id else None
        article.disable_link_preview = disable_link_preview

        # Handle media upload (image/video for bot display)
        if 'article_media' in request.files:
            media_file = request.files['article_media']
            if media_file and media_file.filename and allowed_media(media_file.filename):
                # Delete old media if exists
                if article.media_path:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(article.media_path))
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = secure_filename(media_file.filename)
                import time
                name, ext = os.path.splitext(filename)
                ext = ext.lower().lstrip('.')
                filename = f"article_media_{int(time.time())}_{name}.{ext}"

                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                file_path = os.path.join(upload_dir, filename)
                media_file.save(file_path)

                article.media_path = f"uploads/{filename}"
                article.media_type = 'photo' if ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'} else 'video'

        # Handle new file attachments
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    name, ext = os.path.splitext(filename)
                    filename = f"article_{int(time.time())}_{name}{ext}"

                    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
                    if not os.path.exists(upload_dir):
                        os.makedirs(upload_dir)

                    file.save(os.path.join(upload_dir, filename))

        db.session.commit()
        flash('Article updated!')
        return redirect(url_for('admin_articles'))

    def get_descendant_ids(article_id):
        ids = set()
        children = Article.query.filter_by(parent_id=article_id).all()
        for child in children:
            ids.add(child.id)
            ids.update(get_descendant_ids(child.id))
        return ids

    disabled_ids = {article_id}
    disabled_ids.update(get_descendant_ids(article_id))
    parent_articles = Article.query.filter_by(parent_id=None, is_active=True).order_by(Article.order).all()
    return render_template('edit_article.html', article=article, parent_articles=parent_articles, disabled_ids=disabled_ids)

@app.route('/admin/articles/<int:article_id>/delete', methods=['POST'])
def delete_article(article_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))

    article = Article.query.get_or_404(article_id)
    
    # Recursively delete children
    def delete_children(parent_id):
        children = Article.query.filter_by(parent_id=parent_id).all()
        for child in children:
            # Delete media file
            if child.media_path:
                media_full_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(child.media_path))
                if os.path.exists(media_full_path):
                    os.remove(media_full_path)
            delete_children(child.id)
            db.session.delete(child)
    
    # Delete media file of main article
    if article.media_path:
        media_full_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(article.media_path))
        if os.path.exists(media_full_path):
            os.remove(media_full_path)
    
    # Delete children recursively
    delete_children(article_id)
    
    # Delete the article itself
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted!')
    return redirect(url_for('admin_articles'))

@app.route('/admin/articles/<int:article_id>/media/delete', methods=['POST'])
def delete_article_media(article_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))

    article = Article.query.get_or_404(article_id)
    
    if article.media_path:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(article.media_path))
        if os.path.exists(file_path):
            os.remove(file_path)
        article.media_path = None
        article.media_type = None
        db.session.commit()
        flash('Media deleted!')
    
    return redirect(url_for('edit_article', article_id=article_id))


def init_db():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if not inspector.get_table_names():
            db.create_all()
        create_admin()

init_db()

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
