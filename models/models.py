from config.database import db

class UF(db.Model):
    __tablename__ = 'ufs'
    id = db.Column(db.Integer, primary_key=True)
    sigla = db.Column(db.String(2), nullable=False, unique=True)
    nome = db.Column(db.String(100), nullable=False)

class Modalidade(db.Model):
    __tablename__ = 'modalidades'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.Integer, nullable=False, unique=True)
    descricao = db.Column(db.String(255), nullable=False)

class Municipio(db.Model):
    __tablename__ = 'municipios'
    id = db.Column(db.Integer, primary_key=True)
    codigo_ibge = db.Column(db.Integer, nullable=False, unique=True)
    nome = db.Column(db.String(255), nullable=False)
    uf_id = db.Column(db.Integer, db.ForeignKey('ufs.id'), nullable=False)

class UnidadeAdministrativa(db.Model):
    __tablename__ = 'unidades_administrativas'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), nullable=False, unique=True)
    nome = db.Column(db.String(255), nullable=False)
