from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import pytz
from datetime import datetime

from sqlalchemy import func

# Créez une instance de SQLAlchemy (cette instance est importée et utilisée dans app.py)
db = SQLAlchemy()

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    active_session_token = db.Column(db.String(120), nullable=True)
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    
    # Dans le modèle User
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    # Implement UserMixin properties
    @property
    def is_active(self):
        # For simplicity, assume all users are active
        return True

    @property
    def is_authenticated(self):
        # For simplicity, assume all users are authenticated
        return True

    @property
    def is_anonymous(self):
        # We assume that users are not anonymous in this system
        return False

    # Required for Flask-Login to get user by id
    def get_id(self):
        return str(self.id)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class LogAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('actions', lazy=True))
    username = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    action = db.Column(db.String(100), nullable=False)
    entry_code = db.Column(db.String(20), nullable=True) 

# Table des clients
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)  # ID du client (clé primaire)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.String(255))
    product = db.Column(db.String(100))  # Produit associé au client
    plant = db.Column(db.String(100))    # Usine associée au client
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Africa/Porto-Novo')))
    created_by = db.Column(db.String(255), nullable=False)

    # Relation one-to-many avec les contrats
    contracts = db.relationship('Contract', backref='customer', lazy=True)

    def get_contracts_bookings_containers(self):
        # Récupère tous les contrats associés au client
        contracts = Contract.query.filter_by(customer_id=self.id).all()
        results = []

        for contract in contracts:
            # Pour chaque contrat, récupère les réservations associées
            bookings = Booking.query.filter_by(contract_id=contract.id).all()
            for booking in bookings:
                # Pour chaque réservation, récupère les conteneurs associés
                containers = Container.query.filter_by(booking_id=booking.id).all()
                for container in containers:
                    # Récupère le poids net du conteneur
                    weight = Weight.query.filter_by(container_id=container.id).first()
                    net_weight = weight.net_weight if weight else None
                    weight_date = weight.weight_date if weight else None

                results.append({
                    'contract_number': contract.contract_number,
                    'plant': contract.plant,
                    'product': contract.product,
                    'booking_name': booking.booking_name,
                    'container_name': container.container_name,
                    'arrival_date': container.arrival_date,
                    'truck_number': container.truck_number,
                    'net_weight': net_weight,
                    'weight_date': weight_date
                })

        return results
    
    
    def __repr__(self):
        return f'<Customer {self.name}>'


class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ID du contrat (clé primaire)
    plant = db.Column(db.String(128), nullable=False)  # Usine associée au contrat
    product = db.Column(db.String(128), nullable=False)  # Produits du contrat
    contract_number = db.Column(db.String(255), nullable=False, unique=True)  # Numéro du contrat
    bag_type = db.Column(db.String(128), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)  # Référence vers le client (clé étrangère)
    shipment_start_date = db.Column(db.Date, nullable=False)  # Date de début de l'expédition
    shipment_end_date = db.Column(db.Date, nullable=False)  # Date de fin de l'expédition
    destination = db.Column(db.String(128), nullable=False)  # Destination de l'expédition
    contract_qty = db.Column(db.Integer, nullable=False)  # Quantité contractuelle
    booking_planned = db.Column(db.Integer, nullable=False)  # Quantité contractuelle    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Africa/Porto-Novo')))
    created_by = db.Column(db.String(255), nullable=False)
    booking_loaded = db.Column(db.Integer, nullable=True)
    quantity_loaded = db.Column(db.Float, nullable=True)
    # Relations avec les autres tables
    payment_info = db.relationship('PaymentInfo', uselist=False, backref='contract')
    date_info = db.relationship('DateInfo', uselist=False, backref='contract')
    remarks_info = db.relationship('RemarksInfo', uselist=False, backref='contract')

    # Relation avec la table Booking
    bookings = db.relationship('Booking', backref='contract', lazy=True)

    def __repr__(self):
        return f'<Contract {self.contract_number}>'

    def update_booking_stats(self):
        # Met à jour le nombre de bookings chargés
        self.booking_loaded = db.session.query(func.count(Booking.id)).filter(Booking.contract_id == self.id).scalar()

        # Met à jour la quantité chargée en utilisant quantity_loaded des Bookings
        self.quantity_loaded = db.session.query(func.coalesce(func.sum(Booking.quantity_loaded), 0)).filter(Booking.contract_id == self.id).scalar()

        db.session.commit()  # Assurez-vous de commettre les modifications après mise à jour des statistiques
        
    def get_total_containers(self):
        # Calcule le nombre total de conteneurs pour ce contrat
        return db.session.query(func.count(Container.id)).\
            join(Booking).\
            filter(Booking.id == Container.booking_id).\
            filter(Booking.contract_id == self.id).\
            scalar()

    @property
    def status(self):
        # Calcul le statut en temps réel
        self.update_booking_stats()  # Assurez-vous que les statistiques sont à jour
        if self.booking_loaded < self.booking_planned:
            return 'In Progress'
        elif self.booking_loaded == self.booking_planned:
            return 'Completed'
        else:
            return 'Invalid State'     

