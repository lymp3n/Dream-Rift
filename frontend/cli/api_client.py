"""API client for backend."""

import requests
from typing import Dict, Any, Optional, List


class APIClient:
    """HTTP client for Dreamforge API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _get(self, endpoint: str) -> Dict[str, Any]:
        """GET request."""
        response = self.session.get(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        return response.json()
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST request."""
        response = self.session.post(f"{self.base_url}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    
    def _delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE request."""
        response = self.session.delete(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        return response.json()
    
    # Character endpoints
    def get_character(self, character_id: int) -> Dict[str, Any]:
        """Get character."""
        return self._get(f"/api/characters/{character_id}")
    
    def get_character_stats(self, character_id: int) -> Dict[str, Any]:
        """Get character stats."""
        return self._get(f"/api/characters/{character_id}/stats")
    
    # Combat endpoints
    def attack(self, character_id: int, monster_id: int, skill_id: Optional[int] = None) -> Dict[str, Any]:
        """Attack monster."""
        return self._post("/api/combat/attack", {
            "character_id": character_id,
            "monster_id": monster_id,
            "skill_id": skill_id
        })
    
    # Location endpoints
    def get_locations(self) -> List[Dict[str, Any]]:
        """Get all locations."""
        return self._get("/api/locations")
    
    def get_location(self, location_id: int) -> Dict[str, Any]:
        """Get location info."""
        return self._get(f"/api/locations/{location_id}")
    
    def travel(self, character_id: int, target_location_id: int) -> Dict[str, Any]:
        """Travel to location."""
        return self._post("/api/locations/travel", {
            "character_id": character_id,
            "target_location_id": target_location_id
        })
    
    def get_available_locations(self, character_id: int) -> List[Dict[str, Any]]:
        """Get available locations."""
        return self._get(f"/api/locations/{character_id}/available")
    
    # Inventory endpoints
    def get_inventory(self, character_id: int) -> Dict[str, Any]:
        """Get inventory."""
        return self._get(f"/api/inventory/{character_id}")
    
    def get_equipment(self, character_id: int) -> Dict[str, Any]:
        """Get equipment."""
        return self._get(f"/api/inventory/{character_id}/equipment")
    
    def equip_item(self, character_id: int, item_id: int) -> Dict[str, Any]:
        """Equip item."""
        return self._post("/api/inventory/equip", {
            "character_id": character_id,
            "item_id": item_id
        })
    
    # Skills endpoints
    def get_skills(self) -> List[Dict[str, Any]]:
        """Get all skills."""
        return self._get("/api/skills")
    
    def get_learned_skills(self, character_id: int) -> List[Dict[str, Any]]:
        """Get learned skills."""
        return self._get(f"/api/skills/{character_id}/learned")
    
    def get_selected_skills(self, character_id: int) -> List[Dict[str, Any]]:
        """Get selected skills."""
        return self._get(f"/api/skills/{character_id}/selected")
    
    def start_combat(self, character_id: int, monster_id: int) -> Dict[str, Any]:
        """Start combat."""
        return self._post("/api/combat-enhanced/start", {
            "character_id": character_id,
            "monster_id": monster_id
        })
    
    def combat_action(self, character_id: int, monster_id: int, action_type: str, skill_id: Optional[int] = None) -> Dict[str, Any]:
        """Perform combat action."""
        data = {
            "character_id": character_id,
            "monster_id": monster_id,
            "action_type": action_type
        }
        if skill_id:
            data["skill_id"] = skill_id
        return self._post("/api/combat-enhanced/action", data)

