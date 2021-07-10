from django.utils.translation import gettext_lazy as _
from lyshop import utils
import datetime
import re


SHORT_DESCRIPTION_MAX_SIZE = 164
DESCRIPTION_MAX_SIZE = 300
CATEGORY_DESCRIPTION_MAX_SIZE = 512

TOP_VIEWS_MAX = 10

CACHE_CATEGORY_PATH_PREFIX = 'category.path.'
CACHE_CATEGORY_DESCENDANTS_PREFIX = 'category.descendants.'
CACHE_CATEGORY_PRODUCTS_PREFIX = 'category.products.'
CACHE_PRODUCT_ATTRIBUTES_PREFIX = 'product.attrs.'
CACHE_CATEGORY_MAPS_PREFIX = "category.map."
CACHE_CATEGORY_ALL_PREFIX = "category.categories.all"
CACHE_CATEGORY_CHILDREN_PREFIX = "category.children."
CACHE_CATEGORY_ROOT_CHILDREN_KEY = CACHE_CATEGORY_CHILDREN_PREFIX + "root"
CACHE_PRODUCT_TYPES_PREFIX = "product_type."
CACHE_PRODUCT_TYPES_ALL_KEY = CACHE_PRODUCT_TYPES_PREFIX + "all"
CACHE_NEWS_PREFIX = "news."
CACHE_NEWS_ALL_KEY = CACHE_NEWS_PREFIX + "all"
CACHE_BRAND_PREFIX = "brand."
CACHE_BRAND_PRODUCT_PREFIX = CACHE_BRAND_PREFIX + "products"
CACHE_BRAND_ALL_KEY = CACHE_BRAND_PREFIX + "all"



GENDER_MEN          = 1
GENDER_WOMEN        = 2
GENDER_BABY_GIRL    = 3
GENDER_BABY_BOY     = 4
GENDER_GIRL         = 5
GENDER_BOY          = 6
GENDER_NO_GENDER    = 7

ATTRIBUTE_TYPE_STRING = 1
ATTRIBUTE_TYPE_INTEGER = 2
ATTRIBUTE_TYPE_DECIMAL = 3
ATTRIBUTE_TYPE_DATE   = 4
ATTRIBUTE_TYPE_DATETIME = 5
ATTRIBUTE_TYPE_DEFAULT = ATTRIBUTE_TYPE_STRING

PRODUCT_ACTION_DELETE = 0
PRODUCT_ACTION_ACTIVATE = 1
PRODUCT_ACTION_DEACTIVATE = 2
PRODUCT_ACTION_SALE_ON = 3
PRODUCT_ACTION_SALE_OFF = 4



CHILDREN = (
    (GENDER_BOY, 'BOY'),
    (GENDER_GIRL, 'GIRL')
)

BABY = (
    (GENDER_BABY_BOY, 'BABY BOY'),
    (GENDER_BABY_GIRL, 'BABY GIRL')
)

GENDER = (
        (GENDER_MEN, 'MEN'),
        (GENDER_WOMEN, 'WOMEN'),
        (GENDER_BABY_GIRL, 'BABY GIRL'),
        (GENDER_BABY_BOY, 'BABY BOY'),
        (GENDER_GIRL, 'GIRL'),
        (GENDER_BOY, 'BOY'),
        (GENDER_NO_GENDER, 'NO GENDER')
    )



ATTRIBUTE_TYPE = (
    (ATTRIBUTE_TYPE_STRING, 'STRING'),
    (ATTRIBUTE_TYPE_INTEGER, 'INTEGER'),
    (ATTRIBUTE_TYPE_DECIMAL, 'DECIMAL'),
    (ATTRIBUTE_TYPE_DATE, 'DATE'),
    (ATTRIBUTE_TYPE_DATETIME, 'DATETIME')
)

