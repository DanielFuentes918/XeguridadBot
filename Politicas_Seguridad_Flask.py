from flask import Flask, render_template

app = Flask("Politica_Seguridad_Flask")

@app.route('/politica_privacidad')
def politica_privacidad():
    return render_template('PoliticasSeguridad.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
