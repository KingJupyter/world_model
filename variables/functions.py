import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import numpy as np
import logging
import math
from scipy.interpolate import PchipInterpolator

from .models import Variable, TargetYear, YearlyInputValue

logger = logging.getLogger(__name__)

# Calculate the value from variable and input value
def formula(variable, determining_values):
    results = []
    for value in determining_values:
        result = 0
        if variable.base_exp:
            if variable.base_exp < 0:
                result -= math.pow(abs(variable.base_exp), value)
            else:
                result += math.pow(variable.base_exp, value)

        if variable.base_log:
            if variable.base_log < 0:
                result -= math.log(abs(variable.base_log), value)
            else:
                result += math.log(variable.base_log, value)
                
        if variable.linear_coeff:
            result += variable.linear_coeff * value

        if variable.quadratic_coeff:
            if variable.quadratic_coeff < 0:
                result -= variable.quadratic_coeff * math.pow(value, 2)
            result += variable.quadratic_coeff * math.pow(value, 2)
                
        if variable.cubic_coeff:
            result += variable.cubic_coeff * math.pow(value, 3)

        if variable.constant_term:
            result += variable.constant_term

        if variable.standard_deviation:
            # convert deviation to real value
            standard_deviation_value = result * variable.standard_deviation / 100
            result = np.random.normal(loc=result, scale=standard_deviation_value)

        results.append(result)

    return results

# 
def calc_yearly_values(variable, target_year):
    if variable.variable_type == 'Input':   
        try:
            year = []
            value = []
            # calculated input value distribution(current use linear distribution)
            variable_values = YearlyInputValue.objects.filter(variable=variable.id)
            level_in_2023 = variable.level_in_2023
            year.append(2023)
            value.append(level_in_2023)
            for item in variable_values:
                if item.value:
                    year.append(item.year)
                    value.append(item.value)
            spl = PchipInterpolator(np.array(year), np.array(value))
            year_new = np.linspace(2023, target_year, num=target_year-2022)
            input_values = spl(year_new)
            # increase_rate = (target_year_value - level_in_2023) / (target_year - 2024)
            # input_values = []
            # tmp = level_in_2023
            # input_values.append(tmp)
            # for year in range(2024, target_year + 1):
            #     tmp = tmp + increase_rate
            #     input_values.append(tmp)
        except YearlyInputValue.DoesNotExist:
            logger.error(f'Value for {variable.variable_name} in year {target_year} not found')
            return None
        return input_values
    else:
        values = []
        determining_variables = Variable.objects.filter(variable_name=variable.determining_value.variable_name)
        for determining_variable in determining_variables:
            determining_values = calc_yearly_values(determining_variable, target_year=target_year)
            values.append(formula(variable, determining_values))
            # if determining_values is None:
            #     return None
        return np.mean(np.array(values), axis=0).tolist()

def calc_average_value_selected(selected_variable_id, target_year):
    try:
        yearly_calculate_values = []
        title = []
        selected_variable = Variable.objects.get(id=selected_variable_id)
        calculated_variables_of_selected = Variable.objects.filter(variable_name=selected_variable.variable_name)
        
        for variable in calculated_variables_of_selected:
            yearly_calculate_value = calc_yearly_values(variable, target_year=target_year)
            if yearly_calculate_value is None:
                return None
            yearly_calculate_values.append(yearly_calculate_value)
            if len(title) == 0:
                if variable.determining_value:
                    title.append(f'(<b>{variable.variable_name}</b> according to the <b>{variable.determining_value.variable_name}</b>)')
                else:
                    title.append(f'(<b>{variable.variable_name}</b>)')
            else:
                print(title[-1])
                title[-1] = title[-1][:-1]
                title.append(f'& <b>{variable.determining_value.variable_name}</b>)')
            
    except Variable.DoesNotExist:
        logger.error("Variable doesn't exist")
        return None
    average_yearly_values = np.mean(np.array(yearly_calculate_values), axis=0).tolist()

    return [average_yearly_values, title]

def display_graph(first_selected_variable_id, second_selected_variable_id):
    first_variable = Variable.objects.get(id=first_selected_variable_id)
    second_variable = Variable.objects.get(id=second_selected_variable_id)
    try:    
        target_year = TargetYear.objects.get().year
    except TargetYear.DoesNotExist:
        logger.error("Target year doesn't exist")
        return None

    years = []
    for year in range(2024, target_year + 1):
        years.append(year)

    [first_average_yearly_values, title1] = calc_average_value_selected(first_selected_variable_id, target_year)
    [second_average_yearly_values, title2] = calc_average_value_selected(second_selected_variable_id, target_year)

    # Create Plotly figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=years, y=first_average_yearly_values, mode='lines', name=first_variable.variable_name, line_shape='spline', connectgaps=True),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=years, y=second_average_yearly_values, name=second_variable.variable_name, line_shape='spline'),
        secondary_y=True,
    )

    title = title1 + ['VS'] + title2

    # Customize layout
    fig.update_layout(
        title='\n'.join(title),
        xaxis_title='Year',
        yaxis_title='Value',
        template='plotly_dark'
    )

    graph_html = pio.to_html(fig, full_html=False)
    return graph_html