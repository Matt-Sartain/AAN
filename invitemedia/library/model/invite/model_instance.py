from invitemedia.library.model import BaseModelInstance

class ModelInstance(BaseModelInstance):
    """
    Represents a instantiated REST resource.  It is assumed that a
    ``ModelInstance`` without an ``id`` is not persisted to the REST service,
    and vice-versa for models with an id.
    
    Fields of the model can be read one of two ways.  Either
    ``entity.fields['field_name']``, or ``entity.field``.  Similarly, fields can
    be set with ``entity.fields['field_name'] = 'foo'`` or
    ``entity.set_field_name('foo')``.
    
    self.__dict__[a] = b trickery was stolen from the Python Cookbook, page 180
    
    :Parameters:
        model : Model
            The REST Model instance to route requets to
        dict : dict
            A dictionary of values that will be set in the model
    """
    def __init__(self, model, model_dict):
        super(ModelInstance, self).__init__(model, model_dict)
        for key, value in model_dict['fields'].iteritems():
            if isinstance(value, dict) and 'pk' in value:
                self.__dict__['fields'][key] = self.__class__(None, value)
            
            elif isinstance(value, list) and len(value) > 0 and \
                 isinstance(value[0], dict) and 'pk' in value[0]:
                self.__dict__['fields'][key] = [self.__class__(None, val) for val in value]
            else:
                self.__dict__['fields'][key] = value
        
        if 'pk' in model_dict.keys():
            self.__dict__['id'] = model_dict['pk']
        else:
            self.__dict__['id'] = None
