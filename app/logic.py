import httpx
from httpx import Timeout
import logging

from app.config import settings
from app.schemas import (
    Entity,
)

logger = logging.getLogger(__name__)

def _preprocess_entities(
    entities: list[str],
) -> list[Entity]:
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
    
    return processed_entities

def _preprocess_questions(
    questions: str,
) -> list[str]:
    if not questions:
        return []
    questions = questions.split("\n\n")
    questions = [
        q.replace("❓", "").strip()
        for q in questions
    ]
    questions = [
        q.split("\n💬")[0].strip()
        for q in questions
    ]

    return questions

def summarize_text(
    content: str,
    entities: list[str] = [],
    questions: str = "",
    model: str = "BARTpho",
    max_new_tokens: int = 256,
    **kwargs,
) -> str:
    entities: list[Entity] = _preprocess_entities(entities)
    questions: list[str] = _preprocess_questions(questions)

    logger.error(f"Summarizing content with model {model}")

    json_request_body = {
        "content": content,
        "question_answer_pairs": [
            {
                "question": question,
                "entity": {
                    "entity_name": entity.entity_name,
                    "entity_type": entity.entity_type
                }
            }
            for question, entity in zip(questions, entities)
        ],
        "summarization_model_name": model,
        "search_config": {
            "kwargs": {
                "max_new_tokens": max_new_tokens
            }
        }
    }

    logger.error(f"Request body for summarization: {json_request_body}")

    try:
        response = httpx.post(
            url=settings.SUMMARIZATION_API_URL,
            json=json_request_body,
            timeout=Timeout(
                connect=settings.MAX_TIMEOUT_CONNECT,
                read=settings.MAX_TIMEOUT_READ,
                write=settings.MAX_TIMEOUT_WRITE,
                pool=settings.MAX_TIMEOUT_POOL,
            )
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
            timeout=Timeout(
                connect=settings.MAX_TIMEOUT_CONNECT,
                read=settings.MAX_TIMEOUT_READ,
                write=settings.MAX_TIMEOUT_WRITE,
                pool=settings.MAX_TIMEOUT_POOL,
            )
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

def generate_questions(
    text: str,
    selected_entities: list[str]
) -> list[str]:
    entities: list[Entity] = _preprocess_entities(selected_entities)

    json_request_body = {
        "content": text,
        "entities": [
            {
                "entity_name": entity.entity_name,
                "entity_type": entity.entity_type
            } for entity in entities
        ]
    }

    try:
        response = httpx.post(
            url=settings.QUESTION_GENERATION_API_URL,
            json=json_request_body,
            timeout=Timeout(
                connect=settings.MAX_TIMEOUT_CONNECT,
                read=settings.MAX_TIMEOUT_READ,
                write=settings.MAX_TIMEOUT_WRITE,
                pool=settings.MAX_TIMEOUT_POOL,
            )
        )

        if response.status_code != 200:
            raise ValueError(f"Error from question generation API: {response.text}")
        
        response_json = response.json()
        questions = response_json.get("questions", [])
        logger.error(f"Generated questions: {questions}")
        questions = [
            q['question']
            for q in questions
        ]

        return questions
    except Exception as e:
        logger.error(f"Failed to generate questions: {e}")
        return ["Error occurred while generating questions."]