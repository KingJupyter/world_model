from django.db import models
from django.core.exceptions import ValidationError


class Variable(models.Model):
    INPUT = 'Input'
    CALCULATED = 'Calculated'
    VARIABLE_TYPE_CHOICES = [
        (INPUT, 'Input'),
        (CALCULATED, 'Calculated'),
    ]

    variable_name = models.CharField(max_length=255)
    variable_type = models.CharField(max_length=10, choices=VARIABLE_TYPE_CHOICES)
    variable_options = models.TextField(null=True, blank=True)
    variable_definition = models.TextField(null=True, blank=True)
    level_in_2023 = models.FloatField(null=True, blank=True)
    units = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    determining_value = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='determined_by'
    )
    linear_coeff = models.FloatField(null=True, blank=True)
    quadratic_coeff = models.FloatField(null=True, blank=True)
    cubic_coeff = models.FloatField(null=True, blank=True)
    log_coeff = models.FloatField(null=True, blank=True)
    exp_coeff = models.FloatField(null=True, blank=True)
    exp_rate_coeff = models.FloatField(null=True, blank=True)
    standard_deviation = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.variable_name}"
    
    def clean(self):
        super().clean()

        # Custom validation logic
        if self.variable_type == self.INPUT:
            if self.determining_value is not None or self.exp_coeff is not None or self.log_coeff is not None or self.linear_coeff is not None or self.quadratic_coeff is not None or self.cubic_coeff is not None or self.exp_rate_coeff is not None or self.standard_deviation is not None:
                raise ValidationError({
                    'determining_value': 'Determining value must be null for Input type.',
                    'exp_coeff': 'Base exp must be null for Input type.',
                    'log_coeff': 'Base log must be null for Input type.',
                    'linear_coeff': 'Linear coefficient must be null for Input type.',
                    'quadratic_coeff': 'Quadratic coefficient must be null for Input type.',
                    'cubic_coeff': 'Cubic coefficient must be null for Input type.',
                    'exp_rate_coeff': 'Constant coefficient must be null for Input type.',
                    'standard_deviation': 'Standard coefficient must be null for Input type.',
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class TargetYear(models.Model):
    year = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.year)
    
class YearlyInputValue(models.Model):
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE, related_name='yearly_input_values')
    year = models.IntegerField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('variable', 'year')

    def __str__(self):
        return f"{self.year} - {self.variable.variable_name}: {self.value}"