from django.conf import settings


def format_initial_dict(dict):
    ''' For use with forms "initial" to deal with FK 
        pointers
    '''
    new_dict = {}
    for key, value in dict.items():
        new_dict[key] = value
        if key.endswith('_id'):
            new_dict[key[:-3]] = dict[key]
    return new_dict

def base36_encode(val):
    """
        @desc       Encodes string into base36 value.
        @param:     val, string to encode.
        @return:    string, encoded string.
    """
    CLIST = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    rv = ""
    if val != None:
        while val != 0:
            rv = CLIST[val % 36] + rv
            val /= 36
        return rv
    else:
        return None
    
def base36_decode(val):
    return int(val, 36)
    

def parse_sku_file(skufile, org, sl=None, list_name = None, headers={}):
    from datetime import datetime 
    from atrinsic.base.models import SKUList,SKUListItem
    import tempfile
    file_id,file_path = tempfile.mkstemp()
    file_obj = open(file_path,"wb")
    file_obj.write(skufile.read())
    file_obj.close()
    for row in open(file_path, 'rb').readlines():
        row = row.split("\t")
        if len(row) > 1:
            if headers:
                if not sl:
                    if headers.has_key('LISTID'):
                        sl = SKUList.objects.get(pk=headers['LISTID'], organization = org)
                        sl.skulistitem_set.all().delete()
                    else:
                        if list_name == None:
                            list_name = 'ftp upload <%s>' % datetime.now()
                        sl = SKUList.objects.create(name=list_name, advertiser=org)
                        
            SKUListItem.objects.create(skulist=sl, external_sku=row[1].strip(), item=row[0].strip())
        elif len(row) == 1:
            var_name,var_value = row[0].split("=")
            headers[var_name]=var_value
        else:
            err_msg = "the uploaded file did not contain the needed headers or what not in the proper format"