from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
  return render_template('home.html')


@app.route('/eventos')
def eventos():
  return render_template('eventos.html')


@app.route('/contenido')
def contenido():
  return "Contenido page content here"


@app.route('/miembros')
def miembros():
  return "Miembros page content here"


@app.route('/galeria')
def galeria():
  return "Galería page content here"


@app.route('/formatos')
def formatos():
  return render_template('formatos.html')


@app.route('/contacto')
def contacto():
  return render_template('contacto.html', enctype="multipart/form-data")


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
