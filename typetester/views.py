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
        default_texts = {
            ('easy', 'ru'): "Кот сидит на окне. Солнце светит ярко. Девочка читает книгу. Мальчик играет с "
            "машинкой. В саду растут цветы и яблоки. Птицы поют весело. Мама готовит обед. Папа чинит велосипед. "
            "Все счастливы.",
            ('medium', 'ru'): "Эффективное управление временем - ключ к продуктивности. Вместо того чтобы "
            "пытаться сделать всё сразу, разумнее расставлять приоритеты и делить большие задачи на маленькие "
            "шаги. Метод «Помодоро», например, предлагает работать 25 минут без отвлечений, а затем делать короткий "
            "перерыв. Такой подход помогает сохранять концентрацию и избегать выгорания. Важно также уметь говорить "
            "'нет' лишним просьбам и защищать своё расписание. Помните: отдых - не роскошь, а необходимая часть рабочего "
            "процесса.",
            ('hard', 'ru'): "Современные квантовые компьютеры используют принцип суперпозиции и квантовой запутанности "
            "для выполнения вычислений, недоступных классическим системам. Алгоритм Шора, например, способен факторизовать "
            "большие числа экспоненциально быстрее, чем любой известный классический алгоритм, что ставит под угрозу безопасность "
            "криптографических протоколов, основанных на RSA. В то же время, декогеренция остаётся главным препятствием на пути к "
            "созданию масштабируемых квантовых процессоров. Исследователи из лабораторий Google, IBM и IonQ активно работают над "
            "коррекцией квантовых ошибок, применяя топологические коды и сверхпроводящие кубиты, охлаждённые до температур, близких "
            "к абсолютному нулю. Несмотря на прогресс, практическое применение fault-tolerant quantum computing всё ещё находится на "
            "горизонте следующего десятилетия.",
            ('easy', 'en'): "The sun is bright. A dog runs in the park. Birds fly high. Anna drinks tea."
            "Tom plays with a ball. Flowers bloom in spring. It is a happy day.",
            ('medium', 'en'): "Learning to type quickly takes practice and patience. It’s important to keep"
            "your fingers on the home row and avoid looking at the keyboard. Many people improve their speed"
            "by using online typing tutors or playing typing games. Consistency matters more than speed at"
            "first—accuracy builds confidence and reduces errors over time.",
            ('hard', 'en'): "Quantum entanglement describes a phenomenon where particles become intrinsically"
            "linked, such that the state of one instantly influences the other—regardless of distance. This non-local"
            "correlation, famously called “spooky action at a distance” by Einstein, defies classical intuition but has"
            "been repeatedly confirmed through Bell test experiments. Harnessing entanglement is essential for quantum"
            "cryptography, teleportation protocols, and error-resistant quantum computing architectures.",
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