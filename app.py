from flask import Flask, redirect, render_template, url_for, send_file, request
from werkzeug.utils import secure_filename
from canvas import Canvas
from encoding import EncodeHelper

configs = {
    'color_steps' : 8,
    'image_shape' : (64,64,3),
    'source_base' : 8,
}

app = Flask(__name__)
canvas = Canvas(
    color_steps=configs['color_steps'], 
    image_shape=configs['image_shape']
)

configs['num_colors'] = canvas.num_colors

encode_helper = EncodeHelper(
    source_base=configs['source_base']
)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

@app.route("/")
def home():
    context={
        'configs' : configs
    }
    return render_template('home_page.html', context=context)

@app.route('/gallery/<id>')
def gallery_page(id):
    # check id validity
    if not canvas.check_id_valid(id):
        return redirect(url_for('home'))
    # pad id
    if len(id) != canvas.num_vals:
        id = id.zfill(canvas.num_vals)
        return redirect(url_for('gallery_page', id = id))
    image = canvas.id_to_image(id)
    image_url = canvas.image_to_byteobject(image)
    context = {
        'id' : id, #encode_helper.encode_id(id, target_word_size=6),
        'image_url' : image_url,
        # 'prev' : canvas.id_math_add(id, -1),
        # 'next' : canvas.id_math_add(id, 1),
        'configs' : configs
    }
    return render_template('gallery_page.html', context=context)

@app.route("/gallery/nextof/<id>")
def nextof(id):
    next = canvas.id_math_add(id, 1)
    return redirect(url_for('gallery_page', id = next)) 

@app.route("/gallery/prevof/<id>")
def prevof(id):
    prev = canvas.id_math_add(id, -1)
    return redirect(url_for('gallery_page', id = prev)) 

@app.route("/gallery/random")
def random():
    id = canvas.get_random_id()
    return redirect(url_for('gallery_page', id = id))

@app.route("/gallery/max")
def max():
    id = canvas.get_max_id()
    return redirect(url_for('gallery_page', id = id))

@app.route("/gallery/min")
def min():
    id = canvas.get_min_id()
    return redirect(url_for('gallery_page', id = id))

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
        #read image file string data
        fs = request.files['file']
        img = canvas.filestorage_to_np_image(fs)
        id = canvas.image_to_id(img)
        return redirect(url_for('gallery_page', id = id))