ATTRIBUTE_TYPE_MAPPING = {
    ATTRIBUTE_TYPE_STRING : str,
    ATTRIBUTE_TYPE_INTEGER : int,
    ATTRIBUTE_TYPE_DECIMAL : float,
    ATTRIBUTE_TYPE_DATETIME : datetime.datetime,
    ATTRIBUTE_TYPE_DATE : datetime.date
}

PRODUCT_ACTIONS = (
    (PRODUCT_ACTION_DELETE, 'DELETE'),
    (PRODUCT_ACTION_ACTIVATE, 'ACTIVATE'),
    (PRODUCT_ACTION_DEACTIVATE, 'DEACTIVATE'),
    (PRODUCT_ACTION_SALE_ON, 'SALE'),
    (PRODUCT_ACTION_SALE_OFF, 'SALE OFF'),
)

# Category Page Title:
CATEGORY_SHOES_PAGE_TITLE           = _("Shoes | Ballerinas, Loafer, Pumps | LYSHOP")
CATEGORY_BAGS_PAGE_TITLE            = _("Bags | Handbags for women | Online Shopping | LYSHOP")
CATEGORY_PARFUMS_PAGE_TITLE         = _("Perfumes | Perfumes for Men and Women | LYSHOP")
CATEGORY_ELECTRONICS_PAGE_TITLE     = _("Electronics | Smartphones | LYSHOP")
CATEGORY_MODE_PAGE_TITLE            = _("Fashion | Women and Men | LYSHOP")
CATALOG_HOME_PAGE_TITLE             = _("Catalog | Fashion for all | LYSHOP")
CATEGORY_EDP_PAGE_TITLE             = _("Eaux De Parfums | Buy online | LYSHOP")
CATEGORY_EDT_PAGE_TITLE             = _("Eaux De Toilettes | Buy online | LYSHOP")
CATEGORY_SMARTPHONE_PAGE_TITLE      = _("Smartphone | Buy online | LYSHOP")
CATEGORY_BALLERINE_PAGE_TITLE       = _("Ballerines | Flat shoes | Buy online | LYSHOP")
CATEGORY_ESCARPIN_PAGE_TITLE        = _("Escarpins  | High heels shoes | Buy online | LYSHOP")
CATEGORY_MOCASSIN_PAGE_TITLE        = _("Mocassins | Buy online | LYSHOP")
CATEGORY_SNEAKER_PAGE_TITLE         = _("Sneakers | Sport shoes | Buy online | LYSHOP")

CATEGORY_SHOES = 0
CATEGORY_BAGS = 1
CATEGORY_PARFUMS = 2
CATEGORY_ELECTRONICS = 3
CATEGORY_MODE = 4
CATEGORY_EDP = 5
CATEGORY_EDT = 6
CATEGORY_SMARTPHONE = 7
CATEGORY_BALLERINE = 8
CATEGORY_ESCARPIN   = 9
CATEGORY_MOCASSIN = 10
CATEGORY_SNEAKER = 11


CATEGORIES = (
    (CATEGORY_SHOES, CATEGORY_SHOES_PAGE_TITLE),
    (CATEGORY_BAGS, CATEGORY_BAGS_PAGE_TITLE),
    (CATEGORY_PARFUMS, CATEGORY_PARFUMS_PAGE_TITLE),
    (CATEGORY_ELECTRONICS, CATEGORY_ELECTRONICS_PAGE_TITLE),
    (CATEGORY_MODE, CATEGORY_MODE_PAGE_TITLE),
    (CATEGORY_EDP, CATEGORY_EDP_PAGE_TITLE),
    (CATEGORY_EDT, CATEGORY_EDT_PAGE_TITLE),
    (CATEGORY_SMARTPHONE, CATEGORY_SMARTPHONE_PAGE_TITLE),
    (CATEGORY_BALLERINE, CATEGORY_BALLERINE_PAGE_TITLE),
    (CATEGORY_ESCARPIN, CATEGORY_ESCARPIN_PAGE_TITLE),
    (CATEGORY_MOCASSIN, CATEGORY_MOCASSIN_PAGE_TITLE),
    (CATEGORY_SNEAKER, CATEGORY_SNEAKER_PAGE_TITLE),
)




