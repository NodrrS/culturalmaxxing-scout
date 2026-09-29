"""
#############################################################################
### Validator methods file
###
### @file validators.py
### @Sebastian Russo
### @date: 2025
#############################################################################

This module defines several methods to validate several things.
"""
#Native imports
import re

#Third-party imports
import phonenumbers

#Other files imports
from src.utils.custom_logger import log_handler
from src.core_specs.configuration.config_loader import config_loader
from src.core_specs.data.data_loader import data_loader
from fastapi import HTTPException

def validate_email_format(email: str) -> bool:
    """
        Validate an email address.
        
        local_part@subdomain.domain.tld or example@provider.tld

        Checks if:
        - There is exactly one '@' symbol.
        - The local part is non-empty, contains no '@' and only allowed characters.
        - The domain contains exactly 1 '.' separating provider and TLD.
        - The provider and TLD are in allowed lists from config.

        Args:
            email (str): The email string to validate.

        Returns:
            Nothing, it allows execution and not raise an exception
    """
    
    message = ""
    
    #Check exactly one '@' in the email
    if email.count('@') != 1:
        message=f"Invalid email '{email}': must contain exactly one '@'"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)
    local_part, domain_part = email.rsplit('@', 1)

    #Check local part is not empty and contains only allowed characters
    if not local_part or not re.match(r'^[\w\.-]+$', local_part):
        message=f"Invalid email '{email}': local part is invalid"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)
    
    #Domain must contain exactly one '.'
    if domain_part.count('.') != 1:
        message=f"Invalid email '{email}': domain part must contain exactly one '.'"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)
    provider, tld = domain_part.rsplit('.', 1)

    #Check if provider and tld are allowed
    if provider not in  config_loader["email_validation"]["allowed_providers"]:
        message=f"Invalid email '{email}': provider '{provider}' not allowed"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)
    if tld not in config_loader["email_validation"]["allowed_tlds"]:
        message=f"Invalid email '{email}': TLD '{tld}' not allowed"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)

    log_handler.debug(f"Email '{email}' is valid, proceeding")

def validate_password_format(password: str):
    """
        Validate a password.

        Checks if:
        - At least 8 characters long
        - Contains at least one lowercase letter
        - Contains at least one uppercase letter
        - Contains at least one digit
        - Contains at least one special symbol (non-alphanumeric)

        Args:
            password (str): The password string to validate.

        Returns:
            bool: Nothing, the method does not raise exceptions and allows
            to continue execution
    """

    message = ""

    if len(password) < 8:
        message= "Password length is too short."
        log_handler.warning(message) 
        raise HTTPException(status_code=400, detail=message)

    if not re.search(r"[a-z]", password):
        message= "Password validation failed: no lowercase letter found"
        log_handler.warning(message) 
        raise HTTPException(status_code=400, detail=message)

    if not re.search(r"[A-Z]", password):
        message= "Password validation failed: no uppercase letter found"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)

    if not re.search(r"\d", password):
        message= "Password validation failed: no digit found"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)

    if not re.search(r"[^\w\s]", password):
        message= "Password validation failed: no special symbol found"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)

    log_handler.info("Password is valid") 

def validate_access_token_format(token: str):
    jwt_regex = r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$'
    if not re.fullmatch(jwt_regex, token):
        raise HTTPException(status_code=400, detail="Access token format is invalid.")
    
def validate_refresh_token_format(token: str):
    if not token.isalnum() or len(token) < 10:
        raise HTTPException(status_code=400, detail="Refresh token format is invalid.")

def validate_uuid_format(uuid_str: str):
    uuid_regex = r'^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$'
    if not re.fullmatch(uuid_regex, uuid_str.lower()): #RFC 4122 standard
        raise HTTPException(status_code=400, detail="User ID format is invalid.")

def is_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))

def validate_phone_format(phone: str) -> None:
    """
        Validate a phone number for any country in the world.

        Uses Google's libphonenumber (via the `phonenumbers` package), which
        validates against the real numbering plan of every country/region. To
        be region-agnostic, the number MUST be supplied in E.164 format, i.e.
        a leading '+', the country calling code, then the national number
        (e.g. '+14155552671', '+447911123456', '+5491123456789').

        Checks that:
        - The value parses as an international number (has a valid '+' country code).
        - The number is actually valid for its numbering plan (length, prefix, etc.).

        Args:
            phone (str): The phone number string to validate.

        Returns:
            None. Raises HTTPException(400) when the number is invalid;
            otherwise allows execution to continue.
    """

    #Reject empty/whitespace-only input early
    if not phone or not phone.strip():
        message = "Invalid phone number: value is empty"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)

    #Require E.164 so we can validate without assuming a default region
    if not phone.strip().startswith('+'):
        message = (
            f"Invalid phone number '{phone}': must be in international E.164 "
            f"format with a leading '+' and country code (e.g. +14155552671)"
        )
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)

    #Parse with no default region; the '+' country code identifies the country
    try:
        parsed = phonenumbers.parse(phone.strip(), None)
    except phonenumbers.NumberParseException:
        message = f"Invalid phone number '{phone}': could not be parsed"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)

    #Validate against the country's real numbering plan
    if not phonenumbers.is_valid_number(parsed):
        message = f"Invalid phone number '{phone}': not a valid number for its country"
        log_handler.warning(message)
        raise HTTPException(status_code=400, detail=message)

    log_handler.debug(f"Phone '{phone}' is valid, proceeding")
