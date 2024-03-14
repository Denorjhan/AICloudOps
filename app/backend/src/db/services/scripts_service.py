import sys
from pathlib import Path

# Add the parent directory to the Python path (this is a temperary debugging solution)
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    
from orm.models import Scripts
from orm.connection import Session


def insert_script(script_name, script_content):
    session = Session()
    new_script = Scripts(script_name=script_name, script_content=script_content)
    session.add(new_script)
    session.commit()
    session.refresh(new_script)
    session.close()
    return new_script.script_id

def get_all_scripts():
    session = Session()
    scripts = session.query(Scripts).all()
    session.close()
    return scripts

def get_script_content_by_id(script_id):
    session = Session()
    script = session.query(Scripts).filter(Scripts.script_id == script_id).first()
    session.refresh(script)
    session.close()
    return script.script_content
    
