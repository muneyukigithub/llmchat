from typing import Generator
from fastapi import Depends
import os
from google import genai
from gemini_service import GeminiService
from infrastructure.chat_thread_repository import ChatThreadRepository
from core.database import get_db
from application.chat.commands.chat_application_service import ChatApplicationService
from infrastructure.queries.chat_thread_query import ChatThreadQuery
from web_search_service import WebSearchService
from tavily import TavilyClient


def get_chat_thread_repository(db=Depends(get_db)):
    return ChatThreadRepository(db=db)

def get_gemini_service() -> GeminiService:
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    return GeminiService(client) 

def get_search_web_service() -> str:
    api_key = os.getenv("TAVILY_API_KRY")
    client = TavilyClient(api_key=api_key)
    return WebSearchService(client)

def get_chat_application_service(
    chat_repository=Depends(get_chat_thread_repository),
    llm_service=Depends(get_gemini_service),
    search_web_service=Depends(get_search_web_service)):
    return ChatApplicationService(
        chat_repository=chat_repository,
        llm_service=llm_service,
        search_web_service=search_web_service)

def get_chat_query(db=Depends(get_db)):
    return ChatThreadQuery(db=db)