import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os
import secrets
import base64
import getpass
from pathlib import Path
class SecureFolder():
    def __init__(self):
        pass
        
    def hasExistingPassword(self):
        try:
            with open("config/encrypted_master_key.key", "rb") as file:
                file.read()
                return True
             
        except FileNotFoundError:
            return False

    def generate_salt(self,size=16):
        """
        Generate the salt used for key derivation, 
        Args:
            size (int) : the length of the salt to generate
        Returns:
            a random byte string containing *size* bytes.
            
        """
        salt=secrets.token_bytes(size)
        with open("config/salt.salt", "wb") as salt_file:
                salt_file.write(salt)
        return salt
    
    def load_salt(self):
        try:
            with open("config/salt.salt", "rb") as file:
                return file.read()
        except:
            return None
        
    def generate_master_key(self,password):
        """
        Generate a random master key,encrypt(salt,password),store it
        Returns:
            A base64 encoded master key
        """
        self.password=password
        master_key = secrets.token_bytes(32)  # 256-bit key
        master_key_encoded= base64.urlsafe_b64encode(master_key)
        encrypted_master_key = Fernet(self.get_key()).encrypt(master_key_encoded)
        with open("config/encrypted_master_key.key", "wb") as file:
            file.write(encrypted_master_key)


    def validate_password(self,password):
        """
        
        """
        
        self.password=password
        try:
            with open("config/encrypted_master_key.key", "rb") as file:
                encrypted_master_key = file.read()
            master_key=Fernet(self.get_key()).decrypt(encrypted_master_key)
            if master_key:
                return True
             
        except FileNotFoundError:
            #there is no existing master key so this is the first use
            #print("password has been set!")
            return False
        except cryptography.fernet.InvalidToken:
            #print("password is incorrect")
            return False
        
    def get_master_key(self):
        """
        Load and decrypt the master key
        Returns:
            The decrypted master key
        """
        try:
            with open("config/encrypted_master_key.key", "rb") as file:
                encrypted_master_key = file.read()
            return Fernet(self.get_key()).decrypt(encrypted_master_key)
        except FileNotFoundError:
            return False
        except cryptography.fernet.InvalidToken:
            return False

    def generate_key(self,salt):
        """
        Derive the key from the `password` using the passed `salt`
        
        """
        kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
        return base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
    
        
    def get_key(self):
        salt=self.load_salt()
        if salt:
            key=self.generate_key(salt)
        else:
            salt=self.generate_salt()
            key=self.generate_key(salt)
        
        return key
   
    def encrypt(self,filename,password):
        """
        encrypts the file and write over it
        Args:
            filename (str) 
        Returns:
        
        """
        self.password=password
        master_key=self.get_master_key()
        

        if self.validate_password(password):
            f = Fernet(master_key)
            with open(filename, "rb") as file:
                file_data = file.read()
            encrypted_data = f.encrypt(file_data)
            encrypted_filename=os.path.dirname(filename)+'/.'+os.path.basename(filename)+'.ogcrypt'
            with open(encrypted_filename, "wb") as file:
                file.write(encrypted_data)

            os.remove(filename)
            return 1
        return 0
    def decrypt(self,filename,password):
        """
        decrypts the encrypted file and writes over it
        Args:
            filename (str) 
            key (bytes)
        Returns:
        """
        self.password=password
        master_key=self.get_master_key()
        
        
        if self.validate_password(password):
            f = Fernet(master_key)
            with open(filename, "rb") as file:
                encrypted_data = file.read()

            try:
                decrypted_data = f.decrypt(encrypted_data)
            except cryptography.fernet.InvalidToken:
                print("Invalid token, most likely the password is incorrect")
                return
            
            decrypted_filename = Path(filename)
            orig_name = decrypted_filename.with_suffix('')  # Removes the extension .ogcrypt
            orig_name = orig_name.parent / orig_name.name.lstrip('.')  # Removes leading dot

            with open(orig_name, "wb") as file:
                file.write(decrypted_data)
            
            try:
                os.remove(filename)
            except:
                print("couldn't delete encrypted file")
            
            return orig_name
        return 0
    
    


