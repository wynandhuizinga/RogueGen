import pygame
import random
import heapq
import json
import base64
import io
import os
import re

class MapGen(pygame.sprite.Sprite):
    def __init__(self, seed, screen, screenx, screeny, TILESIZE, TILESX, TILESY, directory, LEVELCOUNT=1, PADDING=10, set_traps=True):
        pygame.sprite.Sprite.__init__(self)
        self.seed = seed
        self.screen = screen
        self.directory = directory
        self.WIDTH, self.HEIGHT = screenx, screeny
        self.GRID_SIZEX = TILESX
        self.GRID_SIZEY = TILESY
        self.TILE_SIZE = TILESIZE
        self.SUBTILE_SIZE = TILESIZE // 5
        self.PADDING = PADDING
        self.LEVELCOUNT = LEVELCOUNT
        self.MILESTONE_COLOR = (255, 0, 0)  # Red
        self.START_COLOR = (0, 255, 0)  # Green
        self.END_COLOR = (0, 0, 255)  # Blue
        self.PATH_COLOR = (255, 255, 255)  # White
        self.WALL_COLOR = (30, 30, 30)  # Dark Gray
        self.TRAP_COLOR = (0, 0, 0, 0)  # Transparent
        self.screen_scroll_x = 0
        self.screen_scroll_y = 0
        self.image = pygame.Surface((20, 20))

        random.seed(self.seed)

        # Load textures
        self.textures = self.load_textures()
        self.all_traps = self.trapLoader()
        self.traps = {}
        self.trap_states = {}

        # Generate random gray grid
        self.grid = [[(random.randint(50, 200),) * 3 for _ in range(self.GRID_SIZEX)] for _ in range(self.GRID_SIZEY)]

        # Place milestones
        self.milestones = random.sample([(x, y) for x in range(self.PADDING, self.GRID_SIZEX - self.PADDING) for y in range(self.PADDING, self.GRID_SIZEY - self.PADDING)], self.LEVELCOUNT+1)
        self.start = self.milestones[0]
        self.end = self.milestones[-1]
        
        #Traps
        self.transparent_image = self.all_traps[0]
        self.traps = {}  # Dictionary to store trap states

        self.create_path()
        self.create_walls()
        if set_traps: self.place_traps()

        # Precompute textures for each tile
        self.tile_textures = self.precompute_tile_textures()

    def load_textures(self):
        textures = {'player': [], 'enemy': {}, 'neutral': []}
        # Load player textures 
        pattern = re.compile(r'^0 - [0-9]{8}.*player.*\.json$')
        for file_name in os.listdir(self.directory):
            match = pattern.match(file_name)
            if match:
                with open(os.path.join(self.directory, file_name), 'r') as f:
                    jsondata = json.load(f)
                floor_tile_data = jsondata['CharGen_data']['FloorSprites']['floor_tile_data']
                for image_data in floor_tile_data:
                    image_bytes = base64.b64decode(image_data)
                    image = pygame.image.load(io.BytesIO(image_bytes)).convert()
                    textures['player'].append(image)
                
                floor_tile_neutral_data = jsondata['FloorSprites-neutral']['floor_tile_data']
                for image_data in floor_tile_neutral_data:
                    image_bytes = base64.b64decode(image_data)
                    image = pygame.image.load(io.BytesIO(image_bytes)).convert()
                    textures['neutral'].append(image)
 
        pattern = re.compile(r'^([0-9]{1,2}) - [0-9]{8}.*\.json$')
        for file_name in os.listdir(self.directory):
            match = pattern.match(file_name)
            if match:
                enemy_num = int(match.group(1))
                with open(os.path.join(self.directory, file_name), 'r', encoding='utf-8') as f:
                    jsondata = json.load(f)
                floor_tile_data = jsondata['CharGen_data']['FloorSprites']['floor_tile_data']
                textures['enemy'][enemy_num] = []
                for image_data in floor_tile_data:
                    image_bytes = base64.b64decode(image_data)
                    image = pygame.image.load(io.BytesIO(image_bytes)).convert()
                    textures['enemy'][enemy_num].append(image)
        return textures

    def precompute_tile_textures(self):
        tile_textures = {}
        for y in range(self.GRID_SIZEY):
            for x in range(self.GRID_SIZEX):
                tile_textures[(x, y)] = self.compute_tile_textures(x, y)
        return tile_textures

    def compute_tile_textures(self, x, y):
        if self.grid[y][x] != self.PATH_COLOR:
            return []

        nearest_milestones = self.get_nearest_milestones((x, y))
        total_distance = sum([dist for dist, _ in nearest_milestones if dist < 10])

        # Calculate the number of sub-tiles to be filled based on the closest milestone
        if nearest_milestones and nearest_milestones[0][0] < 10:
            dist_to_closest = nearest_milestones[0][0]
            fill_ratio = (10 - dist_to_closest) / 10
            num_textures = int(25 * fill_ratio)
        else:
            num_textures = 0

        # Flatten the tile into a 5x5 grid of sub-tiles
        subtile_positions = [(i * self.SUBTILE_SIZE, j * self.SUBTILE_SIZE) for i in range(5) for j in range(5)]
        random.shuffle(subtile_positions)

        textures_to_draw = []
        textures = self.textures['player']  # Default to player textures
        if nearest_milestones and nearest_milestones[0][0] < 10:
            enemy_num = self.milestones.index(nearest_milestones[0][1])
            textures = self.textures['enemy'].get(enemy_num, self.textures['player'])

        for i in range(25):
            subtile_x, subtile_y = subtile_positions[i]
            if i < num_textures:
                texture = textures[random.randint(0, len(textures) - 1)]
            else:
                texture = random.choice(self.textures['neutral'])
            textures_to_draw.append((texture, subtile_x, subtile_y))

        return textures_to_draw

    def draw_tile(self, x, y, camera):
        # Calculate the position of the tile relative to the camera
        tile_x = x * self.TILE_SIZE + camera.camera.x
        tile_y = y * self.TILE_SIZE + camera.camera.y

        # Check if the tile is within the camera's viewport
        if tile_x < -self.TILE_SIZE or tile_x > self.WIDTH or tile_y < -self.TILE_SIZE or tile_y > self.HEIGHT:
            return  # Skip rendering if the tile is not within the viewport

        textures_to_draw = self.tile_textures.get((x, y), [])
        for texture, subtile_x, subtile_y in textures_to_draw:
            self.screen.blit(texture, (tile_x + subtile_x, tile_y + subtile_y))
            
        if (x, y) in self.traps:
            trap_image = self.traps[(x, y)]
            self.screen.blit(trap_image, (tile_x, tile_y))

    def draw_grid(self, camera):
        # Determine the range of tiles that need to be drawn based on the camera's position
        start_x = max(0, -camera.camera.x // self.TILE_SIZE)
        end_x = min(self.GRID_SIZEX, (self.WIDTH - camera.camera.x) // self.TILE_SIZE + 1)
        start_y = max(0, -camera.camera.y // self.TILE_SIZE)
        end_y = min(self.GRID_SIZEY, (self.HEIGHT - camera.camera.y) // self.TILE_SIZE + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if self.grid[y][x] == self.WALL_COLOR:
                    pygame.draw.rect(self.screen, self.WALL_COLOR, (x * self.TILE_SIZE + camera.camera.x, y * self.TILE_SIZE + camera.camera.y, self.TILE_SIZE, self.TILE_SIZE))
                else:
                    color = self.grid[y][x]
                    pygame.draw.rect(self.screen, color, (x * self.TILE_SIZE + camera.camera.x, y * self.TILE_SIZE + camera.camera.y, self.TILE_SIZE, self.TILE_SIZE))
                    self.draw_tile(x, y, camera)

        for milestone in self.milestones:
            pygame.draw.rect(self.screen, self.MILESTONE_COLOR, (milestone[0] * self.TILE_SIZE + camera.camera.x, milestone[1] * self.TILE_SIZE + camera.camera.y, self.TILE_SIZE, self.TILE_SIZE))
        pygame.draw.rect(self.screen, self.START_COLOR, (self.start[0] * self.TILE_SIZE + camera.camera.x, self.start[1] * self.TILE_SIZE + camera.camera.y, self.TILE_SIZE, self.TILE_SIZE))
        pygame.draw.rect(self.screen, self.END_COLOR, (self.end[0] * self.TILE_SIZE + camera.camera.x, self.end[1] * self.TILE_SIZE + camera.camera.y, self.TILE_SIZE, self.TILE_SIZE))

    def get_nearest_milestones(self, position):
        distances = []
        for milestone in self.milestones:
            dist = abs(position[0] - milestone[0]) + abs(position[1] - milestone[1])
            distances.append((dist, milestone))
        return sorted(distances, key=lambda x: x[0])

    def get_tile_pixel_coords(self, tile_coords):
        x, y = tile_coords
        pixel_x = x * self.TILE_SIZE + self.TILE_SIZE // 2
        pixel_y = y * self.TILE_SIZE + self.TILE_SIZE // 2
        return pixel_x, pixel_y

    # A* pathfinding algorithm
    def astar(self, start, goal):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < self.GRID_SIZEX and 0 <= neighbor[1] < self.GRID_SIZEY:
                    if self.grid[neighbor[1]][neighbor[0]] != self.WALL_COLOR:
                        tentative_g_score = g_score[current] + 1
                        if tentative_g_score < g_score.get(neighbor, float('inf')):
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                            if neighbor not in [i[1] for i in open_set]:
                                heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []

    # Function to create zigzag path
    def create_zigzag_path(self, path):
        zigzag_path = []
        for i in range(len(path) - 1):
            current = path[i]
            next_step = path[i + 1]
            zigzag_path.append(current)
            if current[0] != next_step[0] and current[1] != next_step[1]:
                # Add intermediate step to create zigzag
                intermediate = (next_step[0], current[1])
                zigzag_path.append(intermediate)
        zigzag_path.append(path[-1])
        return zigzag_path

    # Function to create rooms around milestones
    def create_room(self, center, size=4):
        for dx in range(-size, size + 1):
            for dy in range(-size, size + 1):
                x, y = center[0] + dx, center[1] + dy
                if 0 <= x < self.GRID_SIZEX and 0 <= y < self.GRID_SIZEY:
                    # Add randomness to room shape
                    if random.random() < 0.8:
                        self.grid[y][x] = self.PATH_COLOR

    # Function to create path with expansions
    def create_path(self):
        current = self.start
        for milestone in self.milestones[1:]:
            self.path = self.astar(current, milestone)
            self.path = self.create_zigzag_path(self.path)
            for position in self.path:
                self.grid[position[1]][position[0]] = self.PATH_COLOR
                # Occasional expansions
                if random.random() < 0.1:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            x, y = position[0] + dx, position[1] + dy
                            if 0 <= x < self.GRID_SIZEX and 0 <= y < self.GRID_SIZEY:
                                self.grid[y][x] = self.PATH_COLOR
            current = milestone
            self.create_room(milestone)

    # Function to create walls between rooms
    def create_walls(self):
        for y in range(self.GRID_SIZEY):
            for x in range(self.GRID_SIZEX):
                if self.grid[y][x] == self.PATH_COLOR:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.GRID_SIZEX and 0 <= ny < self.GRID_SIZEY and self.grid[ny][nx] != self.PATH_COLOR:
                                self.grid[ny][nx] = self.WALL_COLOR
    
    def place_traps(self):
        # Constants for readability
        MILESTONE_COLOR = self.MILESTONE_COLOR
        START_COLOR = self.START_COLOR
        END_COLOR = self.END_COLOR
        PATH_COLOR = self.PATH_COLOR
        
        # Place traps in random locations ensuring no two traps are adjacent and not on specific colors
        trap_positions = set()
        attempts = 0
        max_attempts = 1000  # Adjust this value if necessary
        desired_traps = int((self.GRID_SIZEX * self.GRID_SIZEY) * 0.05)

        transparent_image = self.all_traps[0]  # Assuming the first image is the transparent one

        while len(trap_positions) < desired_traps and attempts < max_attempts:
            x = random.randint(1, self.GRID_SIZEX - 2)
            y = random.randint(1, self.GRID_SIZEY - 2)
            cell_color = self.grid[y][x]

            if (cell_color == PATH_COLOR and 
                cell_color != MILESTONE_COLOR and 
                cell_color != START_COLOR and 
                cell_color != END_COLOR and 
                (x, y) not in trap_positions):
                
                if not any((nx, ny) in trap_positions for nx, ny in self.get_neighbors((x, y))):
                    trap_positions.add((x, y))
                    self.traps[(x, y)] = transparent_image
                    self.trap_states[(x, y)] = False 
                    
            attempts += 1

        if len(trap_positions) < desired_traps:
            print(f"Warning: Only placed {len(trap_positions)} out of {desired_traps} desired traps due to constraints.")
                    
    def is_collision(self, rect):
        # Define the area to check for collisions
        start_x = max(0, rect.x // self.TILE_SIZE)
        end_x = min(self.GRID_SIZEX, (rect.right // self.TILE_SIZE) + 1)
        start_y = max(0, rect.y // self.TILE_SIZE)
        end_y = min(self.GRID_SIZEY, (rect.bottom // self.TILE_SIZE) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if self.grid[y][x] == self.WALL_COLOR:
                    wall_rect = pygame.Rect(x * self.TILE_SIZE, y * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE)
                    if rect.colliderect(wall_rect):
                        return True
        return False
    
    def get_neighbors(self, node):
        x, y = node
        neighbors = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.GRID_SIZEX and 0 <= ny < self.GRID_SIZEY]
        return neighbors

    def heuristic(self, a, b):
        (x1, y1), (x2, y2) = a, b
        return abs(x1 - x2) + abs(y1 - y2)

    def get_nearest_milestones(self, tile):
        distances = [(self.heuristic(tile, milestone), milestone) for milestone in self.milestones]
        return sorted(distances)

    def trapLoader(self):
        pattern = re.compile(rf'^0 - [0-9]{{8}}.*\.json$') # hardcoded 0 for player, seed has to be 8 digits.
        for file_name in os.listdir(self.directory):
            match = pattern.match(file_name)
            if match:
                with open(os.path.join(self.directory, file_name), 'r', encoding='utf-8') as f:
                    jsondata = json.load(f)

        trap_data_set = jsondata['CharGen_data']['PlayerSprites']['pittrap_data']
        all_traps = []

        for image_data in trap_data_set:
            image_bytes = base64.b64decode(image_data)
            img = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width()*(self.TILE_SIZE/512)), int(img.get_height()*(self.TILE_SIZE/512))))
            all_traps.append(img)

        return all_traps