from white.ext  import db


class BaseMapper(object):

    def load(self, data, o):
        return o(*data)


class PrimaryTrait(object):

    primary_id = 'id'

    def find(self, id):
        q = db.select(self.table).condition(self.primary_id, id)
        data = q.query()
        if data:
            return self.load(data[0], self.model)