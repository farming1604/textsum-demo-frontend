import httpx
import logging

from app.config import settings
from app.schemas import (
    Entity,
)

logger = logging.getLogger(__name__)

def _preprocess_entities(
    entities: list[str],
) -> list[dict]:
    processed_entities = []
    for entity in entities:
        if not entity:
            continue
        parts = entity.rsplit("(", 1)
        if len(parts) == 2:
            name = parts[0].strip()
            entity_type = parts[1].strip(" )")
            processed_entities.append(Entity(entity_name=name, entity_type=entity_type))
        else:
            processed_entities.append(Entity(entity_name=entity.strip(), entity_type="Unknown"))
    
    processed_entities_dict = [
        {
            "entity_name": entity.entity_name,
            "entity_type": entity.entity_type
        } for entity in processed_entities
    ]

    return processed_entities_dict

def summarize_text(
    content: str,
    entities: list[str] = [],
    **kwargs,
) -> str:
    logger.error("Starting text summarization")
    logger.error(f"{ entities = }")
    entities: list[dict] = _preprocess_entities(entities)

    json_request_body = {
        "content": content,
        "entities": entities
    }

    try:
        response = httpx.post(
            url=settings.SUMMARIZATION_API_URL,
            json=json_request_body,
        )

        if response.status_code != 200:
            raise ValueError(f"Error from summarization API: {response.text}")
        
        response_json = response.json()
        logger.error(f"Received response: {response_json}")
        summary = response_json.get("summary", "")
    except Exception as e:
        logger.error(f"Failed to summarize text: {e}")
        summary = "Error occurred while summarizing the text."

    return summary

def extract_entities(
    content: str,
    **kwargs,
) -> list[Entity]:
    logger.info("Starting entity extraction")
    logger.info(f"{ content = }")

    json_request_body = {
        "content": content,
    }

    try:
        response = httpx.post(
            url=settings.EXTRACT_ENTITIES_API_URL,
            json=json_request_body,
        )

        if response.status_code != 200:
            raise ValueError(f"Error from entity extraction API: {response.text}")
        
        response_json = response.json()
        entities = [
            Entity(
                entity_name=entity["entity_name"],
                entity_type=entity["entity_type"]
            ) for entity in response_json.get("entities", [])
        ]
        logger.info(f"Extracted entities: {entities}")
    except Exception as e:
        logger.error(f"Failed to extract entities: {e}")
        entities = []

    return entities

def generate_questions(text: str, selected_entities: list[str]) -> str:
    # If no entities are selected, return a warning message
    if not selected_entities:
        return "⚠️ No entities selected. Please extract and select entities before generating questions."

    questions = []
    for entity in selected_entities:
        # Extract the entity name by removing the type in parentheses
        name = entity.split(" (")[0]

        # Append some mock example questions for each entity
        questions.append(f"❓ What is the role of {name} in the text?")
        questions.append(f"❓ Why is {name} mentioned?")
        questions.append(f"❓ What happened to {name}?")

    # Return all questions as a single string
    return "\n".join(questions)
