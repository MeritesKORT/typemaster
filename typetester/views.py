from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Count
import json
import random
from .models import TextSample, TypingTestResult

def home(request):
    """Главная страница с выбором настроек"""
    # Статистика для отображения
    total_tests = TypingTestResult.objects.count()
    avg_wpm = TypingTestResult.objects.aggregate(Avg('wpm'))['wpm__avg'] or 0
    best_wpm = TypingTestResult.objects.aggregate(Max('wpm'))['wpm__max'] or 0
    
    context = {
        'total_tests': total_tests,
        'avg_wpm': round(avg_wpm, 1),
        'best_wpm': round(best_wpm, 1),
    }
    return render(request, 'typetester/home.html', context)

def typing_test(request):
    """Страница тестирования скорости печати"""
    difficulty = request.GET.get('difficulty', 'easy')
    language = request.GET.get('language', 'ru')
    
    # Получаем случайный текст
    samples = TextSample.objects.filter(difficulty=difficulty, language=language)
    
    if samples.exists():
        text_sample = random.choice(samples)
        text = text_sample.text
        text_id = text_sample.id
    else:
        # Дефолтные тексты если нет в базе
        default_texts = {
            ('easy', 'ru'): "Привет! Это тест скорости печати. Начните вводить этот текст как можно быстрее.",
            ('medium', 'ru'): "Программирование — это искусство создания инструкций для компьютера. Каждая строка кода важна.",
            ('hard', 'ru'): "Квантовые компьютеры используют принципы квантовой механики для выполнения вычислений.",
            ('easy', 'en'): "The quick brown fox jumps over the lazy dog. This sentence uses every letter.",
            ('medium', 'en'): "Python is a popular programming language known for its simplicity and readability.",
            ('hard', 'en'): "Machine learning algorithms can identify patterns in data and make predictions.",
        }
        text = default_texts.get((difficulty, language), "Начните печатать этот текст.")
        text_id = None
    
    context = {
        'text': text,
        'text_id': text_id,
        'difficulty': difficulty,
        'language': language,
    }
    return render(request, 'typetester/test.html', context)

@csrf_exempt
def save_result(request):
    """Сохранение результата теста (AJAX)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Получаем данные
            typed_text = data.get('typed_text', '')
            original_text = data.get('original_text', '')
            time_seconds = data.get('time_seconds', 0)
            text_id = data.get('text_id')
            
            # Подсчет слов и ошибок
            words = len(typed_text.split())
            
            # Подсчет ошибок (простейший алгоритм)
            mistakes = 0
            min_len = min(len(typed_text), len(original_text))
            for i in range(min_len):
                if typed_text[i] != original_text[i]:
                    mistakes += 1
            
            # Добавляем ошибки за пропущенные/лишние символы
            mistakes += abs(len(typed_text) - len(original_text))
            
            # Рассчитываем WPM и точность
            wpm = (words / time_seconds * 60) if time_seconds > 0 else 0
            accuracy = max(0, 100 - (mistakes / max(len(original_text), 1) * 100))
            
            # Получаем объект текста если есть ID
            text_sample = None
            if text_id:
                try:
                    text_sample = TextSample.objects.get(id=text_id)
                except TextSample.DoesNotExist:
                    pass
            
            # Сохраняем результат
            result = TypingTestResult(
                user=request.user if request.user.is_authenticated else None,
                text_sample=text_sample,
                wpm=round(wpm, 1),
                accuracy=round(accuracy, 1),
                words_count=words,
                time_seconds=round(time_seconds, 2),
                mistakes_count=mistakes,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            result.save()
            
            return JsonResponse({
                'success': True,
                'result_id': result.id,
                'wpm': result.wpm,
                'accuracy': result.accuracy,
                'words': words,
                'time': round(time_seconds, 2),
                'mistakes': mistakes
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def leaderboard(request):
    """Таблица лидеров"""
    # Лучшие результаты (топ 50)
    top_results = TypingTestResult.objects.all().order_by('-wpm')[:50]
    
    # Статистика
    total_users = TypingTestResult.objects.values('user').distinct().count()
    total_tests = TypingTestResult.objects.count()
    
    # Средние показатели
    stats = TypingTestResult.objects.aggregate(
        avg_wpm=Avg('wpm'),
        avg_accuracy=Avg('accuracy'),
        max_wpm=Max('wpm')
    )
    
    context = {
        'results': top_results,
        'total_users': total_users,
        'total_tests': total_tests,
        'avg_wpm': round(stats['avg_wpm'] or 0, 1),
        'avg_accuracy': round(stats['avg_accuracy'] or 0, 1),
        'max_wpm': round(stats['max_wpm'] or 0, 1),
    }
    return render(request, 'typetester/results.html', context)

@login_required
def my_results(request):
    """Личные результаты пользователя"""
    results = TypingTestResult.objects.filter(user=request.user).order_by('-created_at')
    
    # Статистика пользователя
    user_stats = results.aggregate(
        avg_wpm=Avg('wpm'),
        avg_accuracy=Avg('accuracy'),
        best_wpm=Max('wpm'),
        total_tests=Count('id')
    )
    
    context = {
        'results': results,
        'user_stats': user_stats,
    }
    return render(request, 'typetester/my_results.html', context)