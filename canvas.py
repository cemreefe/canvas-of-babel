import numpy as np
from PIL import Image
import math
import random
import io
from base64 import b64encode


class Canvas:

    def __init__(self, color_steps=8, image_shape=(64,64,3)):
        assert len(image_shape)
        self.color_steps = color_steps
        self.encoding_base = color_steps
        self.image_shape = image_shape
        self.num_colors = color_steps**image_shape[2]
        self.num_vals = int(np.prod(image_shape))
        self.num_images = color_steps**int(np.prod(image_shape))-1
        self.encoding_string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.save_size = (256, 256)

    def get_min_id(self):
        return self.encoding_string[0] * self.num_vals

    def get_max_id(self):
        # alternative
        # max_id = np.base_repr(self.num_images-1, base=self.encoding_base)
        return self.encoding_string[self.encoding_base-1] * self.num_vals 

    def get_random_id(self):
        id = ''
        for _ in range(self.num_vals):
            id += self.encoding_string[random.randint(0, self.encoding_base-1)]
        return id

    def id_to_image(self, id):
        img = np.zeros(self.num_vals)
        for i, c in enumerate(id[::-1]):
            img[-i-1] = int(c, self.color_steps)*(1/self.color_steps)
        img = np.reshape(img, self.image_shape)
        return img

    def image_to_id(self, img):
        flat = np.reshape(img, (self.num_vals))
        chars = []
        for val in flat:
            c = hex(int(math.floor(val * self.color_steps)))[-1]
            chars.append(c)
        id = ''.join(chars)
        return id
    
    def image_from_file(self, impath):
        example_im = Image.open(impath)
        example_im.thumbnail(self.image_shape[:2])
        example_np = np.array(example_im)[:,:,:3]/256
        return example_np

    def image_to_file(self, im, impath):
        im = Image.fromarray((im * 255).astype(np.uint8))
        im = im.resize(self.save_size, resample=Image.NEAREST)
        im.save(impath)

    def image_to_byteobject(self, img):
        img = Image.fromarray(((img) * 255).astype(np.uint8))
        img = img.resize(self.save_size, resample=Image.NEAREST)

        # create file-object in memory
        image_io = io.BytesIO()

        # write PNG in file-object
        img.save(image_io, 'PNG')

        # move to beginning of file so `send_file()` it will read from start    
        image_io.seek(0)

        image_url = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')

        return image_url

    def id_math_add(self, id, c):
        integer_value = int(id, self.encoding_base)
        print(">mod")
        integer_value %= int(self.get_max_id(), self.encoding_base)
        print("<mod")
        new_value = np.base_repr(integer_value+c, base=self.encoding_base)
        return new_value

    def check_id_valid(self, id):
        try:
            integer_value = int(id, self.encoding_base)
            assert 0 <= integer_value <= self.num_images
            return True
        except Exception as e: 
            print('>>', str(e))
            return False

    def filestorage_to_np_image(self, fs):
        #convert string data to numpy array
        img = Image.open(fs)
        img = img.crop_to_aspect(*self.image_shape[:2])
        img.thumbnail(self.image_shape[:2])
        img = np.array(img)[:,:,:3]/256
        return img


########

class _Image(Image.Image):

    def crop_to_aspect(self, aspect, divisor=1, alignx=0.5, aligny=0.5):
        """Crops an image to a given aspect ratio.
        Args:
            aspect (float): The desired aspect ratio.
            divisor (float): Optional divisor. Allows passing in (w, h) pair as the first two arguments.
            alignx (float): Horizontal crop alignment from 0 (left) to 1 (right)
            aligny (float): Vertical crop alignment from 0 (left) to 1 (right)
        Returns:
            Image: The cropped Image object.
        """
        if self.width / self.height > aspect / divisor:
            newwidth = int(self.height * (aspect / divisor))
            newheight = self.height
        else:
            newwidth = self.width
            newheight = int(self.width / (aspect / divisor))
        img = self.crop((alignx * (self.width - newwidth),
                         aligny * (self.height - newheight),
                         alignx * (self.width - newwidth) + newwidth,
                         aligny * (self.height - newheight) + newheight))
        return img

Image.Image.crop_to_aspect = _Image.crop_to_aspect