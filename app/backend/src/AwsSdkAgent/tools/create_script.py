import os
from typing import List
from pydantic import Field
from agency_swarm import BaseTool
import time

import sys
from pathlib import Path

# Add the parent directory to the Python path (this is a temperary debugging solution)
parent_dir = str(Path(__file__).resolve().parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from db.services.scripts_service import insert_script, get_all_scripts, get_script_content_by_id
from db.services.vectors_service import insert_vector, create_embedding


class File(BaseTool):
    """
    File to be written to the disk with an appropriate name and file path, containing code that can be saved and executed locally at a later time.
    """
    file_name: str = Field(
        ...,
        description="The name of the file including the extension and the file path from your current directory if needed."
    )
    body: str = Field(..., description="Correct contents of a file based on the CodeQualityStandards given in your instructions.")

    def run(self):
        
        print ("###############")
        start = time.time()
        script_id = insert_script(self.file_name, self.body)
        end = time.time()
        print(f"Time taken to insert script: {end - start}")
        
        start = time.time()
        embedding = create_embedding(self.body)
        end = time.time()
        print(f"Time taken to create embedding: {end - start}")
        
        start = time.time()
        insert_vector(script_id, embedding)
        end = time.time()
        print(f"Time taken to insert vector: {end - start}")
        
        return f"File written to ##{self.file_name} with script_id: ##{script_id}"
        
        


class CreateScript(BaseTool):
    """
    Set of files that represent a complete and correct program.
    """
    chain_of_thought: str = Field(...,
                                  description="Think step by step to determine the correct actions that are needed to implement the program based on the CodeQualityStandards given in yourinstructions.")
    files: List[File] = Field(..., description="List of files")

    def run(self):
        outputs = []
        for file in self.files:
            outputs.append(file.run())

        return str(outputs)
    
# create an instance of File
f = File(file_name="hi_wor.py", body="print('hi')")
f.run()
