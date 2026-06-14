from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    consent = forms.BooleanField(
        required=True,
        error_messages={'required': 'Без согласия на обработку персональных данных оформить заказ нельзя.'},
    )

    # Honeypot-ловушка от спам-ботов: поле скрыто от людей (CSS в шаблоне), они его не заполняют.
    # Бот, заполняющий все поля формы, выдаёт себя — заказ отклоняется.
    website = forms.CharField(
        required=False, label='',
        widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}),
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'contact_method', 'comment']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 'placeholder': 'Как к вам обращаться',
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '(968) 123-45-67',
                'inputmode': 'tel',
                'autocomplete': 'tel',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Комментарий к заказу (необязательно)',
            }),
        }

    def __init__(self, *args, allowed_methods=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Телефон нужен для перезвона/звонка и просто полезен — делаем обязательным.
        self.fields['customer_phone'].required = True
        self.fields['customer_name'].required = True

        if allowed_methods is not None:
            choices = [c for c in Order.ContactMethod.choices if c[0] in allowed_methods]
        else:
            choices = list(Order.ContactMethod.choices)
        self.fields['contact_method'].choices = choices
        self.fields['contact_method'].widget = forms.RadioSelect(choices=choices)
        if choices:
            self.fields['contact_method'].initial = choices[0][0]

    def clean_website(self):
        # Заполненная ловушка = бот.
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Спам-защита: поле должно оставаться пустым.')
        return ''

    def clean_customer_phone(self):
        """В шаблоне +7 показан статичным префиксом, поэтому пользователь вводит
        только остаток. Добавляем +7, если номер не начинается с '+'."""
        value = (self.cleaned_data.get('customer_phone') or '').strip()
        if value and not value.startswith('+'):
            value = '+7 ' + value
        return value
