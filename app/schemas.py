from pydantic import BaseModel, Field

class Entity(BaseModel):
    entity_name: str = Field(..., description="Name of the entity")
    entity_type: str = Field(..., description="Type of the entity, e.g., PERSON, ORGANIZATION, LOCATION")