# Table des contrats
 
# Table pour les informations de paiement
class PaymentInfo(db.Model):
    __tablename__ = 'payment_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False, unique=True)
    payment_term = db.Column(db.String(128), nullable=True)  # Conditions de paiement
    price = db.Column(db.String(128), nullable=True)  # Prix


# Table pour les dates importantes
class DateInfo(db.Model):
    __tablename__ = 'date_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False, unique=True)
    contract_copy_date = db.Column(db.Date, nullable=True)  # Date de copie du contrat
    signed_contract_date = db.Column(db.Date, nullable=True)  # Date de signature du contrat
    si1_date = db.Column(db.Date, nullable=True)  # Date SI 1
    si2_date = db.Column(db.Date, nullable=True)  # Date SI 2
    si3_date = db.Column(db.Date, nullable=True)  # Date SI 3
    lc_date = db.Column(db.Date, nullable=True)  # Date LC

# Table pour les remarques
class RemarksInfo(db.Model):
    __tablename__ = 'remarks_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False, unique=True)
    first_remarks = db.Column(db.String(128), nullable=True)  # Premières remarques
    second_remarks = db.Column(db.String(128), nullable=True)  # Deuxièmes remarques
    ad_created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Africa/Porto-Novo')))
    ad_created_by = db.Column(db.String(255), nullable=True)

