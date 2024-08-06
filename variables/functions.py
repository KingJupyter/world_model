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
    results = [variable.level_in_2023]
    
    for index in range(0, len(determining_values) - 1):
        multiplation_rate = 1
        if determining_values[index + 1] >= determining_values[index]:
            rate = (determining_values[index + 1] - determining_values[index]) / determining_values[index]
        else:
            rate = ((determining_values[index] - (determining_values[index + 1])) / determining_values[index + 1])
        print('rate-->', rate)

        if variable.linear_coeff:
            multiplation_rate += variable.linear_coeff * rate

        if variable.quadratic_coeff:
            multiplation_rate += variable.quadratic_coeff * math.pow(rate, 2)

        if variable.cubic_coeff:
            multiplation_rate += variable.cubic_coeff * math.pow(rate, 3)

        if variable.log_coeff:
            multiplation_rate += variable.log_coeff * math.log(rate + 1)

        if variable.exp_coeff and variable.exp_rate_coeff:
            multiplation_rate += variable.exp_coeff * (math.exp(variable.exp_rate_coeff * rate) - 1)

        if determining_values[index + 1] >= determining_values[index] and multiplation_rate >= 0:
            result = multiplation_rate * results[-1]
        else:
            result = abs(results[-1] / multiplation_rate)
            
        if variable.standard_deviation:
            standard_deviation_value = result * variable.standard_deviation / 100
            result = np.random.normal(loc=result, scale=standard_deviation_value)

        results.append(result)

    print('results--->', results)
    return results

def calc_yearly_values(variable, target_year):
    if variable.variable_type == 'Input':   
        try:
            year = [2023]
            value = [variable.level_in_2023]
            variable_values = YearlyInputValue.objects.filter(variable=variable.id)

            for item in variable_values:
                if item.value:
                    year.append(item.year)
                    value.append(item.value)
            spl = PchipInterpolator(np.array(year), np.array(value))
            year_new = np.linspace(2023, target_year, num=target_year-2022)
            input_values = spl(year_new)
            return input_values
        except YearlyInputValue.DoesNotExist:
            logger.error(f'Value for {variable.variable_name} in year {target_year} not found')
            return None
    else:
        values = []
        determining_variables = Variable.objects.filter(variable_name=variable.determining_value.variable_name)
        for determining_variable in determining_variables:
            determining_values = calc_yearly_values(determining_variable, target_year=target_year)
            if determining_values is None:
                return None
            values.append(formula(variable, determining_values))

        return np.mean(np.array(values), axis=0).tolist()

def run_simulations(selected_variable_id, target_year, num_simulations=100):
    try:
        all_simulated_values = []
        title = []
        selected_variable = Variable.objects.get(id=selected_variable_id)
        calculated_variables_of_selected = Variable.objects.filter(variable_name=selected_variable.variable_name)
        
        for variable in calculated_variables_of_selected:
            yearly_calculate_value = calc_yearly_values(variable, target_year=target_year)
            if yearly_calculate_value is None:
                return None
            if len(title) == 0:
                if variable.determining_value:
                    title.append(f'(<b>{variable.variable_name}</b> according to the <b>{variable.determining_value.variable_name}</b>)')
                else:
                    title.append(f'(<b>{variable.variable_name}</b>)')
            else:
                print(title[-1])
                title[-1] = title[-1][:-1]
                title.append(f'& <b>{variable.determining_value.variable_name}</b>)')

        for index in range(num_simulations):
            print(index + 1)
            simulation_results = []
            for variable in calculated_variables_of_selected:
                yearly_values = calc_yearly_values(variable, target_year)
                if yearly_values is None:
                    continue
                simulation_results.append(yearly_values)
            if simulation_results:
                all_simulated_values.append(np.mean(np.array(simulation_results), axis=0))

        all_simulated_values = np.array(all_simulated_values)
        mean_values = np.mean(all_simulated_values, axis=0)
        std_dev_values = np.std(all_simulated_values, axis=0)
        print('std dev values-->', std_dev_values)
        return mean_values, std_dev_values, title

    except Variable.DoesNotExist:
        logger.error("Variable doesn't exist")
        return None

def display_graph(first_selected_variable_id, second_selected_variable_id):
    print('started----------------------------------------------------------------------------------------!!!!!!')
    first_variable = Variable.objects.get(id=first_selected_variable_id)
    second_variable = Variable.objects.get(id=second_selected_variable_id)
    try:    
        target_year = TargetYear.objects.get().year
    except TargetYear.DoesNotExist:
        logger.error("Target year doesn't exist")
        return None

    years = list(range(2023, target_year + 1))

    first_mean, first_std_dev, title1 = run_simulations(first_selected_variable_id, target_year)
    second_mean, second_std_dev ,title2 = run_simulations(second_selected_variable_id, target_year)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=years, y=first_mean, name=first_variable.variable_name, line_shape='spline'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=years, y=first_mean + first_std_dev, name=f'{first_variable.variable_name} +1 Std Dev', line_shape='spline',
        line=dict(dash='dash')), secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=years, y=first_mean - first_std_dev, name=f'{first_variable.variable_name} -1 Std Dev', line_shape='spline',
        line=dict(dash='dash')), secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=years, y=second_mean, name=second_variable.variable_name, line_shape='spline'),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(x=years, y=second_mean + second_std_dev, name=f'{second_variable.variable_name} +1 Std Dev', line_shape='spline',
        line=dict(dash='dash')), secondary_y=True
    )
    fig.add_trace(
        go.Scatter(x=years, y=second_mean - second_std_dev, name=f'{second_variable.variable_name} -1 Std Dev', line_shape='spline',
        line=dict(dash='dash')), secondary_y=True
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
    print('Done----------------------------------------------------------------------!!!!!!!')
    return graph_html
