import requests
import json
import os
import random
import numpy as np
import io
import base64

from ExplosionGen import ExplosionGenerator
from PIL import Image, ImageDraw, ImageEnhance
from Settings import *
from APICallHandler import APICallHandler
from PromptVault import PromptVault as PV
from Logger import Logger


api_handler = APICallHandler(API_SETTINGS)

class Player():
    
    def __init__(self,path,logger,iteration=0,seed=random.randint(0,10000),fav_color="",subject="Clown",char_type='player',element="Water", splash="Big splash"):

        self.seed = seed
        random.seed(seed)
        self.iteration = iteration
        self.path = path
        self.subject = subject
        self.bodyfront = ""
        self.facefront = ""
        self.legsfront = ""
        self.element = element
        self.splash = splash
        self.fav_color_rgb_converted = (0,0,0)
        self.number_of_explosions = 5
        self.logger = logger
        
        with open('./templates/colorpicker.json', 'r', encoding="utf8") as file:
            jsondata = json.load(file)
        # print(len(list(jsondata.get('color').keys()))) # Get length of color list
        # print(jsondata.get('color', {}).get('gold')) # Get RGB by name

        if fav_color == "":
            fav_color_index = random.randint(0, len(list(jsondata.get('color').keys()))-1)
            self.fav_color = list(jsondata.get('color').keys())[fav_color_index] # get name at index
            self.fav_color_rgb = jsondata.get('color', {}).get(list(jsondata.get('color').keys())[fav_color_index]) # get rgb at index

        else: 
            self.fav_color = fav_color
            self.fav_color_rgb  = jsondata.get('color', {}).get(self.fav_color)

        print("PLAYGEN: Character's Fav_color:",self.fav_color,"- fav_color_rgb:",self.fav_color_rgb)
                
    def convert_template_to_fav_color(self, image_path, color_str=(0, 0, 255),bleached=False,doublebleached=False):
    
        color = tuple(map(int, color_str.replace('(','').replace(')','').split(',')))
        self.fav_color_rgb_converted = color
        if bleached: # divides color by half towards white - red --> pink
            color = (
            int(color[0] + (255-color[0])* 0.5),
            int(color[1] + (255-color[1])* 0.5),
            int(color[2] + (255-color[2])* 0.5)
            )
        if doublebleached: # divides color by half towards white - red --> pink
            color = (
            int(color[0]*(1/4) + 191),
            int(color[1]*(1/4) + 191),
            int(color[2]*(1/4) + 191)
            )
            
        
        img = Image.open(image_path).convert('L')  # Convert image to grayscale
        
        img_array = np.array(img)
        
        normalized_img = img_array / 255.0 # Normalize the pixel values to be between 0 and 1
        
        colored_img = np.zeros((img_array.shape[0], img_array.shape[1], 3), dtype=np.uint8)
        for i in range(3):
            colored_img[:, :, i] = (normalized_img * color[i] ).astype(np.uint8)
        
        # Convert the numpy array back to an image
        result_img = Image.fromarray(colored_img, 'RGB')
        
        # result_img.save(image_path+"edited-template.png") # Save the image (for debugging)
        
        buffer = io.BytesIO()
        result_img.save(buffer, format="PNG")
        processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return processed_base64_data
        
    def transparencyConversion(self, image, threshold=20, middlefill=False): # isolates central object
        image_data = base64.b64decode(image)
        img = Image.open(io.BytesIO(image_data)).convert("RGBA")
        datas = img.getdata()

        width, height = img.size
        new_data = list(datas)
        visited = [[False for _ in range(width)] for _ in range(height)]
        
        def is_dark(pixel):
            return pixel[0] < threshold and pixel[1] < threshold and pixel[2] < threshold
        
        def flood_fill(x, y):
            stack = [(x, y)]
            while stack:
                cx, cy = stack.pop()
                if cx < 0 or cy < 0 or cx >= width or cy >= height:
                    continue
                if visited[cy][cx]:
                    continue
                visited[cy][cx] = True
                idx = cy * width + cx
                if is_dark(datas[idx][:3]):
                    new_data[idx] = (255, 255, 255, 0)
                    stack.append((cx + 1, cy))
                    stack.append((cx - 1, cy))
                    stack.append((cx, cy + 1))
                    stack.append((cx, cy - 1))
        
        # Start flood fill from the edges
        for x in range(width):
            if not visited[0][x]:
                flood_fill(x, 0)
            if not visited[height - 1][x]:
                flood_fill(x, height - 1)
        for y in range(height):
            if not visited[y][0]:
                flood_fill(0, y)
            if not visited[y][width - 1]:
                flood_fill(width - 1, y)
        if middlefill:
            if not visited[int(height//2.1)][int(width//2.1)]:
                flood_fill(int(width/2.1),int(height/2.1))
        
        img.putdata(new_data)
        
        dimx = dimy = 128  # player size
        downsized = img.resize((dimx, dimy), Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        downsized.save(buffer, format="PNG")
        processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return processed_base64_data
        
    def check_border_transparency(self,image, tolerance=70): # checks if left/top/right pixels are mostly transparent
        width, height = image.size
        pixels = image.load()
        
        non_transparent_countL = non_transparent_countR = non_transparent_countT = 0

        for x in range(width):
            if pixels[x, 0][3] != 0:
                non_transparent_countT += 1
            if non_transparent_countT > tolerance:
                return False
            #if pixels[x, height - 1][3] != 0: # --> Bottom row
            #    non_transparent_count += 1
        for y in range(height):
            if pixels[0, y][3] != 0:
                non_transparent_countL += 1
            if non_transparent_countL > tolerance:
                return False
            if pixels[width - 1, y][3] != 0:
                non_transparent_countR += 1
            if non_transparent_countR > tolerance:
                return False
        return True
        
    def taper_transparency(self, image_data, until_percentage=0.25, from_percentage=0.75):
        image_data = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")
        width, height = image.size

        alpha = image.split()[3]

        new_alpha = alpha.copy()
        draw = ImageDraw.Draw(new_alpha)

        until_height = int(height * until_percentage)
        from_height = int(height * from_percentage)

        for y in range(height):
            if until_height > 0 and y <= until_height:
                transparency = int(y / until_height * 255)
            elif from_height < height and y >= from_height:
                transparency = int((y - from_height) / (height - from_height) * 255)
            else:
                transparency = 255

            for x in range(width):
                current_alpha = alpha.getpixel((x, y))
                if until_height > 0 and y <= until_height:
                    new_alpha_value = min(current_alpha, transparency)
                elif from_height < height and y >= from_height:
                    new_alpha_value = min(current_alpha, 255 - transparency)
                else:
                    new_alpha_value = current_alpha
                draw.point((x, y), fill=new_alpha_value)

        image.putalpha(new_alpha)
        
        # image.save(output_path, format="PNG") # save for debugging
        
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return processed_base64_data
        
    def convert_image_to_alpha(self,base64_data): # changes image to grayscale and then to alpha only.
        
        image_data = base64.b64decode(base64_data)
        img = Image.open(io.BytesIO(image_data)).convert("RGBA")
        
        grayscale = img.convert('L')
        alpha_image = Image.new("RGBA", grayscale.size)
        grayscale_data = grayscale.getdata()
        new_data = []
        for pixel in grayscale_data:
            new_data.append((255, 255, 255, pixel))  # R, G, B, A

        alpha_image.putdata(new_data)
        
        buffer = io.BytesIO()
        alpha_image.save(buffer, format="PNG")
        processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return processed_base64_data
                
    def increase_alpha_exponentially(self, base64_data, percentage, exponent=2):
        # Open the image
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")
        width, height = image.size

        # Process the image
        pixels = image.load()

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                # Calculate the increase in alpha using an exponential function
                if a > 0:
                    increase = int((255 - a) * ((percentage / 100.0) ** exponent))
                    # Ensure new alpha is capped at 255
                    new_alpha = min(a + increase, 255)
                    # Update the pixel with the new alpha
                    pixels[x, y] = (r, g, b, new_alpha)
                else:
                    # Keep fully transparent pixels as they are
                    pixels[x, y] = (r, g, b, a)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return processed_base64_data
        
    def fade_to_transparency(self,base64_data,radius=50):
        
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")
        
        width, height = image.size

        # Extract the alpha channel from the original image
        original_alpha = image.split()[-1]

        # Create an alpha mask with the original alpha values
        alpha_mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(alpha_mask)

        # Calculate center of the image
        center_x, center_y = width // 2, height // 2

        # Calculate the maximum distance from the center to the nearest edge
        max_distance = int(min(center_x, center_y) - radius - 10) #(10 pixels extra margin)

        # Create a numpy array for faster manipulation
        alpha_array = np.array(original_alpha)

        for y in range(height):
            for x in range(width):
                # Calculate the distance from the centersssssssss
                distance = ((center_x - x)**2 + (center_y - y)**2)**0.5
                
                if distance <= radius:
                    # Fully opaque within the radius, keep original transparency
                    alpha_value = alpha_array[y, x]
                else:
                    # Fade to transparent outside the radius
                    fade_distance = distance - radius
                    fade_alpha_value = max(0, 255 * (1 - fade_distance / max_distance))
                    alpha_value = int(alpha_array[y, x] * (fade_alpha_value / 255))

                alpha_array[y, x] = alpha_value

        # Convert the numpy array back to an image
        alpha_mask = Image.fromarray(alpha_array)

        # Put the alpha mask on the original image
        image.putalpha(alpha_mask)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return processed_base64_data

    def shift_color(self, base64_data, color_str, shift_factor=0.8):
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")
        pixels = image.load()
        
        color = tuple(map(int, color_str.replace('(','').replace(')','').split(',')))

        target_r, target_g, target_b = color

        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = pixels[x, y]

                if a > 0 and (r, g, b) == (255, 255, 255):
                    new_r = int(r + (target_r - r) * shift_factor)
                    new_g = int(g + (target_g - g) * shift_factor)
                    new_b = int(b + (target_b - b) * shift_factor)
                    pixels[x, y] = (new_r, new_g, new_b, a)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return processed_base64_data
        
    def process_image(input_image_path): # TODO - not used!
        # Load the image
        img = Image.open(input_image_path).convert("RGBA")
        
        # Convert black pixels to transparent
        datas = img.getdata()
        new_data = []
        for item in datas:
            # Change all black (also shades of black) pixels to transparent
            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                new_data.append((255, 255, 255, 0))  # Make black pixels transparent
            else:
                new_data.append(item)
        img.putdata(new_data)

        # Perform 36 rotations and save each image
        for i in range(36):
            rotated_img = img.rotate(10 * i, expand=True, center=(img.width // 2, img.height // 2))
            # Crop the rotated image to the original size
            width, height = rotated_img.size
            left = (width - img.width) // 2
            top = (height - img.height) // 2
            right = (width + img.width) // 2
            bottom = (height + img.height) // 2
            cropped_rotated_img = rotated_img.crop((left, top, right, bottom))

            # Cut the image in half horizontally
            north_half = cropped_rotated_img.crop((0, 0, img.width, img.height // 2))
            south_half = cropped_rotated_img.crop((0, img.height // 2, img.width, img.height))

            # Save the halves
            north_half.save(f'player-halo-north-{i+1}.png')
            south_half.save(f'player-halo-south-{i+1}.png')

    def process_base64_image(self, base64_data, char_type='player', tolerance=10):
        # Decode the base64 image data
        image_data = base64.b64decode(base64_data)
        img = Image.open(io.BytesIO(image_data)).convert("RGBA")
        
        # Convert black pixels to transparent
        datas = img.getdata()
        new_data = []
        for item in datas:
            # Change all black (also shades of black) pixels to transparent
            if item[0] < tolerance and item[1] < tolerance and item[2] < tolerance:
                new_data.append((255, 255, 255, 0))  # Make black pixels transparent
            else:
                new_data.append(item)
                
        img.putdata(new_data)
        dimx = dimy = 128  # player size
        #img.resize((dimx, dimy), Image.Resampling.LANCZOS)
        # Perform 36 rotations and save each image
        for i in range(36):
            rotated_img = img.rotate(10 * i, expand=True, center=(img.width // 2, img.height // 2))
            # Crop the rotated image to the original size
            width, height = rotated_img.size
            left = (width - img.width) // 2
            top = (height - img.height) // 2
            right = (width + img.width) // 2
            bottom = (height + img.height) // 2
            cropped_rotated_img = rotated_img.crop((left, top, right, bottom))
            # resized_img = cropped_rotated_img.resize((dimx, int(dimy/2)), Image.Resampling.LANCZOS)

            # Cut the image in half horizontally
            north_half = cropped_rotated_img.crop((0, 0, img.width, img.height // 2))
            south_half = cropped_rotated_img.crop((0, img.height // 2, img.width, img.height))
            north_half_resized = north_half.resize((int(dimx*1.5), int(dimy/2)), Image.Resampling.LANCZOS)
            south_half_resized = south_half.resize((int(dimx*1.5), int(dimy/2)), Image.ANTIALIAS)

            # Save the halves
            north_half_resized.save(self.path+f'{self.iteration} - {char_type}-halo-north{i+1}.png')
            south_half_resized.save(self.path+f'{self.iteration} - {char_type}-halo-south{i+1}.png') # TODO - add enemy counter so that enemy1 doesn't overwrite enemy2.
        
    def scale_up_crop_bottom(self, image_data): # TODO - make generic
        image_data = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")
        width, height = image.size
        image_stretched = image.resize((width, int(height*1.1)), Image.Resampling.LANCZOS)
        cropped_stretched_img = image_stretched.crop((0, 0, width, height))
        # cropped_stretched_img.save(output_path, format="PNG")
                
        buffer = io.BytesIO()
        cropped_stretched_img.save(buffer, format="PNG")
        processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return processed_base64_data
        
    def rotate_image_counterclockwise(self, image_data):
        image_data = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")

        rotated_img = image.rotate(90, expand=True)
        
        buffer = io.BytesIO()
        rotated_img.save(buffer, format="PNG")
        processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return processed_base64_data
        
    def merge_images(self,base64_background, overlay_path, alpha=1.0):
        background = base64.b64decode(base64_background)
        background = Image.open(io.BytesIO(background)).convert("RGBA")

        overlay = Image.open(overlay_path).convert("RGBA")

        if alpha < 1.0:
            enhancer = ImageEnhance.Brightness(overlay)
            overlay = enhancer.enhance(alpha)

        combined = Image.alpha_composite(background, overlay)
        
        buffer = io.BytesIO()
        combined.save(buffer, format="PNG")
        processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return processed_base64_data

        
    def coordinate_generations(self,char_type):
        if VerboseLogging: self.logger.logTime("s8-sub")
        player_image_data = {}
        face_data = {}
        body_data = {}
        legs_data = {}
        attack_data = {}
        player_image_data['face_data'] = face_data
        player_image_data['body_data'] = body_data
        player_image_data['legs_data'] = legs_data
        player_image_data['attack_data'] = attack_data
        player_image_data['healthbar_data'] = ""
        player_image_data['crosshair_data'] = ""
        player_image_data['pittrap_data'] = []
        face_data['idle'] = []
        face_data['move'] = []
        face_data['jump'] = []
        face_data['dead'] = []
        body_data['idle'] = []
        body_data['move'] = []
        body_data['jump'] = []
        body_data['dead'] = []
        legs_data['idle'] = []
        legs_data['move'] = []
        legs_data['jump'] = []
        legs_data['dead'] = []
        attack_data['projectile_data'] = []
        attack_data['splash_data'] = []
        
        if char_type == 'player':
            self.number_of_explosions = 0 # Player doesn't need explosions?   
            # Crosshair
            crosshair = self.convert_template_to_fav_color('./templates/crosshair.png', color_str=self.fav_color_rgb,bleached=False)
            processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,crosshair,PV.crosshair(self.fav_color),PV.crosshairNeg(),30,12,0.75,512,512,"DDIM")
            processed_img_data = self.transparencyConversion(processed_img_data, threshold=8, middlefill=True)
            player_image_data['crosshair_data'] = processed_img_data
            api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-crosshair.png')
            # health_bar
            generated_image = api_handler.SDRender(self.seed,PV.healthBar(),PV.healthBarNeg(),40,13,512,64,"Euler a")
            player_image_data['healthbar_data'] = generated_image['images'][0]
            api_handler.save_image(generated_image['images'][0], self.path,f'{self.iteration} - {char_type}-healthbar.png')
            # pit_traps (5/5 images)
            with open('./templates/pit-trap-indicator.png', 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            api_handler.save_image(image_data, self.path,f'{self.iteration} - {char_type}-pit_trap00.png')
            temp_list = []
            temp_list.append(image_data) # hard-code trap indicator on [0]
            for i in range(10): # number of different traps
                processed_img_data = api_handler.SDRender(self.seed+i,PV.pitTrap(),PV.pitTrapNeg(),40,14,512,512,"DDIM")
                processed_img_data = self.merge_images(processed_img_data['images'][0],'./templates/pit-trap-indicator.png',alpha=0.8)
                temp_list.append(processed_img_data)
                api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-pit_trap{i}.png')
            player_image_data['pittrap_data'] = temp_list
            if VerboseLogging: self.logger.logTime("step-8-0")

                
        # Explosions:
        explosionGenerator = ExplosionGenerator()
        attack_data['explosion_data'] = explosionGenerator.generate_explosion_sequence(
            self.path,
            prompt=PV.explosionRender(),
            negprompt=PV.explosionRenderNeg(),
            steps=35,
            cfg_scale=13.0,
            strength=0.85,
            width=512,
            height=512,
            sampler_name='Euler a',
            iterations=random.randint(3,8),
            blend_factor=0.3,
            seed=self.seed+self.iteration+random.randint(5000,9999),
            number_of_explosions=self.number_of_explosions
        )
        if VerboseLogging: self.logger.logTime("step-8a")

        # face idle
        self.facefront = self.convert_template_to_fav_color('./templates/faceidle.png', color_str=self.fav_color_rgb,bleached=True)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.facefront,PV.playerFace(self.subject),PV.playerFaceNeg(),30,10,0.9,512,512,"Euler a")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.0,0.70) 
        face_data['idle'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-face-idle1.png')

        # body idle (1 image)
        self.bodyfront = self.convert_template_to_fav_color('./templates/bodyidle.png', color_str=self.fav_color_rgb,bleached=False)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.bodyfront,PV.playerBody(self.fav_color,self.subject),PV.playerBodyNeg(),30,10,0.9,512,512,"Euler a")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.30,0.85) 
        body_data['idle'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-body-idle1.png')

        # legs idle (1 image)
        self.legsfront = self.convert_template_to_fav_color('./templates/legsidle.png', color_str=self.fav_color_rgb,doublebleached=True)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.legsfront,PV.playerLegs(self.fav_color,self.subject),PV.playerLegsNeg(),40,12,0.9,512,512,"DDIM")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.1,1.0) 
        legs_data['idle'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-legs-idle1.png')
        if VerboseLogging: self.logger.logTime("step-8b")


        # face dead
        self.facefront = self.convert_template_to_fav_color('./templates/facedead.png', color_str=self.fav_color_rgb,bleached=True)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.facefront,PV.playerFace(self.subject),PV.playerFaceNeg(),30,10,0.9,512,512,"Euler a")
        processed_img_data = self.rotate_image_counterclockwise(self.taper_transparency(self.transparencyConversion(processed_img_data),0.0,0.70))
        face_data['dead'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-face-dead1.png')

        # body dead (1 image)
        self.bodyfront = self.convert_template_to_fav_color('./templates/bodydead.png', color_str=self.fav_color_rgb,bleached=False)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.bodyfront,PV.playerBody(self.fav_color,self.subject),PV.playerBodyNeg(),30,10,0.9,512,512,"Euler a")
        processed_img_data = self.rotate_image_counterclockwise(self.taper_transparency(self.transparencyConversion(processed_img_data),0.30,0.85))
        body_data['dead'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-body-dead1.png')

        # legs dead (1 image)
        self.legsfront = self.convert_template_to_fav_color('./templates/legsdead.png', color_str=self.fav_color_rgb,doublebleached=True)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.legsfront,PV.playerLegs(self.fav_color,self.subject),PV.playerLegsNeg(),40,12,0.9,512,512,"DDIM")
        processed_img_data = self.rotate_image_counterclockwise(self.taper_transparency(self.transparencyConversion(processed_img_data),0.1,1.0))
        legs_data['dead'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-legs-dead1.png')
        if VerboseLogging: self.logger.logTime("step-8c")


        # legs jump (2 images)
        self.legsfront = self.convert_template_to_fav_color('./templates/legsjump.png', color_str=self.fav_color_rgb,doublebleached=True)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.legsfront,PV.playerLegs(self.fav_color,self.subject),PV.playerLegsNeg(),40,12,0.9,512,512,"DDIM")
        processed_img_data2 = self.taper_transparency(self.transparencyConversion(processed_img_data),0.1,1.0) 
        legs_data['jump'].append(processed_img_data2) #2!!!
        api_handler.save_image(processed_img_data2, self.path,f'{self.iteration} - {char_type}-legs-jump1.png')
        processed_img_data3 = self.taper_transparency(self.scale_up_crop_bottom(self.transparencyConversion(processed_img_data)),0.1,1.0)  
        legs_data['jump'].append(processed_img_data2) #3!!!
        api_handler.save_image(processed_img_data3, self.path,f'{self.iteration} - {char_type}-legs-jump2.png')
        if VerboseLogging: self.logger.logTime("step-8d")


        # face move
        self.facefront = self.convert_template_to_fav_color('./templates/facemove.png', color_str=self.fav_color_rgb,bleached=True)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.facefront,PV.playerFaceSide(self.subject),PV.playerFaceNeg(),30,10,0.9,512,512,"Euler a")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.0,0.70) 
        face_data['move'].append(processed_img_data)
        face_data['jump'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-face-move1.png')
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-face-jump1.png') # Jump

        # body move (1/4 and 3/4 images)
        self.bodyfront = self.convert_template_to_fav_color('./templates/bodymove1.png', color_str=self.fav_color_rgb,bleached=False)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.bodyfront,PV.playerBodyMove(self.fav_color,self.subject),PV.playerBodyNeg(),30,10,0.9,512,512,"Euler a")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.30,0.9)
        body_data['move'].append(processed_img_data)
        body_data['jump'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-body-move1.png')
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-body-jump1.png') # Jump
        #seed alteration for 3/4
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed+1,self.bodyfront,PV.playerBodyMove(self.fav_color,self.subject),PV.playerBodyNeg(),30,10,0.9,512,512,"Euler a")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.15,0.9)
        body_data['move'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-body-move3.png')
        
        # body move (2/4 images)
        self.bodyfront = self.convert_template_to_fav_color('./templates/bodymove2.png', color_str=self.fav_color_rgb,bleached=False)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.bodyfront,PV.playerBodyMove(self.fav_color,self.subject),PV.playerBodyNeg(),30,10,0.9,512,512,"Euler a")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.15,0.9) 
        body_data['move'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-body-move2.png')
        
        # body move (4/4 images)
        self.bodyfront = self.convert_template_to_fav_color('./templates/bodymove4.png', color_str=self.fav_color_rgb,bleached=False)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.bodyfront,PV.playerBodyMove(self.fav_color,self.subject),PV.playerBodyNeg(),30,10,0.9,512,512,"Euler a")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.15,0.9)
        body_data['move'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-body-move4.png')

        # legs move (1/3 images)
        self.legsmove1 = self.convert_template_to_fav_color('./templates/legsmove1.png', color_str=self.fav_color_rgb,doublebleached=True)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.legsmove1,PV.playerLegs(self.fav_color,self.subject),PV.playerLegsNeg(),40,12,0.9,512,512,"DDIM")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.1,1.0) 
        legs_data['move'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-legs-move1.png')
        
        # legs move (2/3 images)
        self.legsmove2 = self.convert_template_to_fav_color('./templates/legsmove2.png', color_str=self.fav_color_rgb,doublebleached=True)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.legsmove2,PV.playerLegs(self.fav_color,self.subject),PV.playerLegsNeg(),40,12,0.9,512,512,"DDIM")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.1,1.0) 
        legs_data['move'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-legs-move2.png')
        
        # legs move (3/3 images)
        self.legsmove3 = self.convert_template_to_fav_color('./templates/legsmove3.png', color_str=self.fav_color_rgb,doublebleached=True)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.legsmove3,PV.playerLegs(self.fav_color,self.subject),PV.playerLegsNeg(),40,12,0.9,512,512,"DDIM")
        processed_img_data = self.taper_transparency(self.transparencyConversion(processed_img_data),0.1,1.0) 
        legs_data['move'].append(processed_img_data)
        api_handler.save_image(processed_img_data, self.path,f'{self.iteration} - {char_type}-legs-move3.png')
        if VerboseLogging: self.logger.logTime("step-8e")

        """
        # attack (36 image)
        self.attackhalo = self.convert_template_to_fav_color('./templates/playercircle.png', color_str=self.fav_color_rgb,doublebleached=True)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.attackhalo,PV.attackHalo(self.fav_color),"",30,12,0.75,512,512,"DDIM")
        self.process_base64_image(processed_img_data, char_type=char_type)
        if VerboseLogging: self.logger.logTime("step-8f")

        # projectile (5/5 images)
        self.projectile = self.convert_template_to_fav_color('./templates/projectile.png', color_str=self.fav_color_rgb)
        processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed,self.projectile,PV.projectile(self.fav_color,self.element),PV.projectileNeg(),30,13,0.8,512,512,"DDIM") # base projectile
        for i in range(5): # evolutions
            processed_img_data2 = api_handler.send_data_to_stable_diffusion(self.seed+i,processed_img_data,PV.projectile(self.fav_color,self.element),PV.projectileNeg(),30,13,0.8,512,512,"DDIM")
            processed_img_data2 = self.transparencyConversion(processed_img_data2)
            attack_data['projectile_data'].append(processed_img_data2)
            api_handler.save_image(processed_img_data2, self.path,f'{self.iteration} - {char_type}-projectile{i}.png')
        if VerboseLogging: self.logger.logTime("step-8f")

        # splash (5/5 images) # evolutions
        processed_img_data = api_handler.send_image_to_stable_diffusion(self.seed,'./templates/watersplash.png',PV.splash(self.element,self.splash),PV.splashNeg(),30,13,0.8,512,512,"DDIM") # base splash
        for i in range(7):
            # make processed_img_data taper off transparency radially
            processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed+i,processed_img_data,PV.splashEvo(self.element,self.splash),PV.splashNeg(),30,13,0.6,512,512,"DDIM")
            processed_img_data2 = self.shift_color(self.fade_to_transparency(self.increase_alpha_exponentially(self.convert_image_to_alpha(processed_img_data),30)),self.fav_color_rgb)
            attack_data['splash_data'].append(processed_img_data2)
            api_handler.save_image(processed_img_data2, self.path,f'{self.iteration} - {char_type}-splash{i}.png')
        if VerboseLogging: self.logger.logTime("step-8g")
        """
        
        return player_image_data