# Table des freight forwarders
class FreightForwarder(db.Model):
    __tablename__ = 'freight_forwarders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ID du transitaire (clé primaire)
    name = db.Column(db.String(128), nullable=False)  # Nom du transitaire
    tel = db.Column(db.String(128), nullable=True)  # Téléphone du transitaire
    bookings = db.relationship('Booking', backref='freight_forwarder', lazy=True)
    freight_created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Africa/Porto-Novo')))
    freight_created_by = db.Column(db.String(255), nullable=False)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant = db.Column(db.String(128), nullable=False)
    product = db.Column(db.String(128), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    booking_name = db.Column(db.String(128), nullable=False , unique=True)
    bag_type = db.Column(db.String(128), nullable=False)
    container_planned = db.Column(db.Integer, nullable=False)
    quantity_planned = db.Column(db.Integer, nullable=False)
    booking_created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Africa/Porto-Novo')))
    booking_created_by = db.Column(db.String(255), nullable=False)
    container_loaded = db.Column(db.Integer, nullable=True)
    quantity_loaded = db.Column(db.Float, nullable=True)

    freight_forwarder_id = db.Column(db.Integer, db.ForeignKey('freight_forwarders.id'), nullable=False)

    containers = db.relationship('Container', back_populates='booking', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Booking {self.booking_name}>'

    def update_container_stats(self):
        # Met à jour le nombre de conteneurs chargés
        self.container_loaded = db.session.query(func.count(Container.id)).filter(Container.booking_id == self.id).scalar()
        
        # Met à jour la quantité chargée en utilisant net_weight de Weight
        self.quantity_loaded = db.session.query(func.coalesce(func.sum(Weight.net_weight), 0)).join(Container).filter(Container.booking_id == self.id).scalar()

        db.session.commit()  # Assurez-vous de commettre les modifications après mise à jour des statistiques

    @property
    def status(self):
        # Calcul le statut en temps réel
        self.update_container_stats()  # Assurez-vous que les statistiques sont à jour
        if self.container_loaded < self.container_planned:
            return 'In Progress'
        elif self.container_loaded == self.container_planned:
            return 'Completed'
        else:
            return 'Invalid State'  # Cas improbable mais géré pour la cohérence

    def save(self):
        # Méthode pour sauvegarder les modifications et mettre à jour les statistiques
        self.update_container_stats()
        db.session.add(self)
        db.session.commit()
        
class Container(db.Model):
    __tablename__ = 'containers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    arrival_date = db.Column(db.Date, nullable=False)
    truck_number = db.Column(db.String(128), nullable=False)
    container_name = db.Column(db.String(128), nullable=False, unique=True)
    plant = db.Column(db.String(128), nullable=False)
    product = db.Column(db.String(128), nullable=False)
    freight_forwarder = db.Column(db.String(128), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    container_tare = db.Column(db.Integer, nullable=False)
    bags_type = db.Column(db.String(128), nullable=False)
    container_created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Africa/Porto-Novo')))
    container_created_by = db.Column(db.String(255), nullable=False)

    # Relations
    booking = db.relationship('Booking', back_populates='containers')
    loading = db.relationship('Loading', uselist=False, backref='container')
    seal = db.relationship('Seal', uselist=False, backref='container')
    weight = db.relationship('Weight', uselist=False, backref='container')

    def __repr__(self):
        return f'<Container {self.container_name}>'

    def get_status(self):
        if self.loading is None:
            return 'In Loading'
        elif self.seal is None:
            return 'Waiting for Seal'
        elif self.weight is None:
            return 'Waiting for Weight'
        else:
            return 'Completed'

# Table pour les informations de chargement
class Loading(db.Model):
    __tablename__ = 'loading'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id'), nullable=False, unique=True)
    no_of_bags = db.Column(db.Integer, nullable=True)  # Nombre de sacs
    labor = db.Column(db.String(128), nullable=True)  # Travail manuel
    loading_created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Africa/Porto-Novo')))
    loading_created_by = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Loading {self.id}>'

# Table pour les informations de scellé
class Seal(db.Model):
    __tablename__ = 'seal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id'), nullable=False, unique=True)
    seal_image = db.Column(db.String(128), nullable=True)
    seal_number = db.Column(db.String(128), nullable=True, unique=True)  # Numéro du scellé
    seal_date = db.Column(db.Date, nullable=True)  # Date du scellé
    seal_created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Africa/Porto-Novo')))
    seal_created_by = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Seal {self.seal_number}>'

# Table pour les informations de poids
class Weight(db.Model):
    __tablename__ = 'weight'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id'), nullable=False, unique=True)
    gross_weight = db.Column(db.Float, nullable=True)  # Poids brut
    tare_weight = db.Column(db.Float, nullable=True)  # Poids de tare
    net_weight = db.Column(db.Float, nullable=True)  # Poids net
    ws_number = db.Column(db.String(128), nullable=True)  # Numéro WS
    ws_image = db.Column(db.String(128), nullable=True)  # Image WS
    weight_date = db.Column(db.Date, nullable=True)  # Date de pesée
    weight_created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Africa/Porto-Novo')))
    weight_created_by = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Weight {self.id}>'
    
    
    
    
    
#--------------------------LOCALES SALES OPERATIONS --------------------------------

class SalesTruckDriverInfo(db.Model):
    __tablename__ = 'truck_driver_info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    truck_number = db.Column(db.String(50), nullable=False)
    arrival_date = db.Column(db.Date, nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    driver_phone_number = db.Column(db.String(20), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with LoadingInfo
    loading_info = db.relationship("SalesLoadingInfo", uselist=False, back_populates="truck", cascade="all, delete-orphan")

    # Relationship with WeightInfo
    weight_info = db.relationship("SalesWeightInfo", uselist=False, back_populates="truck", cascade="all, delete-orphan")

    def __repr__(self):
        return (f"<SalesTruckDriverInfo(id={self.id}, truck_number={self.truck_number}, "
                f"arrival_date={self.arrival_date}, driver_name={self.driver_name}, "
                f"driver_phone_number={self.driver_phone_number}, company={self.company}, "
                f"created_by={self.created_by}, created_at={self.created_at})>")

class SalesLoadingInfo(db.Model):
    __tablename__ = 'loading_info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck_driver_info.id'), nullable=False)
    bag_type = db.Column(db.String(50), nullable=False)
    no_of_bags = db.Column(db.Integer, nullable=False)
    labour_contract = db.Column(db.String(100), nullable=False)
    loading_date = db.Column(db.Date, nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(100), nullable=False)
    
    # Relationship with TruckDriverInfo
    truck = db.relationship("SalesTruckDriverInfo", back_populates="loading_info")

    def __repr__(self):
        return (f"<SalesLoadingInfo(id={self.id}, truck_id={self.truck_id}, bag_type={self.bag_type}, "
                f"no_of_bags={self.no_of_bags}, labour_contract={self.labour_contract}, "
                f"loading_date={self.loading_date}, destination={self.destination}, "
                f"created_at={self.created_at}, created_by={self.created_by})>")

class SalesWeightInfo(db.Model):
    __tablename__ = 'weight_info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck_driver_info.id'), nullable=False)
    gross_weight = db.Column(db.Float, nullable=False)
    tare_weight = db.Column(db.Float, nullable=False)
    net_weight = db.Column(db.Float, nullable=False)
    ws_number = db.Column(db.String(50), nullable=False)
    ws_image = db.Column(db.String)  # Assuming it's a URL or path to the image
    weight_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(100), nullable=False)
    
    # Relationship with TruckDriverInfo
    truck = db.relationship("SalesTruckDriverInfo", back_populates="weight_info")

    def __repr__(self):
        return (f"<SalesWeightInfo(id={self.id}, truck_id={self.truck_id}, gross_weight={self.gross_weight}, "
                f"tare_weight={self.tare_weight}, net_weight={self.net_weight}, ws_number={self.ws_number}, "
                f"ws_image={self.ws_image}, weight_date={self.weight_date}, "
                f"created_at={self.created_at}, created_by={self.created_by})>")
