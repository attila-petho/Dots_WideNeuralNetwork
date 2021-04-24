import numpy as np
import cv2
from collections import deque

class ObsWrapper:
    """
    Wrapper a megfigyelésekhez:
    A környezetből array formában kapott megfigyeléseket:
        1. Transzponálja
        2. Szürkeárnyalatosítja
        3. Átméretezi (96x96 pixelre)
        4. Normalizálja
        5. 4 db egymást követő megfigyelést konkatenálja
    """
    def __init__(self, env, stack=3):
        self.env = env
        self.stack = stack
        self.frames = deque([], maxlen=stack)

    def step(self, red_action, yellow_action):
        state, red_rew, yellow_rew, iteration, game_over = self.env.step(red_action, yellow_action)
        shaped_observation = self._shape_observation(state)
        if iteration == 1:
            for i in range(self.stack):
                self.frames.append(shaped_observation)
            return self._get_observation(), red_rew, yellow_rew, iteration, game_over
        else:
            self.frames.append(shaped_observation)
            return self._get_observation(), red_rew, yellow_rew, iteration, game_over

    def _get_observation(self):
        return np.array(self.frames)

    def _shape_observation(self, observation):
        observation = np.transpose(observation, (1, 0, 2))
        observation = cv2.cvtColor(observation, cv2.COLOR_RGB2GRAY)
        observation = cv2.resize(observation, dsize=(96, 96), interpolation=cv2.INTER_AREA)
        observation = observation / 255.0
        return observation
