from django.contrib import admin
from .models import Variable, TargetYear, YearlyInputValue

class VariableAdmin(admin.ModelAdmin):
    list_display = (
        "variable_name", "variable_type", "variable_options", 
        "variable_definition", 'level_in_2023', 'units', 
        'source', 'determining_value',
        'base_exp', 'base_log', 'linear_coeff', 'quadratic_coeff',
        'cubic_coeff', 'constant_term', 'standard_deviation'
    )
    search_fields = ("variable_name", "variable_type", "source")
    list_filter = ("variable_type", "source")
    fieldsets = (
        (None, {
            'fields': ('variable_name', 'variable_type', 'variable_options', 'variable_definition')
        }),
        ('Details', {
            'fields': (
                'level_in_2023', 'units', 'source', 'determining_value', 
                'base_exp', 'base_log', 'linear_coeff', 'quadratic_coeff',
                'cubic_coeff', 'constant_term', 'standard_deviation'
            )
        }),
    )

class TargetYearAdmin(admin.ModelAdmin):
    list_display = ('year',)
    list_filter = ('year',)

class YearlyInputValueAdmin(admin.ModelAdmin):
    list_display = ('variable', 'year', 'value',)
    list_filter = ('variable', 'year',)

admin.site.register(Variable, VariableAdmin)
admin.site.register(TargetYear, TargetYearAdmin)
admin.site.register(YearlyInputValue, YearlyInputValueAdmin)