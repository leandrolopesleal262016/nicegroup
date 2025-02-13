from apps.extensions import db

class BaseModel(db.Model):
    __abstract__ = True
    
    def save(self):
        db.session.add(self)
        db.session.commit()