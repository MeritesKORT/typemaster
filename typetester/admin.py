from django.contrib import admin
from .models import TextSample, TypingTestResult

@admin.register(TextSample)
class TextSampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'difficulty', 'language', 'created_at')
    list_filter = ('difficulty', 'language', 'created_at')
    search_fields = ('text',)
    list_per_page = 20

@admin.register(TypingTestResult)
class TypingTestResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wpm', 'accuracy', 'time_seconds', 'created_at')
    list_filter = ('created_at',)  # Убрали 'difficulty', так как его нет в модели
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('created_at',)
    list_per_page = 50
    
    # Если хотите фильтровать по difficulty через связанную таблицу TextSample
    def difficulty(self, obj):
        if obj.text_sample:
            return obj.text_sample.get_difficulty_display()
        return "Не указано"
    difficulty.short_description = "Сложность"
    
    # Тогда можно добавить difficulty в list_display, но не в list_filter
    list_display = ('id', 'user', 'difficulty', 'wpm', 'accuracy', 'time_seconds', 'created_at')