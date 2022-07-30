from django import forms
from django.forms import ModelForm
from tgbot.models import Mailing, User,Group, MessageType, File


class MakeGroupForm(ModelForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Group
        fields = '__all__'


class BroadcastForm(forms.Form):
    mailing_name = forms.CharField(
        label='Название рассылки',
        widget=forms.TextInput
    )
    message_text = forms.CharField(
        label='Текст сообщения',
        widget=forms.Textarea
    )
    message_type = forms.ChoiceField(
        label='Тип сообщения',
        choices=MessageType.choices
    )
    files = forms.ModelMultipleChoiceField(
        label='Выбирете существующие файлы для рассылки',
        queryset=File.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    file = forms.FileField(
        label='Загрузите файл для рассылки',
    )
    _users_id = forms.CharField(widget=forms.MultipleHiddenInput)        

