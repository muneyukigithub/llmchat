from abc import ABC, abstractmethod

class IllmInterface(ABC):

    @abstractmethod
    def chat_invoke(self,prompt,messages,system_instruction,temperature,tools):
        pass