from tensorforce.environments import Environment
import abc


class AbstractEnvironment(Environment, metaclass=abc.ABCMeta):

    def __init__(self):
        super().__init__()

    @abc.abstractclassmethod
    def states(self):
        """ Defines and returns the state space
        """
        raise NotImplementedError('states method must defined to use this base class')

    @abc.abstractclassmethod
    def actions(self):
        """ Defines and returns the action space
        """
        raise NotImplementedError('actions method must defined to use this base class')

    @abc.abstractclassmethod
    def reset(self):
        """ Defines and executes steps to reset environment after episode
        """
        raise NotImplementedError('reset method must defined to use this base class')

    @abc.abstractclassmethod
    def execute(self, actions):
        """ Executes an action in the environment

        Parameters
        ----------
        actions :
            chosen action to be executed in the environment

        Returns
        ----------
        next_state :
            next state after executing the actions
        terminal :
            boolean for having reached the final state
        reward :
            reward for the executed action
        """
        raise NotImplementedError('execute method must defined to use this base class')

    @abc.abstractclassmethod
    def calc_reward(self, status):
        """ Returns the reward for a given status

        Parameters
        ----------
        status :
            state or state descrpition that enables reward calculation

        Returns
        ----------
        reward :
            numeric value expressing good and bad states
        """
        raise NotImplementedError('calc_reward method must defined to use this base class')

    def max_episode_timesteps(self):
        """ Optional: should only be defined if environment has a natural fixed
         maximum episode length; restrict training timesteps via
         Environment.create(..., max_episode_timesteps=???)

        """
        return super().max_episode_timesteps()

    def close(self):
        """ Optional additional steps to close environment
        """
        super().close()


