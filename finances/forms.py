#-*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
from django.forms import ModelForm
from django.forms.widgets import PasswordInput
from django.core.exceptions import ObjectDoesNotExist

from users.models import User
from finances.models import Cheque, Cash, Lydia, BankAccount


class TransfertCreateForm(forms.Form):
    recipient = forms.CharField(label='Receveur', max_length=255)
    amount = forms.IntegerField(label='Montant')

    def __init__(self, **kwargs):
        self.request = kwargs.pop('request')
        super(TransfertCreateForm, self).__init__(**kwargs)

    def clean(self):
        cleaned_data = super(TransfertCreateForm, self).clean()
        recipient = cleaned_data['recipient']
        try:
            User.objects.get(username=recipient)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Cette personne n\'existe pas')

        if User.objects.get(username=recipient) == self.request.user:
            raise forms.ValidationError('Transfert vers soi-même impossible')


class ChequeCreateForm(ModelForm):
    class Meta:
        model = Cheque
        fields = ['amount', 'is_cashed', 'signature_date', 'cheque_number', 'sender', 'bank_account', 'recipient']

    bank_account = forms.ModelChoiceField(label='Compte en banque', queryset=BankAccount.objects.all())


class CreationLydiaForm(ModelForm):
    class Meta:
        model = Lydia
        fields = ['sender_user_id', 'recipient_user_id', 'date_operation', 'id_from_lydia', 'amount',
                  'banked', 'date_banked']

    sender_user_id = forms.ModelChoiceField(label='Impulseur', queryset=User.objects.all().order_by('last_name'))
    recipient_user_id = forms.ModelChoiceField(label='Destinataire', queryset=User.objects.all().order_by('last_name'))


class CreationCashForm(ModelForm):
    class Meta:
        model = Cash
        fields = ['sender', 'recipient', 'amount']

    giver = forms.ModelChoiceField(label='Donnateur', queryset=User.objects.all().order_by('last_name'))
    recipient = forms.ModelChoiceField(label='Receveur', queryset=User.objects.all().order_by('last_name'))


class SupplyUnitedForm(forms.Form):

    # Général
    # Type
    type = forms.ChoiceField(label='Type', choices=(('cash', 'Espèces'), ('cheque', 'Chèque'), ('lydia', 'Lydia')))
    # Informations générales
    amount = forms.FloatField(label='Montant (€)')
    sender = forms.CharField(label='Payeur')
    unique_number = forms.CharField(label='Numéro unique', required=False)  # Inutile pour Cash
    signature_date = forms.DateField(label='Date de signature', required=False)  # Inutile pour Cash
    bank_account = forms.ModelChoiceField(label='Compte bancaire', queryset=BankAccount.objects.all(),
                                          required=False)  # Inutile pour Cash et Lydia

    # Gestionnaire - opérateur
    operator_username = forms.CharField(label='Gestionnaire')
    operator_password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    def clean(self):

        cleaned_data = super(SupplyUnitedForm, self).clean()
        operator_username = cleaned_data['operator_username']
        operator_password = cleaned_data['operator_password']

        # Essaye d'authentification seulement si les deux champs sont valides
        if operator_password and operator_password:
            # Cas d'échec d'authentification
            if authenticate(username=operator_username, password=operator_password) is None:
                raise forms.ValidationError('Echec d\'authentification')
            elif authenticate(username=operator_username, password=operator_password).has_perm('users.supply_account') is False:
                raise forms.ValidationError('Erreur de permission')
        return super(SupplyUnitedForm, self).clean()


class SupplyChequeForm(forms.Form):

    # Chèque
    amount = forms.FloatField(label='Montant')
    sender = forms.ModelChoiceField(label='Payeur', queryset=User.objects.all())
    bank_account = forms.ModelChoiceField(label='Compte bancaire', queryset=BankAccount.objects.all())
    cheque_number = forms.CharField(label='Numéro unique', max_length=7)
    signature_date = forms.DateField(label='Date de signature')

    # Gestionnaire - opérateur
    operator_username = forms.CharField(label='Gestionnaire')
    operator_password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    def clean(self):

        cleaned_data = super(SupplyChequeForm, self).clean()
        operator_username = cleaned_data['operator_username']
        operator_password = cleaned_data['operator_password']

        # Essaye d'authentification seulement si les deux champs sont valides
        if operator_password and operator_password:
            # Cas d'échec d'authentification
            if authenticate(username=operator_username, password=operator_password) is None:
                raise forms.ValidationError('Echec d\'authentification')
        return super(SupplyChequeForm, self).clean()


class SupplyCashForm(forms.Form):

    # Cash
    amount = forms.FloatField(label='Montant')
    sender = forms.ModelChoiceField(label='Payeur', queryset=User.objects.all())

    # Gestionnaire - opérateur
    operator_username = forms.CharField(label='Gestionnaire')
    operator_password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    def clean(self):

        cleaned_data = super(SupplyCashForm, self).clean()
        operator_username = cleaned_data['operator_username']
        operator_password = cleaned_data['operator_password']

        # Essaye d'authentification seulement si les deux champs sont valides
        if operator_password and operator_password:
            # Cas d'échec d'authentification
            if authenticate(username=operator_username, password=operator_password) is None:
                raise forms.ValidationError('Echec d\'authentification')
        return super(SupplyCashForm, self).clean()


class SupplyLydiaForm(forms.Form):

    # Lydia
    amount = forms.FloatField(label='Montant')
    sender = forms.ModelChoiceField(label='Payeur', queryset=User.objects.all())
    id_from_lydia = forms.CharField(label='Numéro unique Lydia')
    date_operation = forms.DateField(label='Date d\'opération')

    # Gestionnaire - opérateur
    operator_username = forms.CharField(label='Gestionnaire')
    operator_password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    def clean(self):

        cleaned_data = super(SupplyLydiaForm, self).clean()
        operator_username = cleaned_data['operator_username']
        operator_password = cleaned_data['operator_password']

        # Essaye d'authentification seulement si les deux champs sont valides
        if operator_password and operator_password:
            # Cas d'échec d'authentification
            if authenticate(username=operator_username, password=operator_password) is None:
                raise forms.ValidationError('Echec d\'authentification')
        return super(SupplyLydiaForm, self).clean()