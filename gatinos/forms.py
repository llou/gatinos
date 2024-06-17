from django.forms.renderers import DjangoTemplates as DjangoTemplatesRenderer


class FormRenderer(DjangoTemplatesRenderer):
    form_template_name = "templates/forms/div.html"
    field_template_name = "templates/forms/field.html"
