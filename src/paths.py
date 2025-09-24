from pathlib import Path
import configparser
import os


# Read the configuration file
config = configparser.ConfigParser()

scriptDirectory = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(scriptDirectory, '..', 'res', 'paths.ini')

config.read(configPath)


# Classes
class DynamicPath:
    def __init__(self, path: str, variables: list[str] = []):       # TODO: [2] Implement another contructor that takes in a config, section, and key                          
        self.__rawPath: str = path.strip('"' + "'")                 # Remove quotes
        self.__path: Path = Path(self.__rawPath) if self.exists else None
        self.__variables: set[str] = set(variables)
    
    def __call__(self, *args, **kwargs):
        """
        Assign values to the variables in the path and return a Path.
        You can use positional arguments (in variable order) or keyword arguments (by variable name).
        """
        # Use kwargs if provided, 
        if kwargs:
            if set(kwargs.keys()) != self.variables:    raise ValueError(f"Keyword arguments must match variables: {self.variables}")

            for var in self.variables:
                self.__path = Path(self.__rawPath.replace(f"<{var}>", str(kwargs[var])))
        
        # Otherwise use args
        else:
            if len(args) != self.missing:   raise ValueError("Incorrect number of arguments")
            elif       0 == self.missing:   return self.path
                    
            for var, value in zip(self.__variables, args):
                self.__path = Path(self.__rawPath.replace(f"<{var}>", str(value)))

        # Return the final path
        return self.__path
        

    @property
    def raw(self) -> str:               return self.__rawPath
    @property 
    def path(self) -> Path:             return self.__path          # TODO: [1] Take in parameters for variables incase the path contains variables.
    @property
    def variables(self) -> list[str]:   return self.__variables
    @property
    def missing(self) -> int:           return len(self.__variables)
    @property
    def exists(self) -> bool:           return os.path.exists(self.__rawPath)
    

    def listdir(self) -> tuple[str]:
        """
        List the directory at this path. Mimics os.listdir. Use `DynamicPath.content()` to get Path objects instead.
        """
        if not self.exists: raise FileNotFoundError(f"The path '{self.__path}' does not exist. Try assigning variables if applicable using the call method.")

        return tuple(entry.name for entry in self.path.iterdir())

    def content(self) -> tuple[Path]:
        """
        Returns a list of all the files and directories as Path objects at this path.
        """
        if not self.exists: raise FileNotFoundError(f"The path '{self.__path}' does not exist. Try assigning variables if applicable using the call method.")
        
        return tuple(self.path.iterdir())
    
    def dirs(self) -> tuple[Path]:
        """
        Returns a list of only directories at this path.  
        """
        if not self.exists: raise FileNotFoundError(f"The path '{self.__path}' does not exist. Try assigning variables if applicable using the call method.")

        return tuple(entry for entry in self.path.iterdir() if entry.is_dir())

    def files(self) -> tuple[str]:
        """
        Returns a list of only files at this path.  
        """
        if not self.exists: raise FileNotFoundError(f"The path '{self.__path}' does not exist. Try assigning variables if applicable using the call method.")

        return tuple(entry for entry in self.path.iterdir() if entry.is_file())



# Function to get a config value with variable interpolation
def get(section, key) -> DynamicPath:
    # * Get the raw value
    variables = []
    value = config.get(section, key)


    # * Find all variables in the value
    while '?' in value:                                                 # ? "?" is used as a placeholder for a variable, with the format "?variable?"
        start = value.index('?')
        end = value.index('?', start + 1)

        var = value[start + 1:end]
        variables.append(var)

        value = value[:start] + '<' + var + '>' + value[end + 1:]       # Replace ?variable? with <variable> so it doesn't get picked up again
    

    # * Recursively resolve references
    while '|' in value:                                                 # ? "|" is used as a reference to another key, with the format "|section|key|"
        start = value.index('|')                                        # Find where the "section|key" starts
        sep = value.index('|', start + 1)                               # Find the separator colon
        end = value.index('|', sep + 1)                                 # Find where the "section|key" ends


        ref = value[start + 1:end]
        refSection, refKey = ref.split('|')

        refDynamicPath = get(refSection, refKey)                        # Recursively get the referenced value
        variables.extend(refDynamicPath.variables)

        refValue = refDynamicPath.raw.strip('"' + "'")                  # Remove surrounding quotes if present

        value = value[:start] + refValue + value[end + 1:]


    # * Clean up
    variables = list(set(variables))                                    # Remove duplicates
 
    return DynamicPath(value, variables)


# @DEPRECATED
# def sortByModified(paths: list[DynamicPath]) -> list[DynamicPath]:
#     """
#     Sort a list of DynamicPath objects by their last modified time, newest first.
#     Paths that do not exist or are not files are considered the oldest.
#     """
#     def get_mod_time(path: DynamicPath):
#         if os.path.isfile(path.path):
#             return os.path.getmtime(path.path)
#         return 0  # Non-existent files are considered the oldest

#     return sorted(paths, key=get_mod_time, reverse=True)



if __name__ == "__main__":
    # Example| get the RobloxPlayerBeta path
    robloxPath = get('Roblox', 'RobloxPlayerBeta')

    print("Value: ", robloxPath.path)
    print("Variables: ", robloxPath.variables)

