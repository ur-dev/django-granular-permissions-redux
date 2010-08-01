from django import template
import re

register = template.Library()

class PermNode(template.Node):
    def __init__(self, user_var, perm_var, obj_var, nodelist_true, nodelist_false):
        self.user = template.Variable(user_var)
        self.perm = template.Variable(perm_var)
        self.obj = template.Variable(obj_var)
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        user = self.user.resolve(context)
        obj = self.obj.resolve(context)
        perm = self.perm.resolve(context)
        if user.has_row_perm(obj, perm):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)

@register.tag
def if_row_perms(parser, token):
    '''If-style template tag to test if the specified user has the
        specified row-level perms for the specified object.

        Usage:
            {% load row_level_perms %}

            {% if_row_perms user 'perm' object %}
            You have permission!
            {% endif_row_perms %}

            {% if_row_perms user 'perm' object %}
            You have permission!
            {% else %}
            You don't have permission :(
            {% endif_row_perms %}
    '''
    tag, _, bits = token.contents.partition(' ')
    bits = bits.split()
    end_tag = 'end'+tag
    nodelist_true = parser.parse([end_tag, 'else'])
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse([end_tag])
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    if len(bits) < 3:
        raise template.TemplateSyntaxError, "%r tag requires exactly 3 arguments." % tag
    bits += [nodelist_true, nodelist_false]
    return PermNode(*bits)



