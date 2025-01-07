from PIL import Image
import base64
import io

class PropGenerator():
        
    def generateProp(self, props_response_final, threshold=20):
        # TODO - make this as smart as the same method in playgen. 
        new_list = []

        for prop in props_response_final:
            if prop is None or len(prop) < 5:
                continue
            base64_data = prop[4]
            image_data = base64.b64decode(base64_data)
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

            img.putdata(new_data)
            borderlessness = self.check_border_transparency(img)
            
            dimx = dimy = 32 # bogus
            if prop[1] == "small": dimx = dimy = 64
            if prop[1] == "medium": dimx = dimy = 96
            if prop[1] == "large": dimx = dimy = 128
            downsized = img.resize((dimx, dimy), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            downsized.save(buffer, format="PNG")
            processed_base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            new_prop = prop[:4] + [borderlessness] + [processed_base64_data]
            new_list.append(new_prop)
        return new_list
       
    def is_dark(self, pixel, threshold):
        return pixel[0] < threshold and pixel[1] < threshold and pixel[2] < threshold
        
    def check_border_transparency(self,image, tolerance=70):
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
