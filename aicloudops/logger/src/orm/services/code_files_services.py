import hashlib
from orm.database import Session
from orm.models.code_files import CodeFiles

#TODO: move method to utils dir
def hash_file(file_path):
    try:
        print("Hashing file")
        #read the file in chunks of 4096 bytes. This is to handle large files
        with open(file_path, 'rb') as file:
            chunk = file.read(4096)
            hash_obj = hashlib.sha256()
            
            #loop through the file and update the hash object based on the chunks
            while chunk:
                hash_obj.update(chunk)
                chunk = file.read(4096)
                
            return hash_obj.hexdigest()
    except Exception as e:
        print(f"Error hashing file: {str(e)}")
    
    
def insert_code_file(file_path: str):
    try:
        print("Inserting code file")
        file_hash = hash_file(file_path)
        
        # perfrom insert
        with Session() as session:
            new_file = CodeFiles(file_path=file_path, file_hash=file_hash) 
            session.add(new_file)  
            session.commit()  
            id = new_file.file_id
        
        #return the file_id from the inserted record
        return id
    
    except Exception as e:
        print(f"Error inserting code file: {str(e)}")
        
