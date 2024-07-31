import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
    
def validate_name(name):
    pattern = r'^[a-zA-Z]+$'
    return bool(re.match(pattern, name))
    
def validate_full_name(full_name):
    pattern = r'^[a-zA-Z]+ [a-zA-Z]+$'
    return bool(re.match(pattern, full_name))

def validate_container_number(container_number):
    pattern = r'^[A-Z]{4}\d{7}$'
    return bool(re.match(pattern, container_number))

def validate_truck_number(truck_number):
    patterns = [
        r'^[A-Z]\d{4}RB$',                     # Format: A1245RB
        r'^[A-Z]{2}\d{4}RB$',                  # Format: AA1234RB
        r'^[A-Z]\d{4}RB/[A-Z]\d{4}RB$',        # Format: A3345RB/A4567RB
        r'^[A-Z]{2}\d{4}RB/[A-Z]\d{4}RB$',     # Format: AA3345RB/A4567RB
        r'^[A-Z]\d{4}RB/[A-Z]{2}\d{4}RB$',     # Format: A3345RB/AA4567RB
        r'^[A-Z]{2}\d{4}RB/[A-Z]{2}\d{4}RB$',  # Format: AA3345RB/AA4567RB
        r'^[A-Z0-9/-]+$'                       # Exception: alphanumérique avec tirets et barres obliques
    ]
    
    for pattern in patterns:
        if re.match(pattern, truck_number):
            return True
    return False

def validate_phone_number(phone_number):
    pattern = r'^[0-9]{8}$'
    return bool(re.match(pattern, phone_number))

def validate_booking_number(booking_number):
    pattern = r'^[A-Z0-9]{3,10}$'
    return bool(re.match(pattern, booking_number))

def validate_number(value):
    pattern = r'^[-+]?[0-9]*\.?[0-9]+$'
    return bool(re.match(pattern, value))

def validate_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()-_+=])[A-Za-z\d!@#$%^&*()-_+=]{6,}$'
    return bool(re.match(pattern, password))

def validate_contract_number(contract_number):
    pattern = r'^[A-Z0-9/]+$'
    return bool(re.match(pattern, contract_number))
