import numpy as np

class VFH:
    def __init__(self, num_sectors=36, min_distance=0.5):
        self.num_sectors = num_sectors
        self.min_distance = min_distance

    def get_steering_direction(self, lidar_distances, lidar_angles):
        if lidar_distances is None or lidar_angles is None:
            return 0.0

        # Create a histogram of the lidar data
        histogram = np.zeros(self.num_sectors)
        for i in range(len(lidar_distances)):
            if lidar_distances[i] < self.min_distance:
                sector = int(lidar_angles[i] / (2 * np.pi / self.num_sectors))
                histogram[sector] += 1

        # Find the sector with the fewest obstacles
        best_sector = np.argmin(histogram)

        # Calculate the steering direction
        steering_direction = (best_sector - self.num_sectors / 2) * (2 * np.pi / self.num_sectors)

        return steering_direction

class DepthObstacleDetector:
    def __init__(self, obstacle_threshold=0.25, scan_box_width=120, scan_box_height=80, image_width=640, image_height=480):
        self.obstacle_threshold = obstacle_threshold
        self.scan_box_width = scan_box_width
        self.scan_box_height = scan_box_height
        self.image_width = image_width
        self.image_height = image_height

        self.box_x1 = self.image_width // 2 - self.scan_box_width // 2
        self.box_x2 = self.image_width // 2 + self.scan_box_width // 2
        self.box_y1 = self.image_height // 2 - self.scan_box_height // 2
        self.box_y2 = self.image_height // 2 + self.scan_box_height // 2

    def is_obstacle_present(self, depth_image):
        if depth_image is None:
            return False

        # Crop depth area for obstacle scan
        obstacle_area = depth_image[self.box_y1:self.box_y2, self.box_x1:self.box_x2]
        min_depth = np.nanmin(obstacle_area)

        if np.isfinite(min_depth) and min_depth < self.obstacle_threshold:
            return True

        return False