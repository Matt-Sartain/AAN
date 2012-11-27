#!/usr/bin/python
from django.core.urlresolvers import reverse

tabs = {}

def tabset(tabgroup_name,order,name,url,subnav):
    ''' Decorator for managing the site navigational tabs and associating with views '''
    global tabs
    tabgroup = tabs.get(tabgroup_name,[])
    tabs[tabgroup_name] = tabgroup
    while len(tabgroup) < order+1:
        tabgroup.append({})

    tabgroup[order] = {'name':name,'url_name':url,'subnav':subnav}

def settab(request,tabgroup_name,name,subnav):  
    ''' Decorator for managing the site navigational tabs and associating with views '''
    global tabs
    request.tab_name = name
    request.tab_subnav = subnav
    request.tabs = tabs
    request.tabgroup_name = tabgroup_name

    
class tab(object):
    ''' Class representing a navigation tab for the site'''

    def __init__(self,tabgroup_name,name,subnav):
        self.tabgroup_name = tabgroup_name
        self.name = name
        self.subnav = subnav

    def __call__(self,f):

        def wrapped_f(request,*args,**kwargs):
            settab(request,self.tabgroup_name,self.name,self.subnav)
            return f(request,*args,**kwargs)
        return wrapped_f


def get_url(ins):
    try:
        if type(ins) == type(tuple()):
            return reverse(ins[0],args=ins[1])
        return reverse(ins)
    except:
        return ''
    

def tab_context(request):
    ''' Method to build a context for the current navigational tabs on the site '''
    data = {}

    if hasattr(request,'tabs'):
        tabgroup = request.tabs[request.tabgroup_name]
        for t in tabgroup:
            if not t:
                continue
            t['url'] = get_url(t['url_name'])

        data["tabs"] = [x for x in tabgroup if x]
        data["current_tab"] = request.tab_name
        data["current_subnav"] = request.tab_subnav
        for i in tabgroup:
            if i and request.tab_name == i['name']:
                data["subnavs"] = []
                for t in i['subnav']:
                    if not t:
                        continue
                    cur_t = {}
                    cur_t['name'] = t[0]
                    cur_t['url'] = get_url(t[1])
                    if len(t) > 2 and t[2] != None:
                        if t[2](request,cur_t):
                            data["subnavs"].append(cur_t)
                    else:
                        data["subnavs"].append(cur_t)

    return data
