# CODE FOR VALIDATING IPV4 ADDRESS FROM https://www.geeksforgeeks.org/python-program-to-validate-an-ip-address/
import re
class AddressValidator:
    # Make a regular expression 
    # for validating an Ip-address 
    regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
                25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
                25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
                25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''
        
    # Define a function for 
    # validate an Ip addess 
    def __init__(self):
        pass


    def check(self, Ip):  
    
        # pass the regular expression 
        # and the string in search() method 
        if(re.search(AddressValidator.regex, Ip)):  
            return True
            
        else:  
            return False
      