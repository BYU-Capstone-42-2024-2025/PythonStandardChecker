import json
from typing import Callable

class FileHandler(object):
    """Singleton that opens and stores json files."""    
    def __new__(cls) -> 'FileHandler':
        """Creates a new instance if first. Otherwise, uses the first instance, as this is a singleton."""        
        if not hasattr(cls, 'instance'):
            cls.instance = super(FileHandler, cls).__new__(cls)
        return cls.instance
  
    def getFileData(self, filePath:str, convertTypeFunc:Callable|None = None, expectedType:object|None = None) -> object:
        """Accesses the attribute of the singleton for already accessed objects, and opens and accesses the json objects if not.

        Args:
            filePath (str): the file path
            convertTypeFunc (Callable | None, optional): function that converts the fileData to the desired type; defaults to None
            expectedType (object | None, optional): the expected type of fileData. This doesn't matter unless convertTypeFunc is set because; defaults to None

        Returns:
            object: the file data
        """        
        fileData = None
        if hasattr(self, filePath):
            fileData = getattr(self, filePath)
        else:
            with open(filePath, 'r', encoding='utf-8') as file:
                fileData = json.load(file)
            setattr(self, filePath, fileData)
        if (convertTypeFunc is not None) and (type(fileData) != expectedType):
            fileData = convertTypeFunc(fileData)
        return fileData