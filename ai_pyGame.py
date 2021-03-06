# -*- coding: utf-8 -*-
import random
from pyGameView import pyGame
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import time as t

DEBUG = True
#DEBUG = False

CONT = False
CONT = True

EPISODES = 1000

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 0.01
        if not CONT:
            self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995
        self.learning_rate = 0.001
        self.model = self._build_model()


    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(128, input_dim=self.state_size, activation='relu'))
        model.add(Dense(64, activation='relu'))
#        model.add(Dense(64, activation='relu'))
#        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        #print(act_values, state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)




if __name__ == "__main__":


    if DEBUG:
        EPISODES = 10
        env = pyGame(verbose = True, fps = 1000)
    else:
        env = pyGame(verbose = False, fps = 1000)

    scores = []
    avg = 0
    state_size = 8 #rearAxis, frontAxis, parkEnd, parkFront
    action_size = 3 #7 -> action 0 - stop, 1-forward, 2-backward, 3 forward + right, 4 forward + left, 5 - backward + rigth, 6 backward + left
    agent = DQNAgent(state_size, action_size)
    if CONT:
        agent.load("./game_save.h5")
        print("Loading")
    f=open("results.csv","a+")
    done = False
    batch_size = 32
    print("Start")
    for e in range(EPISODES):
        actionTime  = 0.0
        stepTime    = 0.0
        replayTime  = 0.0

        state = env.reset(rX = True)
        state = np.reshape(state, [1, state_size])
        maxReward = 0
        for time in range(100):
            # env.render()
            actionTime -= t.time()
            action = agent.act(state)
            actionTime += t.time()

            stepTime -= t.time()
            next_state, reward, done, _ = env.step(action)
            stepTime += t.time()
            #print(time,action)
            #print(next_state, reward, done)
            maxReward = max(maxReward, reward)
            #reward = reward if not done else -100
            next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            if done:
                #print("episode: {}/{}, score: {}, e: {:.2}"
                #      .format(e, EPISODES, maxReward, agent.epsilon))
                break
            if len(agent.memory) > batch_size:
                replayTime -= t.time()
                agent.replay(batch_size)
                replayTime += t.time()

        if e % 10 == 0:
            agent.save("./game_save.h5")
        scores.append(reward)
        avg = int(np.average(scores[-10:]))

        print("episode: {:4}/{},    score: {:5} / {:5}    avg: {:5}, e: {:5.2},    Action {:6.2},   Step {:7.2},   Replay {:5.2}"
              .format(e, EPISODES, reward, maxReward, avg, agent.epsilon, actionTime, stepTime, replayTime))
        f.write("{},{},{},{},{},{:.2}\n"
            .format(e, EPISODES, reward, maxReward, avg, agent.epsilon))
        #print(scores[:-10])
    f.close()
