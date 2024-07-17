from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.forms import modelformset_factory
from django.urls import reverse

from .models import Variable, TargetYear, YearlyInputValue
from .forms import TargetYearForm, YearlyInputValueForm

import logging

logger = logging.getLogger(__name__)

def manage_target_year(request):
    try:
        target_year = TargetYear.objects.get()
    except TargetYear.DoesNotExist:
        target_year = None

    if request.method == 'POST':
        form = TargetYearForm(request.POST, instance=target_year)
        if form.is_valid():
            form.save()
            return redirect('input_yearly_values')
    else:
        form = TargetYearForm(instance=target_year)

    return render(request, 'manage_target_year.html', {'form': form})



def input_yearly_values(request):
    YearlyInputValueFormSet = modelformset_factory(YearlyInputValue, form=YearlyInputValueForm, extra=0, can_delete=False)
    variables = Variable.objects.filter(variable_type='Input')

    # Getting or setting the target year
    try:
        target_year = TargetYear.objects.get().year
    except TargetYear.DoesNotExist:
        return redirect('manage_target_year')

    selected_year = request.GET.get('year', target_year)

    if request.method == 'POST':
        formset = YearlyInputValueFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                if instance.value is not None:
                    instance.save()
            formset.save_m2m()
            return HttpResponseRedirect(f"{reverse('input_yearly_values')}?year={selected_year}")
        else:
            print("Formset errors:", formset.errors)
            for form in formset:
                print("Form errors:", form.errors)
    else:
        for variable in variables:
            for year in range(2024, target_year + 1):
                YearlyInputValue.objects.get_or_create(year=year, variable=variable, defaults={'value': None})
        
        formset = YearlyInputValueFormSet(queryset=YearlyInputValue.objects.filter(year=selected_year))

    years = list(range(2024, target_year + 1))
    return render(request, 'input_yearly_values.html', {'formset': formset, 'years': years, 'target_year': target_year, 'selected_year': int(selected_year)})



def variables(request):
    try:
        variables = Variable.objects.all()
        # Use a set to filter out unique names
        unique_variable_names = set()
        unique_variables = []
        for variable in variables:
            if variable.variable_name not in unique_variable_names:
                unique_variable_names.add(variable.variable_name)
                unique_variables.append(variable)
        template = loader.get_template('all_variables.html')
        context = {
            'variables': variables,
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
        print('no')
        # Log the error
        logger.error(f"Error occurred in /variables/ endpoint: {e}")
        return render(request, 'error_template.html', {'error_message': str(e)})

def details(request, id):
    variable = Variable.objects.get(id=id)
    template = loader.get_template('details.html')
    context ={
        'variable': variable
    }
    return HttpResponse(template.render(context, request))

def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render())

def testing(request):
    template = loader.get_template('template.html')
    context = {
        'fruits': ['Apple', 'Banana', 'Cherry'], 
    }
    return HttpResponse(template.render(context, request))

def output(request):
    calculated_variables = Variable.objects.filter(variable_type='Calculated')
    # Use a set to filter out unique names
    unique_variable_names = set()
    unique_variables = []
    for variable in calculated_variables:
        if variable.variable_name not in unique_variable_names:
            unique_variable_names.add(variable.variable_name)
            unique_variables.append(variable)
    template = loader.get_template('output.html')
    context = {
        'variables': unique_variables,
    }
    return HttpResponse(template.render(context, request))

# here x1: input value, y1: calculated value, a: multiplier, x0: level in 2023 of x1, y0: level in 2023 of y1
# def display_graph(x1=3.1, a=5, x0=3, y0=20, sta_dev=1, target=2050):
from .functions import display_graph
def graph(request):
   
    unique_name = set()
    unique_calculated_variables = []
    calculated_variables = Variable.objects.all()
    for variable in calculated_variables:
        if variable.variable_name not in unique_name:
            unique_name.add(variable.variable_name)
            unique_calculated_variables.append(variable)
    first_selected_variable_id = request.GET.get('first_selected_variable')
    second_selected_variable_id = request.GET.get('second_selected_variable')
    
    if not first_selected_variable_id and calculated_variables.exists():
        # If no variable is selected, select the first calculated variable by default
        first_selected_variable_id = unique_calculated_variables[0].id
        second_selected_variable_id = unique_calculated_variables[1].id
    
    result = display_graph(first_selected_variable_id, second_selected_variable_id)
    
    context = {
        'graph_html': result, 
        'calculated_variables': unique_calculated_variables, 
        'first_selected_variable_id': int(first_selected_variable_id),
        'second_selected_variable_id': int(second_selected_variable_id),
    }
    
    return render(request, 'graph.html', context)

