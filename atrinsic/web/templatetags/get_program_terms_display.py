from django import template
register = template.Library()
from atrinsic.base.models import Organization,PublisherRelationship

def get_program_terms_display(parser, token):
    '''Returns the PublisherRelationship term between the 2 parties'''
    #try:
    function, pid, aid = token.split_contents()
    publisher_id = template.Variable(pid)
    advertiser_id = template.Variable(aid)
    
    return ProgramTermNode(publisher_id,advertiser_id)
    #except ValueError:
    #    raise template.TemplateSyntaxError, "%r tag requires 2 arguments publisher and advertiser id" % token.contents.split()[0]
       
class ProgramTermNode(template.Node):
    def __init__(self,publisher_id,advertiser_id):
        self.publisher_id = publisher_id
        self.advertiser_id = advertiser_id
    def render(self, context):
        publisher = Organization.objects.get(id=self.publisher_id.resolve(context))
        advertiser = Organization.objects.get(id=self.advertiser_id.resolve(context))
        pt = PublisherRelationship.objects.get(publisher=publisher,advertiser=advertiser)
        return pt.program_term.display_term()

register.tag('get_program_terms_display', get_program_terms_display)