COMMISSION_DEFAULT = 0.03
COMMISSION_MAX_DIGITS = 7
COMMISSION_DECIMAL_PLACES = 5

DEFAULT_PRIMARY_ATTRIBUTES = ['size', 'capacity', 'color']

INTEGER_PATTERN_REGEX               = re.compile(r'^[0-9]+$')
LIST_FILTER_PATTERN                 = re.compile(r'^\w+([,;]\w+)*$')
INTEGER_RANGE_FILTER_PATTERN        = re.compile(r'(?P<START>\d+)?(?:-{1,2})(?P<END>\d+)?')

CATEGORY_CHILD_TO_ROOT_QUERY = """
WITH RECURSIVE CTE_CAT(id, name, parent_id, parents) AS (
SELECT id,name, parent_id, array[parent_id] FROM catalog_category 
WHERE id=%s
UNION
SELECT CTE_CAT.id, CTE_CAT.name, c.parent_id, CTE_CAT.parents||c.parent_id 
FROM CTE_CAT
JOIN catalog_category c ON CTE_CAT.parent_id = c.id
)
SELECT distinct on (id) id,name, parents
FROM CTE_CAT 
ORDER BY id, array_length(parents, 1) desc;
"""

### GET ANCESTOR :
CATEGORY_ANCESTOR = """
 WITH RECURSIVE
    CTE AS (
        SELECT 
            *
        FROM
            catalog_category
        WHERE
            id = %s
        UNION ALL
        SELECT
            c.*
        FROM
            catalog_category c
                JOIN CTE  ON c.id = CTE.parent_id
        WHERE
            CTE.parent_id IS NOT NULL
    )
    SELECT * FROM CTE;
"""

CATEGORY_ROOT_TO_CHILD_QUERY = """
WITH RECURSIVE CTE_CAT(id, name, parent_id, parents) AS (
SELECT id,name, parent_id, array[parent_id] FROM catalog_category 
WHERE parent_id=%s
UNION
SELECT CTE_CAT.id, CTE_CAT.name, c.parent_id, CTE_CAT.parents||c.parent_id 
FROM CTE_CAT
JOIN catalog_category c ON c.id = CTE_CAT.parent_id
)
SELECT distinct on (id) id,name, parents
FROM CTE_CAT 
ORDER BY id, array_length(parents, 1) desc;
"""


CATEGORY_DESCENDANTS_QUERY = """
WITH RECURSIVE CTE AS(
    SELECT * FROM catalog_category
    WHERE id=%s AND is_active=%s
    UNION 
    SELECT c.*   
    FROM catalog_category c
    JOIN CTE  ON c.parent_id = CTE.id
)
SELECT * FROM CTE;
"""


## GET ALL Product from the current category and subcategories
CATEGORY_PRODUCT_QUERY = """

WITH RECURSIVE graph(id) AS(
SELECT id FROM catalog_category
WHERE id=%s AND is_active=true
UNION 
SELECT c.id FROM catalog_category c, graph g WHERE c.parent_id = g.id AND c.is_active=true
)
SELECT * from catalog_product p
WHERE p.category_id IN (SELECT id FROM graph ORDER BY id);
"""


CATEGORY_TREE_QUERY = """

"""


def get_attribute_type_key(value):
    return utils.find_element_by_value_in_tuples(value, ATTRIBUTE_TYPE)

def get_gender_key(value):
    return utils.find_element_by_value_in_tuples(value, GENDER)


def get_attribute_type_value(key):
    return utils.find_element_by_key_in_tuples(key, ATTRIBUTE_TYPE)

def get_gender_value(key):
    return utils.find_element_by_key_in_tuples(key, GENDER)


def get_category_page_title(key):
    return utils.find_element_by_key_in_tuples(key, CATEGORIES)
