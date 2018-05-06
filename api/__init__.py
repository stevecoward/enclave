from flask import Flask, jsonify, request
from core.models import Puppet

app = Flask(__name__)


@app.route('/puppets')
def get_unlinked_puppets():
    unlinked = []
    for puppet in Puppet.select().where(Puppet.ip == None):
        unlinked.append({
            'vps': puppet.vps,
            'id': puppet.uuid,
        })
    return jsonify(unlinked)
