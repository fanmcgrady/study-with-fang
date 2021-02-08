# 《先进计算模型》深度强化学习 hello world 程序
import chainer
import chainer.functions as F
import chainer.links as L
import chainerrl
import gym
import numpy as np


# 使用强化学习模型chainerrl，来创建一个agent智能体
def createDQNAgent(env):
    # 构建Q Network
    class QFunction(chainer.Chain):
        def __init__(self, obs_size, n_actions, n_hidden_channels=50):
            super().__init__()
            with self.init_scope():
                self.l0 = L.Linear(obs_size, n_hidden_channels)
                self.l1 = L.Linear(n_hidden_channels, n_hidden_channels)
                self.l2 = L.Linear(n_hidden_channels, n_actions)

        def __call__(self, x, test=False):
            """
            Args:
                x (ndarray or chainer.Variable): An observation
                test (bool): a flag indicating whether it is in test mode
            """
            h = F.tanh(self.l0(x))
            h = F.tanh(self.l1(h))
            return chainerrl.action_value.DiscreteActionValue(self.l2(h))

    obs_size = env.observation_space.shape[0]
    n_actions = env.action_space.n
    q_func = QFunction(obs_size, n_actions)
    # 是否使用gpu
    # q_func.to_gpu()

    # Use Adam to optimize q_func. eps=1e-2 is for stability.
    optimizer = chainer.optimizers.Adam(eps=1e-2)
    optimizer.setup(q_func)

    # Set the discount factor that discounts future rewards.
    gamma = 0.95

    # Use epsilon-greedy for exploration
    explorer = chainerrl.explorers.ConstantEpsilonGreedy(
        epsilon=0.3, random_action_func=env.action_space.sample)

    # DQN uses Experience Replay.
    # Specify a replay buffer and its capacity.
    replay_buffer = chainerrl.replay_buffer.ReplayBuffer(capacity=10 ** 6)

    # Since observations from CartPole-v0 is numpy.float64 while
    # Chainer only accepts numpy.float32 by default, specify
    # a converter as a feature extractor function phi.
    phi = lambda x: x.astype(np.float32, copy=False)

    # Now create an graduation_agent that will interact with the environment.
    agent = chainerrl.agents.DoubleDQN(
        q_func, optimizer, replay_buffer, gamma, explorer,
        replay_start_size=32, update_interval=1,
        target_update_interval=100, phi=phi)

    return agent


# 使用手工的方式训练agent
def trainingAgent(agent, env):
    # train agent
    print('开始训练agent')

    n_episodes = 100

    for i in range(1, n_episodes + 1):
        obs = env.reset()
        reward = 0
        done = False
        R = 0  # return (sum of rewards)
        t = 0  # time step
        while not done:
            # Uncomment to watch the behaviour
            # env.render()
            action = agent.act_and_train(obs, reward)
            obs, reward, done, _ = env.step(action)
            R += reward
            t += 1
        if i % 10 == 0:
            print('episode:', i,
                  'R:', R)
        agent.stop_episode_and_train(obs, reward, done)

    print('Agent training finished！')


# 随机的方式创建一个agent智能体
class randomAgent():
    """The world's simplest agent!"""

    def __init__(self, env):
        self.action_space = env.action_space

    def act(self, observation):
        return self.action_space.sample()

    def stop_episode(self):
        pass

    def load(self, model_name):
        pass


# 使用gym的CartPole游戏
env = gym.make('CartPole-v0')

# 1、随机的方法创建智能体
# agent = randomAgent(env)

# 2、手写的强化学习方法创建智能体
agent = createDQNAgent(env)
# 现场训练模型
trainingAgent(agent, env)

# 3、循环运行10次游戏，对agent进行测试
for i_episode in range(10):
    observation = env.reset()
    R = 0
    for t in range(200):
        env.render()
        action = agent.act(observation)
        observation, reward, done, info = env.step(action)
        R += reward
        if done:
            print("{}:Episode finished after {} timesteps, reward {}".format(i_episode, t + 1, R))
            break
    agent.stop_episode()
