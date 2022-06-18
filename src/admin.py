from flask_admin import Admin
from flask_admin.base import AdminIndexView
from flask_admin.contrib.sqla import ModelView

from src.models import (
    Spec,
    Vendor,
    User,
    Callback,
    Auto,
    Ars,
    Registration,
    Request,
    Offer,
    Occupation,
)


class CommonModelView(ModelView):
    column_display_pk = True
    can_set_page_size = True
    can_view_details = True


class SpecModelView(CommonModelView):
    column_sortable_list = [
        'id',
        'title',
    ]
    column_searchable_list = [
        'id',
        'title',
    ]
    column_default_sort = 'id'


class VendorModelView(CommonModelView):
    column_sortable_list = [
        'id',
        'title',
    ]
    column_searchable_list = [
        'id',
        'title',
    ]
    column_default_sort = 'id'


class UserModelView(CommonModelView):
    column_sortable_list = [
        'id',
        'tg_id',
        'tg_message_id',
        'state_id',
        'state_args',
        'phone',
    ]
    column_searchable_list = [
        'id',
        'tg_id',
        'tg_message_id',
        'state_args',
        'phone',
    ]
    column_default_sort = 'id'
    column_filters = [
        'state_id',
    ]


class CallbackModelView(CommonModelView):
    column_sortable_list = [
        'id',
        'data',
    ]
    column_searchable_list = [
        'id',
        'data',
    ]
    column_default_sort = 'id'


class AutoModelView(CommonModelView):
    column_sortable_list = [
        'id',
        'year',
        'fuel',
        'volume',
    ]
    column_searchable_list = [
        'id',
        'volume',
    ]
    column_default_sort = 'id'
    column_filters = [
        'year',
        'fuel',
    ]


class ArsModelView(CommonModelView):
    column_sortable_list = [
        'id',
        'title',
        'description',
        'address',
        'latitude',
        'longitude',
        'picture',
    ]
    column_searchable_list = [
        'id',
        'title',
        'description',
        'address',
        'latitude',
        'longitude',
        'picture',
    ]
    column_default_sort = 'id'


class RegistrationModelView(CommonModelView):
    column_sortable_list = [
        'phone',
    ]
    column_searchable_list = [
        'phone',
    ]


class RequestModelView(CommonModelView):
    column_sortable_list = [
        'id',
        'description',
    ]
    column_searchable_list = [
        'id',
        'description',
    ]
    column_default_sort = 'id'


class OfferModelView(CommonModelView):
    column_sortable_list = [
        'cost_floor',
        'cost_ceil',
        'description',
        'winner',
    ]
    column_searchable_list = [
        'cost_floor',
        'cost_ceil',
        'description',
        'winner',
    ]
    column_filters = [
        'winner',
    ]


class OccupationModelView(CommonModelView):
    column_sortable_list = [
        'id',
        'time',
    ]
    column_searchable_list = [
        'id',
        'time',
    ]
    column_default_sort = 'id'


def setup_admin(flask, session, token):
    flask.config["FLASK_ADMIN_SWATCH"] = "cerulean"

    admin = Admin(flask, index_view=AdminIndexView(url=f"/{token}"))

    admin.add_view(SpecModelView(Spec, session))
    admin.add_view(VendorModelView(Vendor, session))
    admin.add_view(UserModelView(User, session))
    admin.add_view(CallbackModelView(Callback, session))
    admin.add_view(AutoModelView(Auto, session))
    admin.add_view(ArsModelView(Ars, session))
    admin.add_view(RegistrationModelView(Registration, session))
    admin.add_view(RequestModelView(Request, session))
    admin.add_view(OfferModelView(Offer, session))
    admin.add_view(OccupationModelView(Occupation, session))
