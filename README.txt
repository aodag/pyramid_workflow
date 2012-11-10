pyramid_workflow
=============================

::

   @workflow_config(
      type="security",
      name="the workflow",
      state_attr="state",
      initial_state="private",
      content_types=".dummy.IContent",
      permission_checker="repoze.bfg.security.has_permission")
   class SecurityWorkflow(object):
   
      private = State(callback=".dummy.callback",
           title="Private",
           description="Nobody can see it")
   
      public = State(callback=".dummy.callback",
        title="Public",
        description="Everybody can see it")
   
      public_to_private = Transition(
         callback=".dummy.callback",
         from_state="public",
         to_state="private",
         permission="moderate")
   
      private_to_public = Transition(
         callback=".dummy.callback",
         from_state="private",
         to_state="public",
         permission="moderate")

