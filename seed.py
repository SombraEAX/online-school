#!/usr/bin/env python3
"""Seed the database with comprehensive test data.

Safe to run multiple times — only seeds if the database is empty.
Designed for Render.com pre-deploy step: python seed.py
"""
import os
import sys
import shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import User, Course, Module, Lesson, LandingPage, AuthorBlock
from app import ThemeSettings, SiteSettings, HomePage, Article, BotUser, BotSettings
from werkzeug.security import generate_password_hash
from datetime import datetime
import json
import urllib.request
import ssl

SEED_DIR = 'static/seed'
UPLOAD_DIR = 'static/uploads'

SEED_IMAGES = [
    'python-course.jpg',
    'flask-course.jpg',
    'datascience-course.jpg',
    'author-sarah.jpg',
    'author-michael.jpg',
    'landing-python-bg.jpg',
    'landing-flask-bg.jpg',
    'landing-datascience-bg.jpg',
    'landing-python-cta.jpg',
    'landing-flask-cta.jpg',
    'landing-datascience-cta.jpg',
    'home-header-bg.jpg',
    'home-cta.jpg',
    'test-image.jpg',
]

def _seed_images():
    print(f"\nCopying images from {SEED_DIR}/ to {UPLOAD_DIR}/...")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ok = 0
    for name in SEED_IMAGES:
        src = os.path.join(SEED_DIR, name)
        dst = os.path.join(UPLOAD_DIR, name)
        try:
            if os.path.exists(src):
                shutil.copy2(src, dst)
                ok += 1
            else:
                print(f"  warning: seed image not found: {src}")
        except Exception as e:
            print(f"  warning: could not copy {name}: {e}")
    # Video — download if missing
    video_path = os.path.join(UPLOAD_DIR, 'test-video.mp4')
    if not os.path.exists(video_path):
        try:
            ctx = ssl._create_unverified_context()
            data = urllib.request.urlopen(
                'https://www.w3schools.com/html/mov_bbb.mp4', context=ctx, timeout=30
            ).read()
            with open(video_path, 'wb') as f:
                f.write(data)
            ok += 1
        except Exception as e:
            print(f"  warning: could not download test-video.mp4: {e}")
    else:
        ok += 1
    print(f"  {ok}/{len(SEED_IMAGES) + 1} files ready")

