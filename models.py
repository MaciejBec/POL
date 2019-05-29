from application import db


class Category(db.Model):
    """kategorie"""

    __tablename__ = 'category'
    id = db.Column(db.Integer, db.Sequence('category_id_seq'), primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    item = db.relationship('Item', backref='category')

    def __init__(self, name):
        self.name = name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'item': [x.serialize for x in self.item]
        }


class Item(db.Model):
    """itemy"""

    __tablename__ = 'item'
    id = db.Column(db.Integer, db.Sequence('item_id_seq'), primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    description = db.Column(db.String(100), nullable=False, unique=True)
    title = db.Column(db.String(40), nullable=False, unique=True)

    def __init__(self, cat_id, description, title):
        self.cat_id = cat_id
        self.description = description
        self.title = title

    @property
    def serialize(self):
        return {
            'id': self.id,
            'cat_id': self.cat_id,
            'description': self.description,
            'title': self.title
        }
