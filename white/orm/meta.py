from .base import BaseMapper
from white.ext  import db
from white.model import Meta
from flask.json import loads, dumps

class MetaMapper(BaseMapper):

    model = Meta
    table = 'meta'

    def find(self, type, node_id, extend_id):
        data = (db.select(self.table).fields('node_id', 'type', 'extend', 'data', 'mid')
            .condition('type', type)
            .condition('node_id', node_id)
            .condition('extend',  extend_id)
            .execute())
        if data:
            return self.load(data[0])

    def load(self, data):
        data = list(data)
        try:
            data[3] = loads(data[3])
        except:
            data[3] = dict()
        return BaseMapper.load(self, data, self.model)

    def create(self, meta):
        data = dumps(meta.data)
        return (db.insert(self.table).fields('node_id', 'type', 'extend', 'data')
            .values((meta.node_id, meta.type, meta.extend, data)).execute())

    def save(self, meta):
        data = dumps(meta.data)
        return (db.update(self.table).mset(
            dict(node_id=meta.node_id,
                type=meta.type,
                extend=meta.extend,
                data=data)).condition('mid', meta.mid).execute())

    def delete(self, meta):
        return db.delete(self.table).codition('mid', meta.mid)