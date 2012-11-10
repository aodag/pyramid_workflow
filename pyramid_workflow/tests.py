import unittest
from pyramid import testing

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from pyramid_workflow.example import Context
        self.root = Context()

    def _getAUT(self):
        from pyramid.config import Configurator
        from pyramid_workflow import get_workflow
        from pyramid_workflow.example import IContext
        from zope.interface import providedBy
        from repoze.workflow.interfaces import IWorkflowList
        config = Configurator()
        config.include('pyramid_workflow')
        config.set_root_factory(lambda request: self.root)
        def dummy_view(request):
            wf = get_workflow(request, IContext, "security")
            if not hasattr(request.context, 'status'):
                wf.initialize(request.context)

            transitions = wf.get_transitions(request.context, request)
            return dict(transitions=transitions)
        config.add_view(dummy_view, renderer="json")
        config.scan('pyramid_workflow.example')
        app = config.make_wsgi_app()
        import webtest
        return webtest.TestApp(app)

    def test_it(self):
        app = self._getAUT()
        res = app.get('/')
        self.assertEqual(res.json, {})
        
class TestIt(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_workflow')

    def tearDown(self):
        testing.tearDown()

    def test_it(self):
        from pyramid_workflow.example import IContext
        self.config.scan('pyramid_workflow.example')

        from repoze.workflow.interfaces import IWorkflowList
        from zope.interface import providedBy
        wf_list = self.config.registry.adapters.lookup((IContext,), IWorkflowList, name="security")
        self.assertTrue(wf_list)
        self.assertEqual(wf_list[0]['workflow'].name, "the workflow")


class add_workflowTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from . import add_workflow
        return add_workflow(*args, **kwargs)

    def test_it(self):
        from repoze.workflow.interfaces import IWorkflowList
        from zope.interface import providedBy

        type = "test-workflow"
        name = "this is test workflow"
        state_attr = "status"
        initial_state = "init"
        content_types = (testing.DummyResource,)

        self._callFUT(self.config, type, name, state_attr, initial_state,
            content_types=content_types,
            states=[
                testing.DummyModel(name="init", callback=None, aliases=[], extras={}),
            ],
            transitions=[
            ])

        self.config.commit()

        wf_list = self.config.registry.adapters.lookup((providedBy(testing.DummyResource),), IWorkflowList, name=type)
        self.assertTrue(wf_list)
        self.assertEqual(wf_list[0]['workflow'].name, name)
