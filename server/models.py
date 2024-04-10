from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship. First arg in parens is the class name to which you are relating. Second arg is back_populates which points to the relationship attribute in the other class to which you are relating (seems to be lowercase name of the current class...). Third arg is cascading delete if applicable.
    #cascading delete here is such that when a Restaurant is deleted, all of its restaurant_pizzas are also deleted.
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', 
        back_populates='restaurant', 
        cascade ='all, delete-orphan'
    )

    # add serialization rules
    # pattern of note - items inside of the list below are relationshipattribute.back_populates.
    serialize_rules = ['-restaurant_pizzas.restaurant']

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza')

    # add serialization rules
    serialize_rules = ['-restaurant_pizzas.pizza']

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id')) #foreign keys are tablename.column
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    # add relationships
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')

    # add serialization rules
    serialize_rules = ['-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas']

    # add validation
    #validates(item that is getting validated), third person. self, key, and new_value are params.
    #validation imported above from sqlalchemy.orm
    @validates('price')
    def validates_price(self,key,new_price):
        if not (1 <= new_price <= 30):
            raise ValueError('Price must be between 1 and 30.')
        else:
            return new_price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
