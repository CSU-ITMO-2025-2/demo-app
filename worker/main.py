import json
import logging
import os
import time
from typing import List

from sqlalchemy.orm import Session

from common.database import SessionLocal
from common.models import TodoItem, TodoStep
from common.kafka_client import create_todo_consumer

from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

if not YANDEX_CLOUD_API_KEY:
    raise RuntimeError("YANDEX_CLOUD_API_KEY env var is required for worker")

client = OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://llm.api.cloud.yandex.net/v1",
    project=YANDEX_CLOUD_FOLDER
)

def llm_generate_steps(title: str) -> List[str]:
    """
    Генерируем шаги при помощи ChatGPT-модели.

    Просим модель вернуть ЧИСТЫЙ JSON-массив строк:
    ["step 1", "step 2", ...]
    """
    system_prompt = (
        "Ты помощник, который помогает разбивать цель пользователя на конкретный план действий.\n"
        "ПОЛУЧИШЬ только формулировку цели (title).\n\n"
        "Нужно вернуть 3–7 коротких конкретных шагов, что делать, чтобы приблизиться к цели.\n"
        "Формат ответа — СТРОГО JSON-массив строк, без текста до или после.\n"
        'Пример: ["Сделай X", "Сделай Y", "Сделай Z"]'
    )

    user_prompt = f"Цель: {title}"

    logger.info("Calling LLM for title: %s", title)

    try:
        resp = client.chat.completions.create(
            model=f"gpt://{YANDEX_CLOUD_FOLDER}/yandexgpt/rc",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )
    except Exception as e:
        logger.warning(
            "LLM call failed, using fallback steps for title '%s': %s", title, e
        )
        return [f"Review requirements for: {title}"]

    content = resp.choices[0].message.content.strip()
    logger.debug("LLM raw response: %s", content)

    def try_parse_json(text: str) -> List[str] | None:
        try:
            data = json.loads(text)
            if isinstance(data, list):
                steps = [str(x).strip() for x in data if str(x).strip()]
                return steps or None
        except Exception:
            return None

    steps = try_parse_json(content)
    if steps:
        return steps

    if "```" in content:
        fenced = content.split("```")
        for block in fenced:
            maybe = try_parse_json(block.strip())
            if maybe:
                return maybe
        for block in fenced:
            if "[" in block and "]" in block:
                snippet = block[block.find("[") : block.rfind("]") + 1]
                maybe = try_parse_json(snippet)
                if maybe:
                    return maybe

    if "[" in content and "]" in content:
        snippet = content[content.find("[") : content.rfind("]") + 1]
        steps = try_parse_json(snippet)
        if steps:
            return steps

    lines = []
    for line in content.splitlines():
        stripped = line.strip("`").strip()
        if not stripped:
            continue
        for prefix in ("- ", "* ", "• ", "1. ", "2. ", "3. ", "4. ", "5. "):
            if stripped.startswith(prefix):
                stripped = stripped[len(prefix) :]
                break
        lines.append(stripped)
    if len(lines) > 1:
        return lines

    return [content]


def process_message(db: Session, todo_id: int, title: str) -> None:
    todo: TodoItem | None = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not todo:
        logger.warning("Todo %s not found, skip", todo_id)
        return

    if todo.steps:
        logger.info("Todo %s already has %d steps, skip", todo_id, len(todo.steps))
        return

    steps_texts = llm_generate_steps(title)
    logger.info("Generated %d steps for todo %s (%s)", len(steps_texts), todo_id, title)

    for text in steps_texts:
        step = TodoStep(todo_id=todo_id, description=text, completed=False)
        db.add(step)

    db.commit()
    logger.info("Saved %d steps for todo %s", len(steps_texts), todo_id)


def main() -> None:
    consumer = create_todo_consumer(group_id="todo-generator")
    logger.info("Todo generator worker started. Waiting for messages...")

    while True:
        db = SessionLocal()
        try:
            for msg in consumer:
                value = msg.value
                todo_id = value.get("todo_id")
                title = value.get("title", "")

                logger.info("Got message for todo_id=%s, title=%s", todo_id, title)
                time.sleep(10)
                if todo_id is None:
                    logger.warning("No todo_id in message, skip: %s", value)
                    continue

                try:
                    process_message(db, todo_id=todo_id, title=title)
                except Exception as e:
                    logger.exception("Error processing message for todo %s: %s", todo_id, e)
        except Exception as e:
            logger.exception("Worker loop crashed: %s. Sleep and retry...", e)
            time.sleep(5)
        finally:
            db.close()


if __name__ == "__main__":
    main()
