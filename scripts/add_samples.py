#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'type_master.settings')
django.setup()

from typetester.models import TextSample

def create_samples():
    samples = [
        # Русские легкие
        ("Привет! Это тест скорости печати.", "easy", "ru"),
        ("Солнце светит ярко, птицы поют.", "easy", "ru"),
        ("Я люблю программировать на Python.", "easy", "ru"),
        
        # Русские средние
        ("Программирование — искусство создания инструкций.", "medium", "ru"),
        ("Быстрая лиса прыгает через собаку.", "medium", "ru"),
        
        # Русские сложные
        ("Квантовые компьютеры используют кубиты.", "hard", "ru"),
        ("Нейронные сети имитируют работу мозга.", "hard", "ru"),
        
        # Английские
        ("Hello! This is typing speed test.", "easy", "en"),
        ("The quick brown fox jumps over dog.", "easy", "en"),
        ("Programming allows us to create amazing things.", "medium", "en"),
    ]
    
    for text, difficulty, language in samples:
        TextSample.objects.create(
            text=text,
            difficulty=difficulty,
            language=language
        )
    
    print(f"✅ Создано {len(samples)} тестовых текстов")

if __name__ == "__main__":
    create_samples()