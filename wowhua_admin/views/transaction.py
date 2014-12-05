from flask.ext.babelex import lazy_gettext as _

from wowhua_db.common.constants import TRANSACTION_TYPES
from wowhua_admin.views import SafeView


class TransactionView(SafeView):
    column_filters = ('id', 'user_id', 'type')
    column_default_sort = ('created', True)
    column_labels = dict(
        id=_('ID'),
        user_id=_('User Id'),
        amount=_('Amount'),
        type=_('Transaction Type'),
        description=_('Description'),
        cancel_trans_id=_('Cancel Trans Id'),
        created=_('Created Time'),
    )
    column_list = ('id', 'user_id', 'amount', 'type', 'description',
                   'cancel_trans_id', 'created' )

    def type_formatter(self, context, model, name):
        type = getattr(model, name)
        if type is not None:
            if type in TRANSACTION_TYPES:
                return str(type) + '.' + type.name
            else:
                return str(type)
        else:
            return ""


    column_formatters = dict(
        created=SafeView._time_formatter,
        type=type_formatter,
    )
