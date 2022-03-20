from flask import Flask, render_template, request, session, url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect
from flask_marshmallow import Marshmallow
app = Flask(__name__)
app.secret_key="mykey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mabase.sqlite3'
db = SQLAlchemy(app)
ma = Marshmallow(app)
class Students(db.Model):
    cne = db.Column('cne', db.String(50), primary_key = True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(50))
    email = db.Column(db.String(100))
    adresse = db.Column(db.String(200))
    datenaissance = db.Column(db.String(10))

    def __init__(self, cne, nom , prenom , email , adresse , datenaissance):
        self.cne = cne
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.adresse = adresse
        self.datenaissance = datenaissance
    def toJSON(self):
        return {'cne':self.cne,'nom':self.nom,'prenom':self.prenom,'datanaissance':self.datenaissance,'email':self.email,'adresse':self.adresse}

class StudentsSchame(ma.Schema):
    class Meta:
        fields = ('cne','nom','prenom','email','adresse','datanaissance')


class Users(db.Model):
    username = db.Column('username', db.String(100), primary_key = True)
    pwd = db.Column(db.String(100))

    def __init__(self, username, pwd):
        self.username = username
        self.pwd = pwd

# authentification
@app.route('/')
def index():
    if session.get("username"):
        return redirect("/acceuil")
    else:
        return render_template("login.html")

# acceuil
@app.route('/acceuil', methods=['GET','POST'])
def acceuil():
    if request.method == "POST":
        try:
            user =db.session.query(Users).filter_by(username=request.form['username']).first()
            if user.pwd == request.form['pwd']:
                session["username"] = request.form['username']
                return  render_template("index.html",students = Students.query.all())
            else:
                return render_template("login.html", error = "Le mot de passe est incorrecte")
        except:
            return render_template("login.html", error="Identifiant saisit n'existe plus")
    else: #get method
        if not session.get("username"):
            return render_template("login.html",error = "vous devez d'abord se connecter ")
        else:
            if not request.args.get("nom") or not request.args.get("nom"):
                return render_template("index.html" ,students = Students.query.all())
            else:
                student = Students.query.filter_by(cne=request.args.get('cne')).first()
                student.nom = request.args.get("nom")
                student.prenom = request.args.get("prenom")
                student.email = request.args.get("email")   
                student.adresse = request.args.get("adresse")
                student.datenaissance = request.args.get("date")
                db.session.commit()
                return render_template("index.html", res = "bien fait" ,students=Students.query.all())


# ajout
@app.route('/ajouter',methods = ['POST','GET'])
def ajouter():
    if request.method == "POST":
        if not request.form['cne'] or not request.form['nom'] or not request.form['prenom']:
            return render_template("ajouter.html",error = "Remplissez-vous les champs obligatoires")
        try:
            student = Students(request.form['cne'], request.form['nom'], request.form['prenom'], request.form['email'] , request.form['adresse'] , request.form['date'])
            db.session.add(student)
            db.session.commit()
            return render_template("ajouter.html" , res = " bien ajouté")
        except:
            return render_template("ajouter.html", error= "Cne saisi est déja existé")
    else:  # get method
        if not session.get("username"):
            return render_template("login.html", error="vous devez d'abord se connecter ")
        return render_template("ajouter.html")

# modification
@app.route('/modifier/<cnee>' ,methods = ['POST','GET'])
def modifier(cnee):
    if not session.get("username"):
        return redirect("/")
    return  render_template("modifier.html" , student = db.session.query(Students).filter_by(cne=cnee).first() )

@app.route('/supprimer/<cnee>')
def supprimer(cnee):
    if not session.get("username"):
        return render_template("login.html", error="vous devez d'abord se connecter ")
    else:
        db.session.query(Students).filter_by(cne=cnee).delete()
        db.session.commit()
        return render_template("index.html" ,res="bien fait", students=Students.query.all())

# export
@app.route('/exporter')
def exporter():
    if not session.get("username"):
        return render_template("login.html", error="vous devez d'abord se connecter ")
    else:
        students = db.session.query(Students).all()
        output = StudentsSchame().dump(students)
        return jsonify(output)


# logout
@app.route('/logout')
def logout():
    session["username"] = None
    return redirect("/")





if __name__ == '__main__':
    db.create_all()
    db.session.add(Users("admin","admin"))
    app.run()