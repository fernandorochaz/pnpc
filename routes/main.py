from flask import Blueprint, jsonify, render_template
from models.models import UF, Modalidade, Municipio, UnidadeAdministrativa

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/get_ufs')
def get_ufs():
    ufs = UF.query.all()
    return jsonify([{ "id": uf.id, "sigla": uf.sigla, "nome": uf.nome } for uf in ufs])

@main.route('/get_modalidades')
def get_modalidades():
    modalidades = Modalidade.query.all()
    return jsonify([{ "codigo": m.codigo, "descricao": m.descricao } for m in modalidades])

@main.route('/get_municipios/<int:uf_id>')
def get_municipios(uf_id):
    municipios = Municipio.query.filter_by(uf_id=uf_id).all()
    return jsonify([{ "codigo_ibge": m.codigo_ibge, "nome": m.nome } for m in municipios])

@main.route('/get_unidades')
def get_unidades():
    unidades = UnidadeAdministrativa.query.all()
    return jsonify([{ "codigo": u.codigo, "nome": u.nome } for u in unidades])
