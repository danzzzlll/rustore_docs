# vllm
import os
from vllm import LLM, SamplingParams
from abc import ABC, abstractmethod
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

def get_os():
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "2, 3"

    DEVICE_MAP = 'auto'


class GenerativeModel(ABC):
    def __init__(self,
                 model_name,
                 system_prompt=None):
        
        self.model_name = model_name
        self.system_prompt = system_prompt

        
    @abstractmethod
    def inference(self,
                  text):
        pass

    @abstractmethod
    def load(self):
        pass
    
    @abstractmethod
    def config_prompt(self):
        pass



class Mistral(GenerativeModel):
    def __init__(self, model_name, model_path, system_prompt=''):
        super().__init__(model_name, system_prompt)
        self.model_path = model_path
        self.load() 

    def load(self):
        self.model = LLM(model=self.model_path, 
                  trust_remote_code=True, 
                  seed=42)

    def config_prompt(self, system_prompt):
        """Configure or update the system prompt."""
        self.system_prompt = "<s>[INST] " + system_prompt
        

    def inference(self, text, top_p=0.6, temperature=0.8, repetition_penalty=1.0, max_new_tokens=2000,
                  skip_special_tokens=False):
        """Generate text based on the provided input"""
        sampling_params = SamplingParams(top_p=top_p, temperature=temperature, repetition_penalty=repetition_penalty,
                                         max_tokens=max_new_tokens)
        
        prompt = self.system_prompt + '\n' + text + ' [/INST] '
        
        output = self.model.generate(prompt, sampling_params)
        
        prompt = output[0].prompt
        generated_text = output[0].outputs[0].text
        
        return generated_text



class GigaApi(GenerativeModel):
    def __init__(self,
                 model_name,
                 system_prompt='',
                 credentials = ''):
        
        super().__init__(model_name, system_prompt)
        self.credentials = credentials
        self.messages = []
        self.chat = None
        self.load()

        
    def load(self):
        """Load the model and tokenizer."""
        self.chat = GigaChat(model="GigaChat-Pro", credentials=self.credentials, verify_ssl_certs=False)


    def config_prompt(self, system_prompt):
        """Configure or update the system prompt."""
        self.system_prompt = system_prompt
        
        

    def inference(self,
                  text):
        """Generate text based on the provided input"""
        
        self.messages = []
        self.messages.append(SystemMessage(content=self.system_prompt))
#         message = self.messages.copy()
        self.messages.append(HumanMessage(content=text))
        res = self.chat(self.messages)
        
        return res.content



class Solar(GenerativeModel):
    def __init__(self, model_name, model_path, system_prompt=''):
        super().__init__(model_name, system_prompt)
        self.model_path = model_path
        self.load() 

    def load(self):
        self.model = LLM(model=self.model_path, 
                  trust_remote_code=True, 
                  seed=42)

    def config_prompt(self, system_prompt):
        """Configure or update the system prompt."""
        self.system_prompt = "<s>### System: " + system_prompt
        

    def inference(self, text, top_p=0.6, temperature=0.8, repetition_penalty=1.0, max_new_tokens=2000,
                  skip_special_tokens=False):
        """Generate text based on the provided input"""
        sampling_params = SamplingParams(top_p=top_p, temperature=temperature, repetition_penalty=repetition_penalty,
                                         max_tokens=max_new_tokens)
        
        prompt = self.system_prompt + '\n### User: ' + text + '\n### Assistant: '
        
        output = self.model.generate(prompt, sampling_params)
        
        prompt = output[0].prompt
        generated_text = output[0].outputs[0].text
        
        return generated_text
