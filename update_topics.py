#!/usr/bin/env python3
"""Update the 'Course Topics' block and add a landing page for the third course"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Course, LandingPage
import json

with app.app_context():
    print("Updating 'Course Topics' block...")
    
    # Find all courses
    courses = Course.query.all()
    
    for course in courses:
        landing = LandingPage.query.filter_by(course_id=course.id).first()
        
        if course.title == 'Йога для начинающих':
            if landing:
                landing.topics = json.dumps([
                    {'title': 'Асаны стоя', 'description': 'Basic standing poses for strengthening legs and core', 'subitems': [
                        {'name': 'Тадасана (поза горы)', 'icon': 'fas fa-mountain'},
                        {'name': 'Адхо мукха шванасана (собака мордой вниз)', 'icon': 'fas fa-dog'},
                        {'name': 'Врикшасана (поза дерева)', 'icon': 'fas fa-tree'},
                        {'name': 'Вирабхадрасана (поза воина)', 'icon': 'fas fa-fist-raised'}
                    ]},
                    {'title': 'Асаны сидя', 'description': 'Poses for stretching and relaxation', 'subitems': [
                        {'name': 'Падмасана (лотос)', 'icon': 'fas fa-lotus'},
                        {'name': 'Сукхасана (легкая поза)', 'icon': 'fas fa-couch'},
                        {'name': 'Дандасана (поза посоха)', 'icon': 'fas fa-staff'}
                    ]},
                    {'title': 'Пранаяма', 'description': 'Breathing practices for oxygenation', 'subitems': [
                        {'name': 'Полное йоговское дыхание', 'icon': 'fas fa-lungs'},
                        {'name': 'Анулома-вилома (попеременное дыхание)', 'icon': 'fas fa-random'},
                        {'name': 'Капалабхати (дыхание огня)', 'icon': 'fas fa-fire'},
                        {'name': 'Бхрамари (дыхание пчелы)', 'icon': 'fas fa-bee'}
                    ]},
                    {'title': 'Медитация', 'description': 'Practices for calming the mind', 'subitems': [
                        {'name': 'Мантра-медитация', 'icon': 'fas fa-om'},
                        {'name': 'Випассана', 'icon': 'fas fa-eye'},
                        {'name': 'Медитация осознанности', 'icon': 'fas fa-brain'},
                        {'name': 'Шавасана (расслабление)', 'icon': 'fas fa-bed'}
                    ]},
                    {'title': 'Философия йоги', 'description': 'Foundations of teaching and life principles', 'subitems': [
                        {'name': 'Яма и нияма', 'icon': 'fas fa-balance-scale'},
                        {'name': 'Восемь ступеней йоги', 'icon': 'fas fa-stairs'},
                        {'name': 'Принципы здорового образа жизни', 'icon': 'fas fa-heartbeat'}
                    ]}
                ])
                print(f"Updated 'Course Topics' block for: {course.title}")
        
        elif course.title == 'Функциональный тренинг':
            if landing:
                landing.topics = json.dumps([
                    {'title': 'Силовые тренировки', 'description': 'Exercises for developing muscular strength and endurance', 'subitems': [
                        {'name': 'Приседания со штангой', 'icon': 'fas fa-dumbbell'},
                        {'name': 'Отжимания от пола', 'icon': 'fas fa-hands'},
                        {'name': 'Планка (классическая, боковая)', 'icon': 'fas fa-stopwatch'},
                        {'name': 'Выпады и обратные выпады', 'icon': 'fas fa-walking'},
                        {'name': 'Тяга и жим', 'icon': 'fas fa-weight-hanging'}
                    ]},
                    {'title': 'Кардио', 'description': 'Exercises for training the cardiovascular system', 'subitems': [
                        {'name': 'Бег (интервальный, кросс)', 'icon': 'fas fa-running'},
                        {'name': 'Прыжки на скакалке', 'icon': 'fas fa-circle-notch'},
                        {'name': 'Берпи', 'icon': 'fas fa-bolt'},
                        {'name': 'Интервальные тренировки HIIT', 'icon': 'fas fa-tachometer-alt'},
                        {'name': 'Степ-платформа', 'icon': 'fas fa-shoe-prints'}
                    ]},
                    {'title': 'Растяжка и мобильность', 'description': 'Working on flexibility and joint mobility', 'subitems': [
                        {'name': 'Динамическая разминка', 'icon': 'fas fa-sync-alt'},
                        {'name': 'Статическая растяжка', 'icon': 'fas fa-hourglass-half'},
                        {'name': 'Фасциальный релиз (ролл)', 'icon': 'fas fa-compress-arrows-alt'}
                    ]},
                    {'title': 'Функциональные движения', 'description': 'Natural movement patterns for everyday life', 'subitems': [
                        {'name': 'Базовые паттерны: присед, наклон, выпад', 'icon': 'fas fa-redo'},
                        {'name': 'Работа с собственным весом', 'icon': 'fas fa-user'},
                        {'name': 'Упражнения на баланс и координацию', 'icon': 'fas fa-balance-scale'}
                    ]},
                    {'title': 'Восстановление', 'description': 'Relaxation and recovery methods after workouts', 'subitems': [
                        {'name': 'Заминка', 'icon': 'fas fa-wind'},
                        {'name': 'Дыхательные практики', 'icon': 'fas fa-lungs'},
                        {'name': 'Сон и восстановление', 'icon': 'fas fa-moon'}
                    ]}
                ])
                print(f"Updated 'Course Topics' block for: {course.title}")
        
        elif course.title == 'Питание и здоровье':
            if not landing:
                # Create landing page for the third course
                landing = LandingPage(
                    course_id=course.id,
                    header_title='Питание и здоровье',
                    header_subtitle='Learn how to eat right for health and energy',
                    header_background_image='uploads/landing_nutrition.jpg',
                    header_call_to_action='Learn More',
                    target_audience=json.dumps([
                        {'title': 'Все желающие', 'description': 'For those who want to improve their nutrition'},
                        {'title': 'Спортсмены', 'description': 'To optimize diet for workouts'}
                    ]),
                    timeline=json.dumps([
                        {'title': 'Неделя 1-2', 'description': 'Basics of nutrition science'},
                        {'title': 'Неделя 3-4', 'description': 'Creating a meal plan'}
                    ]),
                    course_program=json.dumps([
                        {'title': 'Модуль 1', 'lessons': ['Nutrition Basics']},
                        {'title': 'Модуль 2', 'lessons': ['Diet Planning']}
                    ]),
                    faq=json.dumps([
                        {'question': 'Is the course suitable for vegetarians?', 'answer': 'Yes, we cover different types of diets'}
                    ]),
                    topics=json.dumps([
                        {'title': 'Макронутриенты', 'description': 'Basic nutrients: proteins, fats, carbohydrates', 'subitems': [
                            {'name': 'Белки: роль, нормы, источники', 'icon': 'fas fa-egg'},
                            {'name': 'Жиры: полезные и вредные', 'icon': 'fas fa-oil-can'},
                            {'name': 'Углеводы: сложные и простые', 'icon': 'fas fa-bread-slice'}
                        ]},
                        {'title': 'Микронутриенты', 'description': 'Vitamins and minerals for body health', 'subitems': [
                            {'name': 'Витамины: обзор групп', 'icon': 'fas fa-pills'},
                            {'name': 'Минералы и микроэлементы', 'icon': 'fas fa-atom'},
                            {'name': 'Важность воды и гидратации', 'icon': 'fas fa-tint'}
                        ]},
                        {'title': 'Режим питания', 'description': 'When and how often to eat', 'subitems': [
                            {'name': 'Частота приемов пищи', 'icon': 'fas fa-clock'},
                            {'name': 'Питание до и после тренировки', 'icon': 'fas fa-utensils'},
                            {'name': 'Интервальное голодание', 'icon': 'fas fa-calendar-times'}
                        ]},
                        {'title': 'Составление рациона', 'description': 'Practical skills for menu planning', 'subitems': [
                            {'name': 'Калькуляция калорий', 'icon': 'fas fa-calculator'},
                            {'name': 'Подбор продуктов', 'icon': 'fas fa-shopping-basket'},
                            {'name': 'Меню на неделю', 'icon': 'fas fa-calendar-alt'}
                        ]},
                        {'title': 'Здоровые привычки', 'description': 'Forming a healthy relationship with food', 'subitems': [
                            {'name': 'Чтение этикеток', 'icon': 'fas fa-clipboard-list'},
                            {'name': 'Планирование покупок', 'icon': 'fas fa-shopping-cart'},
                            {'name': 'Приготовление еды дома', 'icon': 'fas fa-home'}
                        ]}
                    ]),
                    cta_title='Eat Right!',
                    cta_text='Change your diet and feel the energy boost!',
                    is_active=True
                )
                db.session.add(landing)
                print(f"Created landing page for course: {course.title}")
            else:
                landing.topics = json.dumps([
                    {'title': 'Макронутриенты', 'subitems': ['Белки: роль, нормы, источники', 'Жиры: полезные и вредные', 'Углеводы: сложные и простые']},
                    {'title': 'Микронутриенты', 'subitems': ['Витамины: обзор групп', 'Минералы и микроэлементы', 'Важность воды и гидратации']},
                    {'title': 'Режим питания', 'subitems': ['Частота приемов пищи', 'Питание до и после тренировки', 'Интервальное голодание']},
                    {'title': 'Составление рациона', 'subitems': ['Калькуляция калорий', 'Подбор продуктов', 'Меню на неделю']},
                    {'title': 'Здоровые привычки', 'subitems': ['Чтение этикеток', 'Планирование покупок', 'Приготовление еды дома']}
                ])
                print(f"Updated 'Course Topics' block for: {course.title}")
    
    db.session.commit()
    print("\n'Course Topics' block successfully updated for all courses!")
    
    # Check the result
    for course in courses:
        landing = LandingPage.query.filter_by(course_id=course.id).first()
        if landing and landing.topics:
            topics = json.loads(landing.topics)
            print(f"\n{course.title}:")
            print(f"  Number of topics: {len(topics)}")
            for topic in topics:
                print(f"    - {topic['title']}: {len(topic['subitems'])} subtopics")
