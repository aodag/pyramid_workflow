from pyramid_workflow import workflow_config, State, Transition
from zope.interface import Interface, implementer

class IContext(Interface):
    pass

@implementer(IContext)
class Context(object):
    pass

@workflow_config(
   type="security",
   name="the workflow",
   state_attr="state",
   initial_state="private",
   content_types=(IContext,),
   permission_checker="pyramid.security.has_permission")
class SecurityWorkflow(object):

   private = State(
        title="Private",
        description="Nobody can see it")

   public = State(
     title="Public",
     description="Everybody can see it")

   public_to_private = Transition(
      from_state="public",
      to_state="private",
      permission="moderate")

   private_to_public = Transition(
      from_state="private",
      to_state="public",
      permission="moderate")

def workflow_view(request):
    from . import get_workflow
    wf = get_workflow(request, IContext, "security")
    if not hasattr(request.context, "state"):
        wf.initialize(request.context)
    if "transition" in request.params:
        wf.transition(request.context, request, request.params['transition'])
    transitions = wf.get_transitions(request.context, request)
    state_info = wf.state_of(request.context)
    return dict(transitions=transitions, state_info=state_info)

def main():
    from pyramid.config import Configurator
    config = Configurator()
    config.include('pyramid_workflow')
    root = Context()
    config.set_root_factory(lambda request: root)
    config.add_view(workflow_view, context=Context, renderer="example_view.pt")
    config.scan(".")
    app = config.make_wsgi_app()
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8080, app)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
