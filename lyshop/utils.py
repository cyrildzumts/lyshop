
from django.apps import apps
import secrets
import logging

logger = logging.getLogger(__name__)

PAGINATED_BY = 10

def get_postdata(request):
    return request.POST.copy()


def show_dict_contents(dict_obj, header):
    logger.info(f"Displaying Dict content for {header}")
    for k, v in dict_obj.items():
            logger.debug(f"key : \"{k}\" - value : \"{v}\"")
    logger.info(f"Displaying Dict content for {header} Done")

def get_session(request):
    return request.session

def get_data_from_request(request_dict, key):
    val = None
    if request_dict and key :
        val = request_dict[key]
    
    return val

    
def get_model(app_name=None, modelName=None):
    return apps.get_model(app_name, modelName)

def get_all_fields_from_form(instance):
    """"
    Return names of all available fields from given Form instance.

    :arg instance: Form instance
    :returns list of field names
    :return type: list
    """

    fields = list(instance().base_fields)

    for field in list(instance().declared_fields):
        if field not in fields:
            fields.append(field)
    return fields

def generate_token_16():
    return secrets.token_urlsafe(16)