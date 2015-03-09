from .base import BaseMapper
from white.ext  import db
from white.model import Extend, Field

from flask.json import loads, dumps

class ExtendMapper(BaseMapper):

    model = Extend
    table = 'extend'

    def find(self, eid):
        """Find and load the extend from database by eid(extend id)"""
        data = (db.select(self.table).fields('type', 'key', 'label', 'field', 'attributes', 'eid').
            condition('eid', eid).execute())
        if data:
            return self.load(data[0])

    def find_by_type(self, type):
        """Find and load the extend from database by eid(extend id)"""
        data = (db.select(self.table).fields('type', 'key', 'label', 'field', 'attributes', 'eid').
            condition('type', type).execute())
        return [ self.load(_) for _ in data]

    def paginate(self, page=1, perpage=10):
        data = db.select(self.table).fields('type', 'key', 'label', 'field', 'attributes', 'eid').limit(perpage).offset((page -1) * perpage).execute()
        return [ self.load(_) for _ in data]

    def load(self, data):
        data = list(data)
        try:
            data[4] = loads(data[4])
        except:
            data[4] = dict()
        return BaseMapper.load(self, data, self.model)

    def field(self, type, key, eid= -1):
        field = db.select(self.table).fields('type', 'key', 'label', 'field', 'attributes', 'eid').condition('type', type).condition('key', key).execute()
        if field:
            return self.load(field[0])

    def count(self, **kw):
        q = db.select(self.table).fields(db.expr('COUNT(*)'))
        if kw:
            for k, v in kw.iteritems():
                q.condition(k, v)
        return q.execute()[0][0]


    def create(self, extend):
        """Create a new extend"""
        attributes = dumps(extend.attributes)
        return db.execute('INSERT INTO extend (`type`, `label`, `field`, `key`, `attributes`) VALUES (%s, %s, %s, %s, %s)',
                          (extend.type, extend.label, extend.field, extend.key, attributes))

    def save(self, extend):
        """Save and update the extend"""
        attributes = dumps(extend.attributes)
        return (db.update(self.table).
                mset(dict(type=extend.type,
                    label=extend.label,
                    key=extend.key,
                    attributes=attributes,
                    field=extend.field))
                .condition('eid', extend.eid).execute())

    def delete(self, extend):
        """Delete category by extend"""
        return db.delete(self.table).condition('eid', extend.eid).execute()