with app.app_context():
    _seed_images()

    if Course.query.first():
        print("Database already has data — skipping seed.")
        sys.exit(0)

    users_data = [
        {'username': 'admin', 'email': 'admin@school.com', 'password': 'admin123', 'role': 'admin'},
        {'username': 'john', 'email': 'john@example.com', 'password': 'password123', 'role': 'user'},
        {'username': 'emma', 'email': 'emma@example.com', 'password': 'password123', 'role': 'user'},
        {'username': 'alex', 'email': 'alex@example.com', 'password': 'password123', 'role': 'user'},
        {'username': 'sarah', 'email': 'sarah@example.com', 'password': 'password123', 'role': 'user'},
    ]
    for u in users_data:
        if not User.query.filter_by(username=u['username']).first():
            db.session.add(User(
                username=u['username'], email=u['email'],
                password_hash=generate_password_hash(u['password']),
                role=u['role'], is_active=True
            ))
    print("  users: admin + 4 regular")

    site = SiteSettings(site_name='Online School',
        site_description='High-quality online courses on programming, data science, and web development.')
    db.session.add(site)
    print("  site settings")

    theme = ThemeSettings(
        primary_color='#4A90D9', secondary_color='#357ABD',
        text_color='#212121', bg_color='#FFFFFF', heading_color='#212121',
        accent_color='#E67E22', button_color='#4A90D9', button_text_color='#FFFFFF')
    db.session.add(theme)
    print("  theme settings")

    authors = [
        AuthorBlock(name='Sarah Johnson', title='Full-Stack Developer',
            bio='Over 12 years of experience in web development. Specializes in Python, JavaScript, and cloud architecture.',
            image='author-sarah.jpg', is_active=True),
        AuthorBlock(name='Michael Chen', title='Data Science Lead',
            bio='PhD in Computer Science from MIT. Expert in machine learning and deep learning.',
            image='author-michael.jpg', is_active=True),
    ]
    db.session.add_all(authors)
    print("  authors: 2")

    courses = [
        Course(title='Python for Beginners',
            description='A comprehensive introduction to Python programming. Learn syntax, data structures, functions, and build real-world projects.',
            price=49.00, is_active=True, published=True, image='python-course.jpg'),
        Course(title='Web Development with Flask',
            description='Build modern web applications from scratch using Flask. Covers routing, templates, databases, authentication, REST APIs, and deployment.',
            price=79.00, is_active=True, published=True, image='flask-course.jpg'),
        Course(title='Data Science Fundamentals',
            description='Master data science: statistics, pandas, visualization, and introductory machine learning with scikit-learn.',
            price=99.00, is_active=True, published=True, image='datascience-course.jpg'),
    ]
    db.session.add_all(courses)
    db.session.flush()
    print("  courses: 3")

    modules_data = [
        Module(title='Getting Started with Python', course_id=courses[0].id, order=1),
        Module(title='Core Language Concepts', course_id=courses[0].id, order=2),
        Module(title='Working with Data', course_id=courses[0].id, order=3),
        Module(title='Building Projects', course_id=courses[0].id, order=4),
        Module(title='Flask Fundamentals', course_id=courses[1].id, order=1),
        Module(title='Databases & Authentication', course_id=courses[1].id, order=2),
        Module(title='Advanced Flask & APIs', course_id=courses[1].id, order=3),
        Module(title='Deployment & Production', course_id=courses[1].id, order=4),
        Module(title='Statistics & Probability', course_id=courses[2].id, order=1),
        Module(title='Data Manipulation with Pandas', course_id=courses[2].id, order=2),
        Module(title='Data Visualization', course_id=courses[2].id, order=3),
        Module(title='Introduction to Machine Learning', course_id=courses[2].id, order=4),
    ]
    db.session.add_all(modules_data)
    db.session.flush()
    print("  modules: 12")

    lessons_data = [
        Lesson(title='Welcome & Setup', content='<p>Install Python, set up your development environment, and write your first program.</p>', module_id=modules_data[0].id, order=1),
        Lesson(title='Hello, World!', content='<p>Write your first Python program. Learn about the <code>print()</code> function.</p>', module_id=modules_data[0].id, order=2),
        Lesson(title='Variables & Data Types', content='<p>Integers, floats, strings, booleans. Variable naming and type conversion.</p>', module_id=modules_data[0].id, order=3),
        Lesson(title='Conditional Statements', content='<p>Master <code>if</code>, <code>elif</code>, <code>else</code>. Comparison operators and boolean logic.</p>', module_id=modules_data[1].id, order=1),
        Lesson(title='Loops', content='<p><code>for</code> and <code>while</code> loops. Iterate, use <code>range()</code>, <code>break</code>, <code>continue</code>.</p>', module_id=modules_data[1].id, order=2),
        Lesson(title='Functions', content='<p>Define functions with <code>def</code>. Parameters, return values, lambdas.</p>', module_id=modules_data[1].id, order=3),
        Lesson(title='Lists & Tuples', content='<p>Create and manipulate lists and tuples. Indexing, slicing, comprehensions.</p>', module_id=modules_data[2].id, order=1),
        Lesson(title='Dictionaries & Sets', content='<p>Key-value pairs with dicts. Unordered collections with sets.</p>', module_id=modules_data[2].id, order=2),
        Lesson(title='File I/O', content='<p>Read/write files. CSV, JSON formats.</p>', module_id=modules_data[2].id, order=3),
        Lesson(title='To-Do List App', content='<p>Build a command-line to-do app. Apply everything you have learned.</p>', module_id=modules_data[3].id, order=1),
        Lesson(title='Setting Up Flask', content='<p>Install Flask, understand app structure, create your first route.</p>', module_id=modules_data[4].id, order=1),
        Lesson(title='Routing & Views', content='<p>Routes with dynamic parameters, HTTP methods, URL building.</p>', module_id=modules_data[4].id, order=2),
        Lesson(title='Jinja2 Templates', content='<p>Dynamic HTML with template inheritance, variables, filters, control structures.</p>', module_id=modules_data[4].id, order=3),
        Lesson(title='SQLAlchemy Models', content='<p>Define models, create relationships, perform CRUD operations.</p>', module_id=modules_data[5].id, order=1),
        Lesson(title='User Registration & Login', content='<p>Authentication from scratch. Password hashing, sessions, login/logout.</p>', module_id=modules_data[5].id, order=2),
        Lesson(title='REST API with Flask', content='<p>Build a JSON REST API with request parsing and response formatting.</p>', module_id=modules_data[6].id, order=1),
        Lesson(title='Deploying to Production', content='<p>Gunicorn, environment variables, Docker, cloud deployment.</p>', module_id=modules_data[7].id, order=1),
        Lesson(title='Descriptive Statistics', content='<p>Mean, median, mode, variance, standard deviation, distributions.</p>', module_id=modules_data[8].id, order=1),
        Lesson(title='Probability Basics', content='<p>Probability rules, conditional probability, Bayes theorem, distributions.</p>', module_id=modules_data[8].id, order=2),
        Lesson(title='Pandas: Series & DataFrames', content='<p>Introduction to pandas. Manipulating Series and DataFrames. CSV/Excel.</p>', module_id=modules_data[9].id, order=1),
        Lesson(title='Data Cleaning', content='<p>Handle missing values, remove duplicates, filter outliers, transform data.</p>', module_id=modules_data[9].id, order=2),
        Lesson(title='Matplotlib & Seaborn', content='<p>Publication-quality visualizations: line, bar, scatter, histograms, heatmaps.</p>', module_id=modules_data[10].id, order=1),
        Lesson(title='Supervised Learning', content='<p>Linear/ logistic regression, decision trees, train/test evaluation.</p>', module_id=modules_data[11].id, order=1),
    ]
    db.session.add_all(lessons_data)
    print(f"  lessons: {len(lessons_data)}")

    landing_pages_data = [
        LandingPage(
            course_id=courses[0].id,
            header_title='Python for Beginners',
            header_subtitle='Start your programming journey today — no experience needed.',
            header_call_to_action='Enroll Now — $49',
            header_background_image='landing-python-bg.jpg',
            target_audience=json.dumps([
                {'image': 'fas fa-user', 'title': 'Absolute Beginners', 'description': 'No prior experience required.'},
                {'image': 'fas fa-briefcase', 'title': 'Career Changers', 'description': 'Python is the most in-demand skill.'},
                {'image': 'fas fa-graduation-cap', 'title': 'Students', 'description': 'Add a valuable skill to your resume.'},
            ]),
            audience_section_title='Who is this course for?',
            timeline=json.dumps([
                {'image': 'fas fa-play', 'title': 'Week 1-2', 'description': 'Python syntax, variables, data types'},
                {'image': 'fas fa-book-open', 'title': 'Week 3-4', 'description': 'Control flow, loops, functions, data structures'},
                {'image': 'fas fa-laptop-code', 'title': 'Week 5-6', 'description': 'File handling, modules, error handling'},
                {'image': 'fas fa-rocket', 'title': 'Week 7-8', 'description': 'Capstone project'},
            ]),
            timeline_section_title='Course Timeline',
            course_program=json.dumps([
                {'image': 'fas fa-play-circle', 'title': 'Module 1: Getting Started', 'lessons': ['Setup', 'Hello World', 'Variables']},
                {'image': 'fas fa-layer-group', 'title': 'Module 2: Core Concepts', 'lessons': ['Conditionals', 'Loops', 'Functions']},
                {'image': 'fas fa-book', 'title': 'Module 3: Working with Data', 'lessons': ['Lists', 'Dicts', 'File I/O']},
                {'image': 'fas fa-rocket', 'title': 'Module 4: Projects', 'lessons': ['To-Do App', 'Error Handling']},
            ]),
            course_program_section_title='Course Program',
            faq=json.dumps([
                {'question': 'Do I need prior programming experience?', 'answer': 'No, this course is designed for absolute beginners.'},
                {'question': 'What tools do I need?', 'answer': 'Just a computer and an internet connection.'},
                {'question': 'How long does it take?', 'answer': 'Most students finish in 6-8 weeks studying 5-7 hours per week.'},
            ]),
            faq_section_title='Frequently Asked Questions',
            topics=json.dumps([
                {'title': 'Python Basics', 'description': 'Core language fundamentals', 'subitems': [
                    {'name': 'Variables & Data Types', 'icon': 'fas fa-check-circle'},
                    {'name': 'Strings & Formatting', 'icon': 'fas fa-check-circle'},
                    {'name': 'Boolean Logic', 'icon': 'fas fa-check-circle'},
                ]},
                {'title': 'Data Structures', 'description': 'Working with collections', 'subitems': [
                    {'name': 'Lists & Tuples', 'icon': 'fas fa-check-circle'},
                    {'name': 'Dictionaries & Sets', 'icon': 'fas fa-check-circle'},
                    {'name': 'List Comprehensions', 'icon': 'fas fa-check-circle'},
                ]},
                {'title': 'Control Flow', 'description': 'Making decisions', 'subitems': [
                    {'name': 'If / Elif / Else', 'icon': 'fas fa-check-circle'},
                    {'name': 'For Loops', 'icon': 'fas fa-check-circle'},
                    {'name': 'Try / Except', 'icon': 'fas fa-check-circle'},
                ]},
            ]),
            topics_section_title='What You Will Learn',
            topics_section_description='From beginner to confident Python programmer.',
            cta_title='Ready to Start Coding?',
            cta_text='Join over 5,000 students. Start today with lifetime access.',
            cta_image='landing-python-cta.jpg',
            is_active=True
        ),
        LandingPage(
            course_id=courses[1].id,
            header_title='Web Development with Flask',
            header_background_image='landing-flask-bg.jpg',
            header_subtitle='Build and deploy real-world web applications using Python and Flask.',
            header_call_to_action='Start Learning — $79',
            target_audience=json.dumps([
                {'image': 'fas fa-code', 'title': 'Python Developers', 'description': 'Know Python basics, want to build web apps'},
                {'image': 'fas fa-laptop', 'title': 'Aspiring Web Devs', 'description': 'Learn backend web development'},
            ]),
            audience_section_title='Who is this course for?',
            timeline=json.dumps([
                {'image': 'fas fa-play', 'title': 'Week 1-2', 'description': 'Flask fundamentals: routes, views, templates'},
                {'image': 'fas fa-database', 'title': 'Week 3-4', 'description': 'Databases with SQLAlchemy'},
                {'image': 'fas fa-user-lock', 'title': 'Week 5-6', 'description': 'User authentication'},
                {'image': 'fas fa-cloud-upload-alt', 'title': 'Week 7-8', 'description': 'REST APIs and deployment'},
            ]),
            timeline_section_title='Course Timeline',
            course_program=json.dumps([
                {'image': 'fas fa-play-circle', 'title': 'Module 1: Flask Fundamentals', 'lessons': ['Setup', 'Routing', 'Templates']},
                {'image': 'fas fa-database', 'title': 'Module 2: Databases & Auth', 'lessons': ['SQLAlchemy', 'Registration', 'Login']},
                {'image': 'fas fa-code', 'title': 'Module 3: Advanced Flask', 'lessons': ['REST API']},
                {'image': 'fas fa-ship', 'title': 'Module 4: Deployment', 'lessons': ['Gunicorn', 'Docker', 'Production']},
            ]),
            course_program_section_title='Course Program',
            faq=json.dumps([
                {'question': 'Do I need to know HTML/CSS?', 'answer': 'Basic HTML is helpful but not required.'},
                {'question': 'Will I build real projects?', 'answer': 'Yes, a complete web app with auth, database, and API.'},
            ]),
            faq_section_title='Frequently Asked Questions',
            topics=json.dumps([
                {'title': 'Flask Framework', 'description': 'Core concepts', 'subitems': [
                    {'name': 'Application Setup', 'icon': 'fas fa-check-circle'},
                    {'name': 'URL Routing', 'icon': 'fas fa-check-circle'},
                    {'name': 'HTTP Methods', 'icon': 'fas fa-check-circle'},
                ]},
                {'title': 'Templates', 'description': 'Dynamic pages with Jinja2', 'subitems': [
                    {'name': 'Template Inheritance', 'icon': 'fas fa-check-circle'},
                    {'name': 'Variables & Filters', 'icon': 'fas fa-check-circle'},
                    {'name': 'Forms & Validation', 'icon': 'fas fa-check-circle'},
                ]},
                {'title': 'Databases', 'description': 'SQLAlchemy', 'subitems': [
                    {'name': 'Model Definitions', 'icon': 'fas fa-check-circle'},
                    {'name': 'Relationships', 'icon': 'fas fa-check-circle'},
                    {'name': 'CRUD Operations', 'icon': 'fas fa-check-circle'},
                ]},
                {'title': 'Authentication', 'description': 'User management', 'subitems': [
                    {'name': 'Password Hashing', 'icon': 'fas fa-check-circle'},
                    {'name': 'Login / Logout', 'icon': 'fas fa-check-circle'},
                    {'name': 'Session Management', 'icon': 'fas fa-check-circle'},
                ]},
            ]),
            topics_section_title='Curriculum Overview',
            topics_section_description='From Flask basics to production-ready apps.',
            cta_title='Build Your First Web App',
            cta_text='Stop watching tutorials — start building.',
            cta_image='landing-flask-cta.jpg',
            is_active=True
        ),
        LandingPage(
            course_id=courses[2].id,
            header_title='Data Science Fundamentals',
            header_background_image='landing-datascience-bg.jpg',
            header_subtitle='Turn raw data into actionable insights.',
            header_call_to_action='Enroll Now — $99',
            target_audience=json.dumps([
                {'image': 'fas fa-chart-line', 'title': 'Aspiring Data Scientists', 'description': 'Start your data science journey'},
                {'image': 'fas fa-code', 'title': 'Python Developers', 'description': 'Expand into data analysis'},
            ]),
            audience_section_title='Who is this course for?',
            timeline=json.dumps([
                {'image': 'fas fa-play', 'title': 'Week 1-2', 'description': 'Statistics foundations'},
                {'image': 'fas fa-table', 'title': 'Week 3-4', 'description': 'Pandas data manipulation'},
                {'image': 'fas fa-chart-bar', 'title': 'Week 5-6', 'description': 'Data visualization'},
                {'image': 'fas fa-brain', 'title': 'Week 7-8', 'description': 'Machine learning intro'},
            ]),
            timeline_section_title='Course Timeline',
            course_program=json.dumps([
                {'image': 'fas fa-calculator', 'title': 'Module 1: Statistics', 'lessons': ['Descriptive Stats', 'Probability']},
                {'image': 'fas fa-table', 'title': 'Module 2: Pandas', 'lessons': ['DataFrames', 'Data Cleaning']},
                {'image': 'fas fa-chart-bar', 'title': 'Module 3: Visualization', 'lessons': ['Matplotlib', 'Seaborn']},
                {'image': 'fas fa-brain', 'title': 'Module 4: ML Intro', 'lessons': ['Supervised Learning']},
            ]),
            course_program_section_title='Course Program',
            faq=json.dumps([
                {'question': 'What math background is required?', 'answer': 'Basic high school math is sufficient.'},
                {'question': 'Will I use real datasets?', 'answer': 'Yes, including datasets from Kaggle.'},
            ]),
            faq_section_title='Frequently Asked Questions',
            topics=json.dumps([
                {'title': 'Statistics', 'description': 'Essential concepts', 'subitems': [
                    {'name': 'Descriptive Statistics', 'icon': 'fas fa-check-circle'},
                    {'name': 'Probability Distributions', 'icon': 'fas fa-check-circle'},
                    {'name': 'Hypothesis Testing', 'icon': 'fas fa-check-circle'},
                ]},
                {'title': 'Pandas', 'description': 'Data analysis', 'subitems': [
                    {'name': 'Series & DataFrames', 'icon': 'fas fa-check-circle'},
                    {'name': 'Filtering & Grouping', 'icon': 'fas fa-check-circle'},
                    {'name': 'Merging & Reshaping', 'icon': 'fas fa-check-circle'},
                ]},
                {'title': 'Visualization', 'description': 'Effective visuals', 'subitems': [
                    {'name': 'Matplotlib Basics', 'icon': 'fas fa-check-circle'},
                    {'name': 'Seaborn', 'icon': 'fas fa-check-circle'},
                    {'name': 'Dashboard Creation', 'icon': 'fas fa-check-circle'},
                ]},
                {'title': 'Machine Learning', 'description': 'ML algorithms', 'subitems': [
                    {'name': 'Linear & Logistic Regression', 'icon': 'fas fa-check-circle'},
                    {'name': 'Decision Trees', 'icon': 'fas fa-check-circle'},
                    {'name': 'Model Evaluation', 'icon': 'fas fa-check-circle'},
                ]},
            ]),
            topics_section_title='Full Curriculum',
            topics_section_description='From statistics to machine learning.',
            cta_title='Start Your Data Journey',
            cta_text='Data science is the most in-demand field in tech.',
            cta_image='landing-datascience-cta.jpg',
            is_active=True
        ),
    ]
    db.session.add_all(landing_pages_data)
    print("  landing pages: 3")

    home_page = HomePage(
        header_title='Welcome to Online School',
        header_subtitle='Master in-demand tech skills with expert-led courses. Learn Python, web development, data science, and more.',
        header_call_to_action='Browse Our Courses',
        header_background_image='home-header-bg.jpg',
        features=json.dumps([
            {'image': 'fas fa-user-check', 'title': 'Expert Instructors', 'description': 'Learn from industry professionals.'},
            {'image': 'fas fa-clock', 'title': 'Learn at Your Pace', 'description': 'Lifetime access. Study anytime.'},
            {'image': 'fas fa-headset', 'title': 'Community Support', 'description': 'Get help in community forums.'},
            {'image': 'fas fa-certificate', 'title': 'Certificates', 'description': 'Earn verified certificates.'},
        ]),
        features_section_title='Why Choose Us?',
        stats=json.dumps([
            {'number': '10,000+', 'label': 'Students'},
            {'number': '25+', 'label': 'Courses'},
            {'number': '4.8/5', 'label': 'Rating'},
        ]),
        stats_section_title='Our Impact',
        about_text=json.dumps([
            {'image': 'fas fa-bullseye', 'title': 'Our Mission', 'description': 'Quality tech education accessible to everyone. We believe that learning to code should be affordable, practical, and fun. Our courses are designed by industry experts who have years of real-world experience.'},
            {'image': 'fas fa-users', 'title': 'Our Community', 'description': 'Join a thriving community of over 10,000 learners from 50+ countries. Learn together through our forums, study groups, and live Q&A sessions. Our students go on to build careers at top tech companies.'},
            {'image': 'fas fa-handshake', 'title': 'Our Commitment', 'description': 'Every course includes hands-on projects, real-world examples, and lifetime updates. We offer a 30-day money-back guarantee because we are confident you will love the learning experience.'},
        ]),
        about_section_title='About Us',
        faq=json.dumps([
            {'question': 'How do I enroll?', 'answer': 'Browse courses, click Enroll, create an account, start learning.'},
            {'question': 'Can I access on mobile?', 'answer': 'Yes, all courses are fully responsive.'},
            {'question': 'Do you offer refunds?', 'answer': '30-day money-back guarantee on all courses.'},
            {'question': 'Will I receive a certificate?', 'answer': 'Yes, a verified certificate upon completion.'},
        ]),
        faq_section_title='FAQ',
        cta_title='Start Learning Today',
        cta_text='Join over 10,000 students. Your future in tech starts here.',
        cta_image='home-cta.jpg',
        chatbot_cta_text='Have questions? Chat with our bot.',
        chatbot_button_text='Open Chat Bot',
        chatbot_button_url='https://t.me/mira_test_school_bot',
        is_active=True
    )
    db.session.add(home_page)
    print("  home page")

    bot_settings = BotSettings(
        bot_token=os.getenv('BOT_TOKEN', ''),
        webhook_url='',
        is_active=True
    )
    db.session.add(bot_settings)
    print("  bot settings")

    bot_users = [
        BotUser(telegram_id='123456789', username='johndoe', first_name='John', last_name='Doe', is_active=True),
        BotUser(telegram_id='987654321', username='janesmith', first_name='Jane', last_name='Smith', is_active=True),
    ]
    db.session.add_all(bot_users)
    print("  bot users: 2")

    articles_root = Article(
        title='Getting Started with Our Platform',
        content='<b>Welcome!</b>\n\nThis guide helps you navigate the platform.\n\n<a href="https://example.com/welcome">Watch the welcome video</a>',
        order=1, is_active=True, media_path='uploads/test_image.jpg', media_type='photo',
        disable_link_preview=False
    )
    db.session.add(articles_root)
    db.session.flush()

    Article(title='Platform Overview',
        content='<i>Get familiar</i> with <b>key features</b>: Dashboard, Course Player, Community, Certificates.',
        parent_id=articles_root.id, order=1, is_active=True,
        media_path='uploads/test-video.mp4', media_type='video', disable_link_preview=True)
    Article(title='Quick Start Checklist',
        content='<b>Steps:</b>\n1. Complete your profile\n2. Enroll in a course\n3. Set a study schedule',
        parent_id=articles_root.id, order=2, is_active=True)

    articles_root2 = Article(
        title='Learning Tips & Resources',
        content='<b>How to succeed:</b>\n\n1. Study daily\n2. Take notes\n3. Do exercises\n4. Join discussions',
        order=2, is_active=True, disable_link_preview=False
    )
    db.session.add(articles_root2)
    db.session.flush()

    Article(title='Study Schedule Template',
        content='Monday: Watch lesson (1h)\nTuesday: Exercises (1h)\nWednesday: Review (30m)\nThursday: Project (1.5h)\nFriday: Discussion (30m)',
        parent_id=articles_root2.id, order=1, is_active=True)
    Article(title='Recommended Tools',
        content='<b>Tools:</b>\n• VS Code\n• Git\n• Notion\n• Discord',
        parent_id=articles_root2.id, order=2, is_active=True,
        media_path='uploads/test_image.jpg', media_type='photo')

    print("  articles: 6")

    db.session.commit()
    print("\nDatabase seeded successfully!")
    print(f"  Admin: admin / admin123")
    print(f"  Users: john / password123 (and 3 more)")
