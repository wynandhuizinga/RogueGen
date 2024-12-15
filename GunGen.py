from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import base64
import random
import io
from Settings import *
from APICallHandler import APICallHandler
from PromptVault import PromptVault as PV
from PlayGen import Player as PG

api_handler = APICallHandler(API_SETTINGS)

class GunGen():
    def __init__(self, seed, path):
        self.path = path
        self.seed = seed
        self.counter = 0

    def generate(self, guntype, amount, threshold, fav_color, fav_color_rgb, iteration=""):
        # Constants
        width, height = 832, 448
        gray = (135, 135, 135)
        diagray = (85, 85, 85)
        black = (0, 0, 0)
        fade_percentage_horizontal = 40
        fade_percentage_vertical = 40
        border_percentage = 5
        self.counter += 100
        gun_data_list = []

        for j in range(amount):
            # Helper function to draw a fading line
            def draw_fading_line(draw, start, end, width, color):
                half_width = width // 2
                for i in range(width):
                    if i <= half_width:
                        alpha = i / half_width
                    else:
                        alpha = (width - i) / half_width
                    fade_color = int(color[0] * alpha), int(color[1] * alpha), int(color[2] * alpha)
                    draw.line([(start[0], start[1] + i), (end[0], end[1] + i)], fill=fade_color)

            for k in range(11):
                # 1. Generate a full black image of 448 by 832 pixels
                img = Image.new('RGB', (width, height), black)
                draw = ImageDraw.Draw(img)

                # 2. Generate 1-3 diagonal scanlines under an angle of 65% starting from 5% of the width ending at 20% of the width
                diagonal_count = np.random.randint(1, 4)
                diagonality = random.randint(60, 70)
                # 3. Add 2-4 gray horizontal scanlines starting from 25% of the height up to 70% of the height
                scanline_count = np.random.randint(2, 5)
                for _ in range(diagonal_count):
                    diagray = (random.randint(70, 90), random.randint(70, 90), random.randint(70, 90))
                    diag_scanline_width = np.random.randint(7, 12)
                    start_x = np.random.randint(int(width * 0.25), int(width * 0.35))
                    end_x = start_x + int(height / np.tan(np.deg2rad(-diagonality)))
                    draw_fading_line(draw, (start_x, height * 0.4), (end_x, height), diag_scanline_width, diagray)
                for _ in range(scanline_count):
                    gray = (random.randint(100, 135), random.randint(100, 135), random.randint(100, 135))
                    hori_scanline_width = np.random.randint(7, 15)
                    y = np.random.randint(int(height * 0.25), int(height * 0.6))
                    draw_fading_line(draw, (0, y), (width, y), hori_scanline_width, gray)

                # 4. Fade the left and right side to black starting from the border percentage
                fade_start_horizontal = int(width * (border_percentage / 100))
                fade_length_horizontal = int(width * (fade_percentage_horizontal / 100))
                for x in range(fade_start_horizontal, fade_start_horizontal + fade_length_horizontal):
                    alpha = (x - fade_start_horizontal) / fade_length_horizontal
                    for y in range(height):
                        r, g, b = img.getpixel((x, y))
                        fade_color = int(r * alpha), int(g * alpha), int(b * alpha)
                        draw.point((x, y), fill=fade_color)
                        r, g, b = img.getpixel((width - 1 - x, y))
                        fade_color = int(r * alpha), int(g * alpha), int(b * alpha)
                        draw.point((width - 1 - x, y), fill=fade_color)

                # 5. Fade the top and bottom side to black starting from the border percentage
                fade_start_vertical = int(height * (border_percentage / 100))
                fade_length_vertical = int(height * (fade_percentage_vertical / 100))
                for y in range(fade_start_vertical, fade_start_vertical + fade_length_vertical):
                    alpha = (y - fade_start_vertical) / fade_length_vertical
                    for x in range(width):
                        r, g, b = img.getpixel((x, y))
                        fade_color = int(r * alpha), int(g * alpha), int(b * alpha)
                        draw.point((x, y), fill=fade_color)
                        r, g, b = img.getpixel((x, height - 1 - y))
                        fade_color = int(r * alpha), int(g * alpha), int(b * alpha)
                        draw.point((x, height - 1 - y), fill=fade_color)

                # 6. Add a black border such that no scanlines are visible within 10% of the outer image border
                border_size = int(width * (border_percentage / 100))
                for x in range(width):
                    for y in range(height):
                        if x < border_size or x >= width - border_size or y < border_size or y >= height - border_size:
                            draw.point((x, y), fill=black)

                # 7. Save the output as PNG and base64 data string - debugging
                #output_path = 'output_image.png'
                #img.save(output_path)

                # 8. Convert to base64
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

                # 9. SD steps for base gun
                processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed+self.counter, img_base64, PV.gunPrompt(guntype), PV.gunPromptNeg(), 30, 7, 0.65, 832, 384, "DDIM")
                
                # 11. Add transparency and masks for base gun
                base_gun_img = self.transparencyConversion(processed_img_data, threshold=threshold, bottomrightfill=True)

                # 10. Convert processed image back to PIL Image for base gun
                base_gun_img = Image.open(io.BytesIO(base64.b64decode(base_gun_img)))

                # 15. Validate the alpha values
                alpha_threshold = 0
                alpha_pixel_count = 0
                total_pixels = base_gun_img.width * base_gun_img.height

                for x in range(base_gun_img.width):
                    for y in range(base_gun_img.height):
                        if base_gun_img.getpixel((x, y))[3] > alpha_threshold:
                            alpha_pixel_count += 1                    
                # 16. Check if more than 80% of the pixels have a non-zero alpha value
                if alpha_pixel_count / total_pixels <= 0.2:
                    # Convert combined image to base64
                    print("picture is not overly full: ",alpha_pixel_count / total_pixels, "%")
                    break
                else:
                    print("picture is overly full: ",alpha_pixel_count / total_pixels, "%, ABORTING!")  
                    # Save the base gun image
                    base_gun_output_path = f'{self.path}/failure {iteration}-{self.counter}- gun__{guntype}_{j}_base.png'
                    base_gun_img.save(base_gun_output_path)  
                    continue

            # 12. Check and flip the base gun image if necessary
            flipped = False
            if self.handle_on_right_side(base_gun_img):
                base_gun_img = base_gun_img.transpose(Image.FLIP_LEFT_RIGHT)
                flipped = True

            # 13. Create a new transparent image of the same size
            transparent_img = Image.new("RGBA", (width // 2, height), (0, 0, 0, 0))

            # 14. Create a new image with the transparent image on the left and the processed image on the right
            combined_img = Image.new("RGBA", (int(width * 1.5), height))
            combined_img.paste(transparent_img, (0, 0))
            combined_img.paste(base_gun_img, (width // 2, 0))
            
            # Save the base gun image
            base_gun_output_path = f'{self.path}/{iteration}-gun__{guntype}_{j}_base_{flipped}.png'
            combined_img.save(base_gun_output_path)

            # Add base gun image to the gun_data structure
            buffered_base = io.BytesIO()
            combined_img.save(buffered_base, format="PNG")
            base_gun_base64 = base64.b64encode(buffered_base.getvalue()).decode("utf-8")
            
            # projectile (5/5 images)
            base_projectile_image_data = []
            upgrade_projectile_image_data = []
            projectile = self.convert_template_to_fav_color("./templates/projectile.png", color_str=fav_color_rgb)
            projectile_processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed+j+self.counter,projectile,PV.projectile(fav_color,"Water"),PV.projectileNeg(),30,13,0.8,512,512,"DDIM") # base projectile
            for i in range(4): # evolutions
                projectile_processed_img_data2 = api_handler.send_data_to_stable_diffusion(self.seed+i+j+self.counter,projectile_processed_img_data,PV.projectile(fav_color,"Water"),PV.projectileNeg(),30,13,0.8,512,512,"DDIM")
                projectile_processed_img_data2 = self.transparencyConversion2(projectile_processed_img_data2)
                if i < 2:
                    base_projectile_image_data.append(projectile_processed_img_data2)
                    upgrade_projectile_image_data.append(projectile_processed_img_data2)
                    api_handler.save_image(projectile_processed_img_data2, self.path,f'{iteration}-{self.counter} - projectile{i}.png')

                else:
                    upgrade_projectile_image_data.append(projectile_processed_img_data2)
                    api_handler.save_image(projectile_processed_img_data2, self.path,f'{iteration}-{self.counter} - projectile{i}.png')
                
            # splash (5/5 images) # evolutions
            base_splash_image_data = []
            upgrade_splash_image_data = []
            splash_processed_img_data = api_handler.send_image_to_stable_diffusion(self.seed+j+self.counter,'./templates/watersplash.png',PV.splash("Water","Big Splash"),PV.splashNeg(),30,13,0.8,512,512,"DDIM") # base splash
            for i in range(7):
                splash_processed_img_data = api_handler.send_data_to_stable_diffusion(self.seed+i+j+self.counter,splash_processed_img_data,PV.splashEvo("Water","Big Splash"),PV.splashNeg(),30,13,0.6,512,512,"DDIM")
                splash_processed_img_data2 = self.shift_color(self.fade_to_transparency(self.increase_alpha_exponentially(self.convert_image_to_alpha(splash_processed_img_data),30)),fav_color_rgb)
                if i < 3:
                    base_splash_image_data.append(splash_processed_img_data2)
                    upgrade_splash_image_data.append(splash_processed_img_data2)
                    api_handler.save_image(splash_processed_img_data2, self.path,f'{iteration}-{self.counter} - splash{i}.png')
                else:
                    upgrade_splash_image_data.append(splash_processed_img_data2)
                    api_handler.save_image(splash_processed_img_data2, self.path,f'{iteration}-{self.counter} - splash{i}.png')
                    

            base_gun_data = {
                "gun_image_data": base_gun_base64,
                "projectile_data": base_projectile_image_data,  # Replace with actual data
                "splash_data": base_splash_image_data  # Replace with actual data
            }

            # 13. Create mask from base gun for upgraded gun
            mask = Image.new("L", base_gun_img.size, 0)
            for x in range(base_gun_img.width):
                for y in range(base_gun_img.height):
                    if base_gun_img.getpixel((x, y))[3] > 0:  # Non-transparent pixel
                        mask.putpixel((x, y), 255)
            
            # 14. SD steps for upgraded gun
            upgraded_img_data = api_handler.send_data_to_stable_diffusion(self.seed+self.counter, processed_img_data, PV.gunUpgradePrompt(fav_color, guntype), PV.gunUpgradePromptNeg(), 30, 13, 0.2, 832, 384, "DDIM")

            # 15. Convert upgraded image back to PIL Image
            upgraded_gun_img = Image.open(io.BytesIO(base64.b64decode(upgraded_img_data)))

            # 17. Check and flip the upgraded gun image if necessary (consistent with base gun)
            if flipped:
                upgraded_gun_img = upgraded_gun_img.transpose(Image.FLIP_LEFT_RIGHT)
                
            # 16. Apply mask to upgraded gun
            upgraded_gun_img.putalpha(mask)

            combined_upgraded_img = Image.new("RGBA", (int(width * 1.5), height))
            combined_upgraded_img.paste(transparent_img, (0, 0))
            combined_upgraded_img.paste(upgraded_gun_img, (width // 2, 0))
            
            # Save the upgraded gun image
            upgraded_gun_output_path = f'{self.path}/{iteration}-gun__{guntype}_{j}_upgraded_{flipped}.png'
            combined_upgraded_img.save(upgraded_gun_output_path)

            # Add upgraded gun image to the gun_data structure
            buffered_upgraded = io.BytesIO()
            combined_upgraded_img.save(buffered_upgraded, format="PNG")
            upgraded_gun_base64 = base64.b64encode(buffered_upgraded.getvalue()).decode("utf-8")

            upgraded_gun_data = {
                "gun_image_data": upgraded_gun_base64,
                "projectile_data": upgrade_projectile_image_data,  # Replace with actual data
                "splash_data": upgrade_splash_image_data  # Replace with actual data
            }

            gun_data_list.append({
                "base_gun_data": base_gun_data,
                "upgraded_gun_data": upgraded_gun_data
            })

        return gun_data_list

    def handle_on_right_side(self, img):
        """Determine if the handle of the gun is on the right side of the image."""
        width, height = img.size
        pixels = np.array(img)

        # Define region for detecting handle: bottom half of the image
        bottom_half = pixels[int(height / 2):, :]

        # Summarize horizontal and vertical blobs in the bottom half
        vertical_blobs = np.sum(np.sum(bottom_half, axis=2) < 255 * 3, axis=0)
        horizontal_blobs = np.sum(np.sum(bottom_half, axis=2) < 255 * 3, axis=1)

        # Find the vertical blob with the most pixels
        handle_position = np.argmax(vertical_blobs)

        # Check if the handle is on the right side
        if handle_position > width // 2:
            return True
        return False
        
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
        
    def transparencyConversion2(self, image, threshold=20, middlefill=False): # isolates central object
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
        

    def transparencyConversion(self, image, threshold=5, bottomrightfill=False):
        # Isolates central object
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
        if bottomrightfill:
            if not visited[int(height * 0.75)][int(width * 0.75)]:
                flood_fill(int(height * 0.75), int(width * 0.75))

        img.putdata(new_data)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
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