from typing import List
from uuid import UUID
from domain.models.chat.chat_thread import ChatThread
from domain.models.chat.chat_thread_id import ChatThreadId
from domain.models.chat.chat_message import ChatMessage
from domain.models.chat.chat_message_role import Role
from domain.repositories.chat_thread_repository_interface import IChatThreadRepository
from domain.exceptions import ThreadNotFoundError, SessionMismatchError
from google.genai import types
from domain.llm.llm_interface import IllmInterface
from domain.models.chat.chat_message_content import MessageContent

class ChatApplicationService:

    def __init__(self,
        chat_repository:IChatThreadRepository,
        llm_service:IllmInterface,
        search_web_service):

        self.chat_repo = chat_repository
        self.llm_service = llm_service
        self.search_web_service=search_web_service
    
    def create_chat(self,session_id:UUID):
        chat_thread = ChatThread.create(session_id)
        return self.chat_repo.save(chat_thread)


    def rename_chat(self, thread_id: UUID, session_id: UUID, title: str):
        chat_thread = self._get_owned_thread(thread_id, session_id)
        chat_thread.change_title(title)
        return self.chat_repo.save(chat_thread)

    def delete_chat(self, thread_id: UUID, session_id: UUID):
        chat_thread = self._get_owned_thread(thread_id, session_id)
        self.chat_repo.delete(chat_thread.id)
        return {"thread_id": str(thread_id)}

    async def chat(
        self,
        thread_id:UUID,
        session_id:UUID,
        prompt:str,
        system_instruction="",
        temperature=2,
        ):

        target_thread_id = ChatThreadId(thread_id)
        chat_thread :ChatThread= self.chat_repo.find_by_id(target_thread_id)

        if not chat_thread:
            raise ThreadNotFoundError(f"Thread {thread_id} not found")
        
        if chat_thread.session_id.value != session_id:
            raise SessionMismatchError("Session ID does not match")

        response = await self.llm_service.chat_invoke(
            prompt=prompt,
            messages=chat_thread.messages, 
            system_instruction=system_instruction,
            temperature=temperature,
            tools=[
                self.search_web_service.search_web
            ],
        )
        user_content = MessageContent(prompt)
        model_content = MessageContent(response)

        user_chat_message = ChatMessage.create(Role.USER,target_thread_id,user_content)
        model_chat_message = ChatMessage.create(Role.MODEL,target_thread_id,model_content)
        chat_thread.add_message(user_chat_message)
        chat_thread.add_message(model_chat_message)
      
        self.chat_repo.save(chat_thread)

        return {"value": response}

    def _get_owned_thread(self, thread_id: UUID, session_id: UUID) -> ChatThread:
        target_thread_id = ChatThreadId(thread_id)
        chat_thread = self.chat_repo.find_by_id(target_thread_id)

        if not chat_thread:
            raise ThreadNotFoundError(f"Thread {thread_id} not found")

        if chat_thread.session_id.value != session_id:
            raise SessionMismatchError("Session ID does not match")

        return chat_thread

        # messages = chat_thread.messages

        # context = [
        #     types.Content(
        #         role=message.role.value,
        #         parts=[types.Part.from_text(text=message.content.value)],
        #     )
        #     for message in messages
        # ]

        # user_prompt = types.Content(
        #     role=Role.USER.value,
        #     parts=[types.Part.from_text(text=prompt)],
        # )

        # contents = context + [user_prompt]

        # response_text = await llm_service.chat_invoke(
        #     contents=contents, 
        #     system_instruction=system_instruction,
        #     temperature=temperature,
        #     tools=tools,
        # )

        # if not response_text:
        #     response_text = ""


        # new_messages = messages + [user_chat_message,model_chat_message ]

        # new_chat_thread = ChatThread(
        #     chat_thread.id.value,
        #     chat_thread.session_id.value,
        #     new_messages,
        #     chat_thread.title.value)

  



   

        


    # def get_chat_thread_message(self,chat_thread_id_str:str):
    #     chat_thread_id = ChatThreadId(value=UUID(chat_thread_id_str))
    #     messages : List[ChatMessage] = self.chat_repo.get_chat_thread_message(chat_thread_id)
    #     return messages

