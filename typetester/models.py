from django.db import models
from django.contrib.auth.models import User

class TextSample(models.Model):
    """Образцы текста для тестирования"""
    text = models.TextField(verbose_name="Текст")
    difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Легкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ], verbose_name="Сложность", default='easy')
    language = models.CharField(max_length=10, choices=[
        ('ru', 'Русский'),
        ('en', 'Английский'),
    ], verbose_name="Язык", default='ru')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Текст для теста"
        verbose_name_plural = "Тексты для тестов"
    
    def __str__(self):
        return f"{self.get_difficulty_display()} - {self.get_language_display()}"

class TypingTestResult(models.Model):
    """Результаты тестирования скорости печати"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    text_sample = models.ForeignKey(TextSample, on_delete=models.SET_NULL, null=True, verbose_name="Текст теста")
    
    # Основные метрики
    wpm = models.FloatField(verbose_name="Слов в минуту (WPM)")
    accuracy = models.FloatField(verbose_name="Точность (%)")
    words_count = models.IntegerField(verbose_name="Количество слов")
    time_seconds = models.FloatField(verbose_name="Время (сек)")
    mistakes_count = models.IntegerField(verbose_name="Количество ошибок")
    
    # Дополнительная информация
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP адрес")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата теста")
    
    class Meta:
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестов"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.wpm} WPM ({self.accuracy}%) - {self.user.username if self.user else 'Аноним'}"