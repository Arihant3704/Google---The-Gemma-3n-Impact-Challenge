
import unittest
import numpy as np
from onboard.src.agent import Agent

class TestAgent(unittest.TestCase):

    def test_obstacle_avoidance(self):
        agent = Agent(camera_width=640, camera_height=480)
        
        # Simulate an obstacle directly in front of the car
        lidar_distances = np.full(360, 1.0)
        lidar_distances[0] = 0.1 # Obstacle at 0 degrees
        lidar_angles = np.linspace(-np.pi, np.pi, 360)

        throttle, steering = agent.get_action("search", None, lidar_distances, lidar_angles)

        # The agent should reverse and turn
        self.assertEqual(throttle, -0.2)
        self.assertEqual(steering, 0.5)

if __name__ == '__main__':
    unittest.main()
