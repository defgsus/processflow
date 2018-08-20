from ..description import State
from . import object_compare


class ProcessRunnerContext(object):

    def __init__(self, process_runner, initial_state, **kwargs):
        """
        Create a new context for a runner
        :param kwargs: any key/value that should be stored in the context
        """
        self._runner = process_runner
        self._pd = self._runner._pd
        self._current_state = initial_state
        self._function_context = _FunctionContext(self, **kwargs)
        self._finished = False

    def _log(self, x):
        print(x)

    def step(self):
        if self._finished:
            return
        if not isinstance(self._current_state, State):
            raise ValueError("Invalid state '%s'" % self._current_state)

        # get state function
        func = self._runner.get_state_function(self._current_state.name)
        if not func or not callable(func):
            raise ValueError("Invalid state function '%s' for state '%s'" % (func, self._current_state))

        # run state decision function and determine next state
        self._log("running state: %s" % self._current_state)
        next_state = func(self._function_context)

        # verify next state
        if next_state is None:
            self._log("process finished")
            self._finished = True
            return

        if not isinstance(next_state, State):
            raise ValueError("Invalid next state '%s' returned from state function for '%s'" % (
                next_state, self._current_state))
        if not self._pd.has_transition(self._current_state.name, next_state.name):
            raise ValueError("Invalid transition from state '%s' to '%s'" % (
                self._current_state, next_state
            ))

        # get transition function
        transition = self._runner.get_transition(self._current_state.name, next_state.name)
        self._log("running transition: %s" % transition)
        func = self._runner.get_transition_function(self._current_state.name, next_state.name)
        if not func or not callable(func):
            raise ValueError("Invalid transition function '%s' for transition '%s'" % (
                func, transition))

        pre_condition = object_compare.deep_copy(self._function_context)

        # run transition function
        result = func(self._function_context)

        post_condition = object_compare.deep_copy(self._function_context)

        changes = object_compare.get_difference(pre_condition, post_condition)
        invalid_changes = object_compare.subtract_valid_changes(changes, transition.changes)
        if invalid_changes:
            raise RuntimeError("transition '%s' has made invalid changes to context: '%s'" % (
                transition, invalid_changes
            ))

        self._current_state = next_state

        return result




class _FunctionContext:
    """
    A relatively clean context object which is passed to state and transition functions
    and contains the runtime objects
    """
    def __init__(self, prc, **kwargs):
        self._prc = prc
        self._states = _StateObject(self._prc._runner.states())
        self._objects = kwargs

        for key in self._objects:
            setattr(self, key, self._objects[key])

    @property
    def state(self):
        return self._states


class _StateObject:
    def __init__(self, states):
        self._states = states
        for s in states:
            setattr(self, s.name, s)
