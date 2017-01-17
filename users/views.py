import json
import datetime
import re

from django.shortcuts import render, HttpResponse, force_text, redirect
from django.shortcuts import Http404, HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, ModelFormMixin
from django.views.generic.edit import DeleteView
from django.views.generic import ListView, DetailView, FormView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.core import serializers
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.db.models import BooleanField
from django.forms import ChoiceField
from django.db.models import Q
from django.core.urlresolvers import reverse

from users.forms import *
from users.models import User, list_year, ExtendedPermission
from contrib.models import add_to_breadcrumbs
from borgia.utils import *
from notifications.models import notify


class LinkTokenUserView(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    """
    Link a token id to a User instance and redirect to the workboard of the
    group.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    form_class = LinkTokenUserForm
    template_name = 'users/link_token.html'
    success_url = None
    perm_codename = 'link_token_user'
    lm_active = 'lm_link_token'

    def form_valid(self, form):
        user = User.objects.get(username=form.cleaned_data['username'])
        user.token_id = form.cleaned_data['token_id']
        user.save()
        return super(LinkTokenUserView, self).form_valid(form)


# TODO: jquery is not found on the template
# Due to the jquery of admin ?
class ManageGroupView(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    template_name = 'users/group_manage.html'
    success_url = None
    form_class = ManageGroupForm
    perm_codename = None
    group_updated = None
    lm_active = None

    def dispatch(self, request, *args, **kwargs):
        """
        Check permission.

        This function is at some parts redundant with the mixin GroupPermission
        however you cannot set a perm_codename directly, because it depends
        on the group_name directly.

        :raises: Http404 if the group doesn't exist
        :raises: Http404 if the group updated doesn't exist
        :raises: PermissionDenied if the group doesn't have perm

        Save the group_updated in self.
        """
        try:
            self.group = Group.objects.get(name=kwargs['group_name'])
            self.group_updated = Group.objects.get(pk=kwargs['pk'])
            self.lm_active = 'lm_manage_group_' + kwargs['group_name']
        except ObjectDoesNotExist:
            raise Http404

        if permission_to_manage_group(self.group_updated)[0] not in self.group.permissions.all():
            raise PermissionDenied

        return super(ManageGroupView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Add possible members and permissions to kwargs of the form.

        Possible members are all members, except specials members.
        Possible permissions are all permissions.
        :note:: For the special case of a shop management, two groups exist:
        group of chiefs and group of associates. If the group of associates is
        managed, possible permissions are only permissions of the chiefs group.
        """
        kwargs = super(ManageGroupView, self).get_form_kwargs()

        if self.group_updated.name.startswith('associates-') is True:
            chiefs_group_name = self.group_updated.name.replace('associates', 'chiefs')
            kwargs['possible_permissions'] = ExtendedPermission.objects.filter(
                pk__in=[p.pk for p in Group.objects.get(
                name=chiefs_group_name).permissions.all().exclude(
                pk=permission_to_manage_group(self.group_updated)[0].pk)]
            )

        else:
            kwargs['possible_permissions'] = ExtendedPermission.objects.all()

        kwargs['possible_members'] = User.objects.all().exclude(
            groups=Group.objects.get(name='specials'))
        return kwargs

    def get_initial(self):
        initial = super(ManageGroupView, self).get_initial()
        initial['members'] = User.objects.filter(groups=self.group_updated)
        initial['permissions'] = [
            ExtendedPermission.objects.get(pk=p.pk) for p in self.group_updated.permissions.all()
            ]
        return initial

    def get_context_data(self, **kwargs):
        context = super(ManageGroupView, self).get_context_data(**kwargs)
        context['group_updated_name_display'] = group_name_display(self.group_updated)
        return context

    def form_valid(self, form):
        """
        Update permissions and members of the group updated.
        """
        old_members = User.objects.filter(groups=self.group_updated)
        new_members = form.cleaned_data['members']
        old_permissions = self.group_updated.permissions.all()
        new_permissions = form.cleaned_data['permissions']

        # Modification des membres
        for m in old_members:
            if m not in new_members:
                m.groups.remove(self.group_updated)
                m.save()
        for m in new_members:
            if m not in old_members:
                m.groups.add(self.group_updated)
                m.save()

        # Modification des permissions
        for p in old_permissions:
            if p not in new_permissions:
                self.group_updated.permissions.remove(p)
        for p in new_permissions:
            if p not in old_permissions:
                self.group_updated.permissions.add(p)
        self.group_updated.save()

        return super(ManageGroupView, self).form_valid(form)


class UserCreateView(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    """
    Create a new user and redirect to the workboard of the group.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    form_class = UserCreationCustomForm
    template_name = 'users/create.html'
    success_url = None
    perm_codename = 'add_user'
    lm_active = 'lm_user_create'

    def form_valid(self, form):
        user = User.objects.create(username=form.cleaned_data['username'],
                                   first_name=form.cleaned_data['first_name'],
                                   last_name=form.cleaned_data['last_name'],
                                   email=form.cleaned_data['email'],
                                   surname=form.cleaned_data['surname'],
                                   family=form.cleaned_data['family'],
                                   campus=form.cleaned_data['campus'],
                                   year=form.cleaned_data['year'])
        user.set_password(form.cleaned_data['password'])
        user.save()

        if form.cleaned_data['honnor_member'] is True:
            user.groups.add(Group.objects.get(pk=8))
        else:
            user.groups.add(Group.objects.get(pk=7))
        user.save()

        return super(UserCreateView, self).form_valid(form)

    def get_initial(self):
        initial = super(UserCreateView, self).get_initial()
        initial['campus'] = 'Me'
        initial['year'] = 2014
        return initial


class UserRetrieveView(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    Retrieve a User instance.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    template_name = 'users/retrieve.html'
    perm_codename = 'retrieve_user'

    def get(self, request, *args, **kwargs):

        if request.user.has_perm('users.retrieve_user') is False and int(kwargs['pk']) != request.user.pk:
            raise PermissionDenied

        context = self.get_context_data(**kwargs)
        context['object'] = User.objects.get(pk=self.kwargs['pk'])
        return render(request, self.template_name, context=context)


# Used in the pg mode to modify itself
class UserUpdateView(FormView):
    form_class = UserUpdateForm
    template_name = 'users/update.html'
    success_url = '/users/profile/'
    modified = False

    def get(self, request, *args, **kwargs):
        try:
            if int(self.kwargs['pk']) != request.user.pk:
                raise PermissionDenied
        except ValueError:
            raise PermissionDenied

        add_to_breadcrumbs(request, 'Modification user')
        return super(UserUpdateView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UserUpdateView, self).get_form_kwargs()
        kwargs['user_modified'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.request.POST.get('next', self.success_url))
        return context

    def get_success_url(self):
        if self.modified is True:
            # Notifications
            notify(self.request, 'user_updating', self.request.user, None)
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))

    def get_initial(self):
        initial = super(UserUpdateView, self).get_initial()
        initial['email'] = self.request.user.email
        initial['phone'] = self.request.user.phone
        initial['avatar'] = self.request.user.avatar
        return initial

    def form_valid(self, form):

        if getattr(self.request.user, 'email') != form.cleaned_data['email']:
            setattr(self.request.user, 'email', form.cleaned_data['email'])
            self.modified = True
        if getattr(self.request.user, 'phone') != form.cleaned_data['phone']:
            setattr(self.request.user, 'phone', form.cleaned_data['phone'])
            self.modified = True
        if getattr(self.request.user, 'avatar') != form.cleaned_data['avatar']:
            if self.request.user.avatar:
                self.request.user.avatar.delete(True)
            if form.cleaned_data['avatar'] is not False:
                setattr(self.request.user, 'avatar', form.cleaned_data['avatar'])
            self.modified = True

        if self.modified is True:
            self.request.user.save()

        return super(UserUpdateView, self).form_valid(form)


class UserUpdateAdminView(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    """
    Update an user and redirect to the workboard of the group.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    model = User
    form_class = UserUpdateAdminForm
    template_name = 'users/update_admin.html'
    success_url = None
    perm_codename = 'change_user'
    modified = False

    def get_form_kwargs(self):
        kwargs = super(UserUpdateAdminView, self).get_form_kwargs()
        kwargs['user_modified'] = User.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UserUpdateAdminView, self).get_context_data(**kwargs)
        context['user_modified'] = User.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super(UserUpdateAdminView, self).get_initial()
        user_modified = User.objects.get(pk=self.kwargs['pk'])
        for k in UserUpdateAdminForm(user_modified=user_modified).fields.keys():
            initial[k] = getattr(user_modified, k)
        return initial

    def form_valid(self, form):
        user_modified = User.objects.get(pk=self.kwargs['pk'])
        for k in form.fields.keys():
            if form.cleaned_data[k] != getattr(user_modified, k):
                self.modified = True
                setattr(user_modified, k, form.cleaned_data[k])
        user_modified.save()
        return super(UserUpdateAdminView, self).form_valid(form)


class UserDeactivateView(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    Deactivate an user and redirect to the workboard of the group.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    template_name = 'users/deactivate.html'
    success_url = None
    perm_codename = 'delete_user'

    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        context = self.get_context_data(**kwargs)
        context['object'] = user
        return render(request, 'users/deactivate.html', context=context)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        if user.is_active is True:
            user.is_active = False
        else:
            user.is_active = True
        user.save()

        return redirect(force_text(self.success_url))


class UserListView(GroupPermissionMixin, View, GroupLateralMenuMixin):
    """
    List User instances.

    :param kwargs['group_name']: name of the group used.
    :param self.perm_codename: codename of the permission checked.
    """
    perm_codename = 'list_user'
    template_name = 'users/user_list.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['list_year'] = list_year()
        return render(request, self.template_name, context=context)


# TODO: obsolète
def workboard_presidents(request):

    group_vices_presidents_vie_interne_pk = 10
    group_tresoriers_pk = 2
    group_presidents_pk = 1
    group_gadzarts_pk = 7
    group_membres_honneurs_pk = 8

    add_to_breadcrumbs(request, 'Workboard présidents')
    return render(request, 'users/workboard_presidents.html', locals())

# TODO: obsolète
def workboard_vices_presidents_vie_interne(request):

    group_chefs_gestionnaires_foyer_pk = 3
    group_chefs_gestionnaires_auberge_pk = 5
    group_chefs_gestionnaires_cvis_pk = 11
    group_chefs_gestionnaires_bkars_pk = 13

    add_to_breadcrumbs(request, 'Workboard vices présidents')
    return render(request, 'users/workboard_vices_presidents_vie_interne.html', locals())

def username_from_username_part(request):
    data = []

    try:
        key = request.GET.get('keywords')

        # Fam'ss en entier
        where_search = User.objects.filter(family=key).order_by('-year')

        if len(key) > 2:
            # Nom de famille, début ou entier à partir de 3 caractères
            where_search = where_search | User.objects.filter(last_name__startswith=key)
            # Prénom, début ou entier à partir de 3 caractères
            where_search = where_search | User.objects.filter(first_name__startswith=key)
            # Buque, début ou entier à partir de 3 caractères
            where_search = where_search | User.objects.filter(surname__startswith=key)

        # Suppression des doublons
        where_search = where_search.distinct()

        for e in where_search:
            data.append(e.username)

    except KeyError:
        pass

    return HttpResponse(json.dumps(data))

# TODO: obsolète
def profile_view(request):
    add_to_breadcrumbs(request, 'Profil')
    return render(request, 'users/profile.html', locals())

def data_from_username(self):
    try:
        user = User.objects.get(username=self.GET.get('username'))
        data = {
            'surname': user.surname,
            'balance': str(user.balance),
            'family': user.family}
        return HttpResponse(json.dumps(data))
    except ObjectDoesNotExist:
        return HttpResponse()
