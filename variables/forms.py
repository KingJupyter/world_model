from django import forms
from .models import TargetYear, Variable, YearlyInputValue

class TargetYearForm(forms.ModelForm):
    class Meta:
        model = TargetYear
        fields = ['year']

class YearlyInputValueForm(forms.ModelForm):
    class Meta:
        model = YearlyInputValue
        fields = ['value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'variable') and self.instance.variable:
            self.fields['value'].label = self.instance.variable.variable_name
        else:
            self.fields['value'].label = 'Value'