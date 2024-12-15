import numpy as np
import cv2
import base64
import requests
import json
import random
from APICallHandler import *
from Settings import API_SETTINGS

api_handler = APICallHandler(API_SETTINGS)

class ExplosionGenerator:

    def generate_white_dot_image(self, r1, r2, width=512, height=512):
        image = np.zeros((height, width), np.uint8)
        center = (width // 2, height // 2)
        cv2.circle(image, center, r2, (0,), -1)  # Black circle (fade out area)
        cv2.circle(image, center, r1, (255,), -1)  # White circle (bright center)
        return image

    def merge_images(self, base_image, overlay_image, blend_factor=1.0):
        overlay_image_color = cv2.cvtColor(overlay_image, cv2.COLOR_GRAY2BGR)
        alpha = (overlay_image_color.astype(float) / 255.0) * blend_factor
        base_image_float = base_image.astype(float)
        merged_image = (alpha * overlay_image_color + (1 - alpha) * base_image_float).astype(np.uint8)
        return merged_image

    def apply_alpha_and_fade(self, image):
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        max_radius = width // 2

        # Create alpha mask
        alpha = np.zeros((height, width), dtype=np.uint8)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Set alpha based on grayscale intensity
        alpha = np.interp(gray_image, [0, 20, 50, 255], [0, 64, 192, 255]).astype(np.uint8)

        # Create radial fade mask
        for y in range(height):
            for x in range(width):
                distance = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
                if distance > 200:
                    fade = max(0, 1 - (distance - 200) / (max_radius - 200))
                    alpha[y, x] = int(alpha[y, x] * fade)

        # Add alpha channel to the image
        image_with_alpha = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        image_with_alpha[:, :, 3] = alpha

        # Ensure transparency is preserved
        transparent_mask = alpha == 0
        image_with_alpha[transparent_mask] = [0, 0, 0, 0]

        return image_with_alpha

    def generate_explosion_sequence(self, path, prompt, negprompt, steps, cfg_scale, strength, width, height, sampler_name, iterations=5, blend_factor=0.4, seed=42, number_of_explosions=5):
       
        animation_sequences = []
        r1, r2 = 10, 40
        
        # Generate initial black image with a white dot
        base_image = self.generate_white_dot_image(r1, r2)
        
        counter = 1
        for i in range(number_of_explosions):
            animation_sequence = []
            for j in range(iterations):
                # Convert base image to base64
                _, buffer = cv2.imencode('.png', base_image)
                base64_image = base64.b64encode(buffer).decode('utf-8')
                
                # Send the base64 image to Stable Diffusion
                result_image_data = api_handler.send_data_to_stable_diffusion(seed+i+(j+counter)*seed, base64_image, prompt, negprompt, steps, cfg_scale, strength, width, height, sampler_name)
                
                # Generate the next white dot image with increased radii
                r1 += 5
                r2 += 20
                counter += 9
                new_white_dot_image = self.generate_white_dot_image(r1, r2)
                
                # Merge the new white dot image with the result image
                result_image = cv2.imdecode(np.frombuffer(base64.b64decode(result_image_data), np.uint8), -1)
                result_image_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGRA2BGR)
                base_image = self.merge_images(result_image_rgb, new_white_dot_image, blend_factor)
                
                temp_image = self.apply_alpha_and_fade(result_image_rgb)
                _, final_buffer_temp = cv2.imencode('.png', temp_image)
                final_base64_image_temp = base64.b64encode(final_buffer_temp).decode('utf-8')
                animation_sequence.append(final_base64_image_temp)
                with open(f'{path}explosion_step_{i}{j}.png', 'wb') as f:
                    f.write(base64.b64decode(final_base64_image_temp))

                # Apply alpha and radial fade to the base image
                base_image_with_alpha = self.apply_alpha_and_fade(base_image)

                # Convert the image with alpha to base64 for final output
                _, final_buffer = cv2.imencode('.png', base_image_with_alpha)
                final_base64_image = base64.b64encode(final_buffer).decode('utf-8')
                #animation_sequence.append(final_base64_image)  # Update the list with the final image
                            
                # Save the image for debugging
            animation_sequences.append(animation_sequence)

        return animation_sequences

# Usage
'''
explosion_animator = ExplosionAnimator(SDendpoint='http://192.168.1.163:7860')
explosion_sequence = explosion_animator.generate_explosion_sequence(
    prompt='A powerful explosion',
    negprompt='',
    steps=35,
    cfg_scale=13.0,
    strength=0.75,
    width=512,
    height=512,
    sampler_name='Euler a',
    iterations=5,
    blend_factor=0.2  # Control the merge process
)
'''