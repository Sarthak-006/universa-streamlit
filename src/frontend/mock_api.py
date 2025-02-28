"""
Mock API module for UNIVERSA frontend demonstration.
Used when the real API is not available.
"""

import time
import random
import json
import uuid
from typing import Dict, List, Any, Optional

class MockAPI:
    """Mock API handler for UNIVERSA frontend."""
    
    def __init__(self):
        """Initialize with demo data."""
        self.profiles = [
            {
                "id": f"profile_{i}",
                "name": f"Demo User {i}",
                "description": f"This is a demo profile #{i} for testing purposes.",
                "preferences": {
                    "interests": random.sample(["AI", "blockchain", "privacy", "web3", "science", "art", "music", "sports"], 3),
                    "location": random.choice(["Remote", "New York", "San Francisco", "London", "Tokyo"]),
                    "availability": random.choice(["Full-time", "Part-time", "Weekends"])
                },
                "tags": random.sample(["developer", "researcher", "designer", "mentor", "student"], 2)
            }
            for i in range(1, 6)
        ]
        
        self.groups = [
            {
                "id": f"group_{i}",
                "name": f"Demo Group {i}",
                "description": f"This is a demo group #{i} for testing purposes.",
                "preferences": {
                    "focus": random.choice(["research", "development", "education", "networking"]),
                    "meeting_frequency": random.choice(["weekly", "monthly", "as needed"])
                },
                "members": random.sample([p["id"] for p in self.profiles], random.randint(1, 3)),
                "tags": random.sample(["tech", "science", "ai", "blockchain", "privacy"], 3)
            }
            for i in range(1, 4)
        ]
    
    def health(self) -> Dict:
        """Health check endpoint."""
        return {"status": "healthy", "mode": "mock"}
    
    def generate_key_pair(self) -> Dict:
        """Generate a mock encryption key pair."""
        return {
            "public_key": f"mock_public_key_{uuid.uuid4().hex[:8]}",
            "private_key": f"mock_private_key_{uuid.uuid4().hex[:16]}"
        }
    
    def get_profiles(self) -> List[Dict]:
        """Get all profiles."""
        return self.profiles
    
    def get_profile(self, profile_id: str) -> Dict:
        """Get a specific profile."""
        for profile in self.profiles:
            if profile["id"] == profile_id:
                return profile
        return {"error": "Profile not found"}
    
    def create_profile(self, data: Dict) -> Dict:
        """Create a new profile."""
        profile_id = f"profile_{uuid.uuid4().hex[:8]}"
        profile = {
            "id": profile_id,
            "name": data.get("name", f"User {profile_id}"),
            "description": data.get("description", "No description provided."),
            "preferences": data.get("preferences", {}),
            "tags": data.get("tags", [])
        }
        self.profiles.append(profile)
        return {"profile_id": profile_id}
    
    def get_groups(self) -> List[Dict]:
        """Get all groups."""
        return self.groups
    
    def get_matches(self, profile_id: str, params: Optional[Dict] = None) -> List[Dict]:
        """Get matches for a profile."""
        # Filter out the requesting profile
        other_profiles = [p for p in self.profiles if p["id"] != profile_id]
        
        # Generate random match scores
        matches = []
        for profile in other_profiles:
            score = random.uniform(0.5, 1.0)
            matches.append({
                "profile": profile,
                "score": score
            })
        
        # Sort by score and limit
        matches.sort(key=lambda x: x["score"], reverse=True)
        limit = params.get("limit", 10) if params else 10
        return matches[:limit]
    
    def handle_request(self, endpoint: str, method: str = "GET", 
                      data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Handle a mock API request."""
        # Simulate network delay
        time.sleep(0.3)
        
        # Health check
        if endpoint == "/health" and method == "GET":
            return self.health()
        
        # Encryption
        if endpoint == "/encryption/generate-key-pair" and method == "POST":
            return self.generate_key_pair()
        
        # Profiles
        if endpoint == "/profiles/" and method == "GET":
            return self.get_profiles()
        
        if endpoint.startswith("/profiles/") and method == "GET":
            profile_id = endpoint.split("/")[2]
            return self.get_profile(profile_id)
        
        if endpoint == "/profiles/" and method == "POST":
            return self.create_profile(data or {})
        
        # Groups
        if endpoint == "/groups/" and method == "GET":
            return self.groups
        
        # Matching
        if endpoint.startswith("/matching/profile/") and "matches" in endpoint and method == "GET":
            profile_id = endpoint.split("/")[2]
            return self.get_matches(profile_id, params)
        
        # Default error response
        return {"error": f"Endpoint {endpoint} with method {method} not implemented in mock API"}

# Create a singleton instance
mock_api = MockAPI()

def make_mock_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None,
                    params: Optional[Dict] = None) -> Dict:
    """Make a request to the mock API."""
    return mock_api.handle_request(endpoint, method, data, params) 