__docformat__ = 'restructuredtext'
"""
Utility functions for loading various Invite Media models
"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
# Imported this way to work with invitemedia/library/testing/mock/mock_rest_model
from invitemedia.library import model

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------
def get_connection(rest_server_url, rest_user, rest_password):
    """
    Get a connection to REST, using a cache if necessary to avoid
    extra logins
    """
        
    if(model.Connection.cached == True):
        rest_conn = model.Connection.conn_cache            
    else:
        rest_conn = model.Connection(rest_server_url)
        rest_conn.login(rest_user, rest_password)
        model.Connection.cached = True
        model.Connection.conn_cache = rest_conn
        
    return rest_conn
        

def load_lineitems(rest_server_url, rest_user, rest_password):
    """ 
    Loads all lineitems from the database and caches 
    them in a local dict
    """

    rest_conn = get_connection(rest_server_url, rest_user, rest_password)
    LineItem = rest_conn.model('line_items')    
    try:
        lineitems = LineItem.all()
    except Exception:
        rest_conn.login(rest_user, rest_password)
        lineitems = LineItem.all()
        
    lineitem_dict = dict([(li.id, li) for li in lineitems])
    
    return lineitem_dict

def load_inventories(rest_server_url, rest_user, rest_password):
    """
    Loads all inventory sizes from the database and caches 
    them in a local dict
    """
    rest_conn = get_connection(rest_server_url, rest_user, rest_password)
        
    InventorySize = rest_conn.model('inventory_sizes')    
    
    try:
        sizes = InventorySize.all()
    except Exception:
        rest_conn.login(rest_user, rest_password)
        sizes = InventorySize.all()
    
    inventory_size_dict = dict([(sz.id, sz) for sz in sizes])
    
    return inventory_size_dict

def load_placements(rest_server_url, rest_user, rest_password):
    """ 
    Loads all placements from the database and caches 
    them in a local dict
    """
    rest_conn = get_connection(rest_server_url, rest_user, rest_password)
        
    try:
        Placement = rest_conn.model('placements')    
    except Exception:
        rest_conn.login(rest_user, rest_password)
        Placement = rest_conn.model('placements')    
        
    return dict([(p.id, p) for p in Placement.all()])

def load_campaigns(rest_server_url, rest_user, rest_password):
    """ 
    Loads all campaigns from the database and caches 
    them in a local dict
    """
    rest_conn = get_connection(rest_server_url, rest_user, rest_password)

    Campaign = rest_conn.model('campaigns')    
    try:
        campaigns = Campaign.all()
    except Exception:
        rest_conn.login(rest_user, rest_password)
        campaigns = Campaign.all()
        
    campaigns = dict([(camp.id, camp) for camp in campaigns])    
    
    return campaigns

def load_publisher_items(rest_server_url, rest_user, rest_password):
    """ 
    Loads all campaigns from the database and caches 
    them in a local dict
    """
    rest_conn = get_connection(rest_server_url, rest_user, rest_password)
                      
    PublisherItem = rest_conn.model('publisher_items')    

    try:
        pub_items = PublisherItem.all()
    except Exception:
        rest_conn.login(rest_user, rest_password)
        pub_items = PublisherItem.all()

    pub_items = dict([(pub_item.id, pub_item) for pub_item in pub_items])    
    
    return pub_items

def load_creatives(rest_server_url, rest_user, rest_password,creative_ids=None):
    """ 
    Loads all creatives from the databases and caches 
    them in a local variables 
    """
    rest_conn = get_connection(rest_server_url, rest_user, rest_password)
        
    Creative = rest_conn.model('creatives')    
    try:
        if isinstance(creative_ids, (tuple, list, set)): 
            creatives = Creative.get_many(creative_ids)
        else:
            creatives = Creative.all()
    except Exception:
        rest_conn.login(rest_user, rest_password)
        if isinstance(creative_ids, (tuple, list, set)): 
            creatives = Creative.get_many(creative_ids)
        else:
            creatives = Creative.all()
            
    creatives = dict([(creative.id, creative) for creative in creatives])
    
    return creatives

def load_pixels(rest_server_url, rest_user, rest_password):
    """
    Loads all pixels from database and caches them in a dict
    """
    rest_conn = get_connection(rest_server_url, rest_user, rest_password)
        
    Pixel = rest_conn.model('pixels')    
    
    try:
        pixels = Pixel.all()
    except Exception:
        rest_conn.login(rest_user, rest_password)
        pixels = Pixel.all()
        
    pixel_dict = dict([(pixel.id, pixel) for pixel in pixels])
    for pixel_id, pixel in pixel_dict.iteritems():
        # Lineitems need to be a set
        pixel.lineitems = set(pixel.lineitems)
        
    return pixel_dict
