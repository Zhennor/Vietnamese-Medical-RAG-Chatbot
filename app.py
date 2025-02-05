from langchain.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

model_name = "Viet-Mistral/Vistral-7B-Chat"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

llm = HuggingFacePipeline(pipeline=pipe)

prompt_template = "Hãy giải thích về {topic} một cách dễ hiểu."

prompt = PromptTemplate(input_variables=["topic"], template=prompt_template)

chain = LLMChain(llm=llm, prompt=prompt)

question = "machine learning"
response = chain.run(question)

print(response)
