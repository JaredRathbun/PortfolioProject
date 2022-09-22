import re
import logging as logger
from app import db
from functools import wraps
from flask import session

def is_whitespace(text: str) -> bool:
    '''
    Checks to see if the text specified is whitespace or not.
    
    param: The text to check.
    return: A boolean representing whether or not the text is whitespace.
    '''
    if text is None:
        logger.error('Text given to is_whitespace is None.')
        raise ValueError('Text given to is_whitespace is None.')
    else:
        return bool(re.match('\s+', text))
    

def field_check(data: dict) -> bool:
    '''
    Checks the given dictionary for None or whitespaces using a recursive approach.
    
    param: The data represented in a dictionary to check.
    return: A boolean representing if the dictionary contains valid values or not.
    '''
    # Raise a ValueError is the data is None.
    if data is None:
        raise ValueError('Data is None.')
    else:
        return_res = True
        # Get all keys, then use a recursive check on each.
        keys = data.keys()
        for key in keys:
            if type(data[key]) is dict:
                return field_check(data[key])
            else:
                # Check for a None value or any number of whitespaces.
                return_res = return_res and data[key] is not None and not is_whitespace(data[key])
        return return_res
    
def db_insert(entry: db.Model) -> bool:
    '''
    Inserts an entry into the database. If the entry is None or fails to insert, False is returned.
    
    param: entry The db.Model object to insert into the database.
    returns: A bool representing if the operation was successful or not.
    '''
    
    if entry is None:
        return False
    
    try:
        db.session.add(entry)
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f'Unable to insert entry into database. Reason was: {e}')
        return False

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['user'].is_admin:
            return f(*args, **kwargs)
        else:
            return "Unauthorized", 401
    return decorated_function