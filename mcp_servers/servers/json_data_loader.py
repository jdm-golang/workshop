"""
Shared utility for loading JSON data from local manufacturing data files.
"""
import json
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class JSONDataLoader:
    """Utility class for loading manufacturing data from JSON files."""
    
    def __init__(self, base_path: str = None):
        """Initialize with base path to manufacturing data."""
        if base_path is None:
            # Default to local_manufacturing_data relative to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            base_path = os.path.join(project_root, "manufacturing-data")
        
        self.base_path = base_path
        self._cache = {}
    
    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Load and cache JSON file."""
        if file_path in self._cache:
            return self._cache[file_path]
        
        full_path = os.path.join(self.base_path, file_path)
        try:
            with open(full_path, 'r') as f:
                data = json.load(f)
                self._cache[file_path] = data
                logger.debug(f"Loaded JSON data from {full_path}")
                return data
        except FileNotFoundError:
            logger.error(f"JSON file not found: {full_path}")
            return {"data": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {full_path}: {e}")
            return {"data": {}}
    
    def get_factory_model(self) -> Dict[str, Any]:
        """Get shared factory model data."""
        return self._load_json_file("shared/factory_model.json")
    
    def get_cmms_data(self) -> Dict[str, Any]:
        """Get CMMS maintenance data."""
        return self._load_json_file("cmms/maintenance_data.json")
    
    def get_erp_data(self) -> Dict[str, Any]:
        """Get ERP business data."""
        return self._load_json_file("erp/business_data.json")
    
    def get_mes_data(self) -> Dict[str, Any]:
        """Get MES production data."""
        return self._load_json_file("mes/production_data.json")
    
    def get_wpms_data(self) -> Dict[str, Any]:
        """Get WPMS workforce data."""
        return self._load_json_file("wpms/workforce_data.json")
    
    def clear_cache(self):
        """Clear the data cache to force reload."""
        self._cache.clear()
    
    def get_machines(self) -> List[Dict[str, Any]]:
        """Get all machines from factory model."""
        factory_data = self.get_factory_model()
        return factory_data.get("data", {}).get("machines", [])
    
    def get_machine_by_id(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """Get specific machine by ID."""
        machines = self.get_machines()
        for machine in machines:
            if machine.get("machine_id") == machine_id:
                return machine
        return None
    
    def get_work_centers(self) -> List[Dict[str, Any]]:
        """Get all work centers from factory model."""
        factory_data = self.get_factory_model()
        return factory_data.get("data", {}).get("work_centers", [])
    
    def get_products(self) -> List[Dict[str, Any]]:
        """Get all products from factory model."""
        factory_data = self.get_factory_model()
        return factory_data.get("data", {}).get("products", [])

# Global instance
data_loader = JSONDataLoader()