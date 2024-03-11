from db.orm.models import Scripts
from db.orm.connection import Session


def insert_script(script_name, script_content):
    session = Session()
    new_script = Scripts(script_name=script_name, script_content=script_content)
    session.add(new_script)
    session.commit()
    session.close()
    return new_script

def get_all_scripts():
    session = Session()
    scripts = session.query(Scripts).all()
    session.close()
    return scripts

t = get_all_scripts()
print(t)