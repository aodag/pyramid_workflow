#
from repoze.workflow.workflow import Workflow, WorkflowError, process_wf_list
from repoze.workflow.interfaces import IWorkflow, IWorkflowList, IDefaultWorkflow
from zope.interface.interfaces import IInterface
from zope.interface import providedBy, Interface, implementer
from pyramid.exceptions import ConfigurationError
import venusian

def get_workflow(request, content_type, type, context=None):
    reg = request.registry
    look = reg.adapters.lookup
    if context is None:
        context = request.context

    if not IInterface.providedBy(content_type):
        content_type = providedBy(content_type)

    if content_type not in (None, IDefaultWorkflow):
        print content_type
        wf_list = look((content_type,), IWorkflowList, name=type, default=None)
        print wf_list
        if wf_list is not None:
            wf = process_wf_list(wf_list, context)
            if wf is not None:
                return wf

    wf_list = look((IDefaultWorkflow,), IWorkflowList, name=type, default=None)
    if wf_list is not None:
        return process_wf_list(wf_list, context)

def register_workflow(config, workflow, type, content_type, elector, info=None):
    
    if content_type is None:
        content_type = IDefaultWorkflow

    if not IInterface.providedBy(content_type):
        content_type = providedBy(content_type)

    reg = config.registry

    wf_list = reg.adapters.lookup((content_type,), IWorkflowList, name=type,
                                 default=None)

    if wf_list is None:
        wf_list = []
        reg.registerAdapter(wf_list, (content_type,), IWorkflowList, type, info)

    wf_list.append({'workflow':workflow, 'elector':elector})

def add_workflow(config, type, name, state_attr, initial_state,
                 content_types=(), elector=None, permission_checker=None,
                 description='',
                 states=[], transitions=[]):

    elector = config.maybe_dotted(elector)
    permission_checker = config.maybe_dotted(permission_checker)
    def register(content_type):
        workflow = Workflow(state_attr, initial_state,
                                permission_checker, name,
                                description)

        for state in states:
            try:
                workflow.add_state(state.name,
                                   config.maybe_dotted(state.callback),
                                   aliases=state.aliases,
                                   **state.extras)
            except WorkflowError, why:
                raise ConfigurationError(str(why))

        for transition in transitions:
            try:
                workflow.add_transition(transition.name,
                                        transition.from_state,
                                        transition.to_state,
                                        config.maybe_dotted(transition.callback),
                                        transition.permission,
                                        **transition.extras)
            except WorkflowError, why:
                raise ConfigurationError(str(why))
        try:
            workflow.check()

        except WorkflowError, why:
            raise ConfigurationError(str(why))
        register_workflow(config, workflow, type, content_type,
                              elector)

    if elector is not None:
        elector_id = id(self.elector)
    else:
        elector_id = None

    for content_type in content_types:
        content_type = config.maybe_dotted(content_type)
        intr = config.introspectable(category_name="workflow",
            discriminator="",
            title="register workflow",
            type_name="Workflow",
            )    
        config.action("workflow", register,
            args=(content_type,),
            introspectables=(intr,))

def includeme(config):
    config.add_directive('add_workflow', add_workflow)

class IState(Interface):
    pass

class ITransition(Interface):
    pass

@implementer(IState)
class State(object):
    def __init__(self, callback=None, title=None, **kw):
        self.callback = callback
        self.extras = {}
        self.extras['title'] = title
        self.aliases = []

@implementer(ITransition)
class Transition(object):
    def __init__(self, from_state, to_state,
                 callback=None, permission=None):
        self.from_state = from_state
        self.to_state = to_state
        self.callback = callback
        self.permission = permission
        self.extras = {}


def workflow_config(type, name, state_attr, initial_state,
                 content_types=(), elector=None, permission_checker=None,
                 description=''):
    def wrap(cls):
        def callback(scanner, _, ob):
            states = []
            transitions = []
            for key, value in ob.__dict__.items():
                if IState.providedBy(value):
                    value.name = key
                    states.append(value)
                if ITransition.providedBy(value):
                    value.name = key
                    transitions.append(value)
            scanner.config.add_workflow(
                type=type,
                name=name, state_attr=state_attr, initial_state=initial_state,
                content_types=content_types, elector=elector, permission_checker=permission_checker,
                description=description, states=states, transitions=transitions)
        venusian.attach(cls, callback)
        return cls
    return wrap
