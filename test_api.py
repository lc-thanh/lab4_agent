import os
import logging

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from logging_utils import configure_logging, log_lines


load_dotenv()
configure_logging()
logger = logging.getLogger(__name__)

llm = ChatOpenAI(
    model="qwen/qwen3.6-plus:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
log_lines(logger, logging.INFO, llm.invoke("Xin chao?").content)
