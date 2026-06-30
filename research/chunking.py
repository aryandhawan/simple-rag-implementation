from pathlib import Path
from entity.config_entity import ChunkingConfig
from config.configuration import read_yaml,create_directories

class ConfigurationManager:
    def __init__(self, config_path: Path='config/config.yaml'):
        self.config_path = read_yaml(config_path)
        create_directories([Path(self.config_path.root_dir)], verbose=True)
    

    
