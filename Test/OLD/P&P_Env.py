import gymnasium as gym
import numpy as np
from gymnasium import spaces
import pygame


class DotEnv(gym.Env):
    def __init__(self, screen_width=400, screen_height=400, render_mode='human'):
        super(DotEnv, self).__init__()

        # screen dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.render_mode = render_mode

        # defining the agent policies
        self.direction_line_length = 20
        self.game_speed = 1
        self.test_health = 10

        # for Blue dot
        self.blue_dot_radius = 20
        self.blue_dot_health = 5
        self.blue_dot_attack_dmg = 1
        self.blue_dot_search_radius = 100
        self.blue_dot_turn_rate = None
        self.blue_dot_stamina = 50
        self.blue_dot_stamina_recovery_rate = 15
        self.blue_dot_speed = None
        self.blue_active_status = True

        # for Red dot
        self.red_dot_radius = self.blue_dot_radius - 10
        self.red_dot_health = 50
        self.red_dot_attack_dmg = 1
        self.red_dot_search_radius = None
        self.red_dot_turn_rate = None
        self.red_dot_speed = None

        # action space (left, right, up, down) for both
        self.action_space = spaces.Discrete(4)

        # Define observation space (positions of blue dot and red dot)
        self.observation_space = spaces.Box(low=np.array([0, 0, 0, 0], dtype=np.float32),
                                            high=np.array([self.screen_width / 2, self.screen_height, self.screen_width,
                                                           self.screen_height], dtype=np.float32),
                                            dtype=np.float32)

        # Initializing the pygame window
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Dots Moving Environment')

        # Initializing the positions of the blue and red dots
        self.blue_dot_pos = np.array([self.screen_width / 4, self.screen_height / 2], dtype=np.float32)
        self.red_dot_pos = np.array([3 * self.screen_width / 4, self.screen_height / 2], dtype=np.float32)

        # Define grid line properties
        self.grid_color = (0, 0, 0)
        self.grid_spacing = 20  # Adjust this value to change the grid spacing

        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

        # defining the reward for the agent
        self.total_reward = 0

        self.obstacles = [
            (200, 100, 20, 150),
            (300, 250, 50, 20)
        ]

    def reset(self, seed=0):
        super().reset(seed=seed)

        # Reset the positions of the blue and red dots
        self.blue_dot_pos = np.array([self.screen_width / 2, self.screen_height / 2], dtype=np.float32)
        self.red_dot_pos = np.array([3 * self.screen_width / 4, self.screen_height / 2], dtype=np.float32)

        self.blue_dot_health = self.test_health
        self.total_reward = 0

        # Return the initial observation (concatenate blue dot position and red dot position)
        observation = np.concatenate([self.blue_dot_pos, self.red_dot_pos])
        # print(observation)

        return [observation, seed]

    def step(self, action):
        reward = 0
        done = False
        # Define the movement speed
        self.blue_dot_speed = 0.9 * self.game_speed

        # unpacking the action for blue and red dots
        action_blue_dot, action_red_dot = action
        temp_reward = 0
        if action_blue_dot == 0:  # Move blue dot left
            self.blue_dot_pos[0] -= self.blue_dot_speed
            temp_reward = 0.001

        elif action_blue_dot == 1:  # Move blue dot right
            self.blue_dot_pos[0] += self.blue_dot_speed
            temp_reward = 0.001

        elif action_blue_dot == 2:  # Move blue dot up
            self.blue_dot_pos[1] -= self.blue_dot_speed
            temp_reward = 0.001

        elif action_blue_dot == 3:  # Move blue dot down
            self.blue_dot_pos[1] += self.blue_dot_speed
            temp_reward = 0.001

        reward += temp_reward

        self.red_dot_speed = 0.05 * self.game_speed

        if action_red_dot == 0:  # Move blue dot left
            self.blue_dot_pos[0] -= self.red_dot_speed
            # temp_reward = 0.001

        elif action_red_dot == 1:  # Move blue dot right
            self.blue_dot_pos[0] += self.red_dot_speed
            # temp_reward = 0.001

        elif action_red_dot == 2:  # Move blue dot up
            self.blue_dot_pos[1] -= self.red_dot_speed
            # temp_reward = 0.001

        elif action_red_dot == 3:  # Move blue dot down
            self.blue_dot_pos[1] += self.red_dot_speed
            # temp_reward = 0.001

        distance_between_centers = np.linalg.norm(self.blue_dot_pos - self.red_dot_pos)

        # # Check if the dots collide with each other
        # if distance_between_centers < self.blue_dot_radius + self.red_dot_radius:
        #     # Separate the dots by moving the red dot away from the blue dot
        #
        #     if (self.blue_dot_health == 0):
        #         done = True
        #     reward -= 5
        #     # print("collision")
        #
        # else:
        #     # Move the red dot towards the blue dot with a fixed speed
        #     self.red_dot_pos += move_speed * direction
        # Clip blue dot position to stay within the first half of the screen
        self.blue_dot_pos[0] = np.clip(self.blue_dot_pos[0], 0, self.screen_width)
        self.blue_dot_pos[1] = np.clip(self.blue_dot_pos[1], 0, self.screen_height)

        # if self.blue_dot_health >= 5:
        #     reward += 2
        # else:
        #     reward -= 5

        # Define a simple reward function (e.g., distance between the two dots)
        self.total_reward = reward

        observation = np.concatenate([self.blue_dot_pos, self.red_dot_pos])

        return observation, reward, done, False, {}

    def display_total_reward(self):
        text_surface = self.font.render(f"Reward: {self.total_reward: .2f} Blue Health: {self.blue_dot_health}", True,
                                        (0, 0, 0))

        text_rect = text_surface.get_rect()

        text_rect.center = (self.screen_width - 200, 10)

        self.screen.blit(text_surface, text_rect)

    def render(self):
        if self.render_mode == 'human':
            # Clear the screen
            self.screen.fill((255, 255, 255))

            # Draw grid lines
            for x in range(0, self.screen_width, self.grid_spacing):
                pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.screen_height), 1)
            for y in range(0, self.screen_height, self.grid_spacing):
                pygame.draw.line(self.screen, self.grid_color, (0, y), (self.screen_width, y), 1)

            # Draw blue dot
            pygame.draw.circle(self.screen, (0, 0, 255), (int(self.blue_dot_pos[0]), int(self.blue_dot_pos[1])),
                               self.blue_dot_radius)

            # draw the blue dot search radius
            pygame.draw.circle(self.screen, (0, 0, 255), (int(self.blue_dot_pos[0]), int(self.blue_dot_pos[1])),
                               self.blue_dot_search_radius, 1)

            # Draw red dot
            pygame.draw.circle(self.screen, (255, 0, 0), (int(self.red_dot_pos[0]), int(self.red_dot_pos[1])),
                               self.red_dot_radius)

            self.display_total_reward()

            # Update the display
            pygame.display.update()


if __name__ == "__main__":
    episodes = 20
    env = DotEnv()
    for episode in range(1, episodes + 1):
        env.reset()
        done = False
        score = 0

        while not done:
            env.render()
            blue_action = env.action_space.sample()
            red_action = env.action_space.sample()

            print(red_action)
            action = [blue_action, red_action]
            obs, reward, done, _, info = env.step(action)
            score += reward
        print('Episode:{} Score:{}'.format(episode, score))
    env.close()