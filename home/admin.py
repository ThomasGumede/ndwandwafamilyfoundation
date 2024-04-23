from django.contrib import admin
from home.models import CategoryModel, PostModel, CommentModel, EmailModel, PrivacyModel, FAQ
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule
from django_celery_results.models import TaskResult, GroupResult
from django_celery_results.admin import TaskResultAdmin, GroupResultAdmin
from django_celery_beat.admin import CrontabScheduleAdmin, PeriodicTaskAdmin, ClockedScheduleAdmin

class CommentInline(admin.StackedInline):
    model = CommentModel
    readonly_fields = ("commenter", "created", "comment")
    extra = False

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    pass

@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("label", )
    date_hierarchy = "created"
    empty_value_display = "Empty"
    prepopulated_fields = {"slug": ["label"]}


@admin.register(PostModel)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["title"]}
    inlines = [CommentInline]

@admin.register(PrivacyModel)
class PrivacyAdmin(admin.ModelAdmin):
    list_display = ("title", "created")
    prepopulated_fields = {"slug": ["title"]}

@admin.register(EmailModel)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("subject", "from_email", "created")
    readonly_fields = ("subject", "from_email", "name", "phone", "message", "created")

class CustomTaskResultAdmin(TaskResultAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser and request.user.is_technical

class CustomGroupResultAdmin(GroupResultAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser and request.user.is_technical

class CustomClockedScheduleAdmin(ClockedScheduleAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser and request.user.is_technical

class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser and request.user.is_technical

class CustomIntervalScheduleAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser and request.user.is_technical

class CustomCrontabScheduleAdmin(CrontabScheduleAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser and request.user.is_technical

class CustomSolarScheduleAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser and request.user.is_technical

try:
    admin.site.unregister(TaskResult)
    admin.site.unregister(GroupResult)
    admin.site.unregister(PeriodicTask)
    admin.site.unregister(SolarSchedule)
    admin.site.unregister(IntervalSchedule)
    admin.site.unregister(CrontabSchedule)
    admin.site.unregister(ClockedSchedule)
    
except admin.sites.NotRegistered:
    pass

try:
    admin.site.register(TaskResult, CustomTaskResultAdmin)
    admin.site.register(GroupResult, CustomGroupResultAdmin)
    admin.site.register(PeriodicTask, CustomPeriodicTaskAdmin)
    admin.site.register(IntervalSchedule, CustomIntervalScheduleAdmin)
    admin.site.register(CrontabSchedule, CustomCrontabScheduleAdmin)
    admin.site.register(SolarSchedule, CustomSolarScheduleAdmin)
    admin.site.register(ClockedSchedule, CustomClockedScheduleAdmin)

except admin.sites.AlreadyRegistered:
    pass

