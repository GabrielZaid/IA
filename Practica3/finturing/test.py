import time 
import torch
from transformers import pipeline

model_id = "./Llama-3.2-3B-trained"
# model_id = "unsloth/Llama-3.2-3B-Instruct"

pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

instruction = "Eres un asistente virtual que ayuda a responder preguntas controlverciales: Responde solo '@SINAYUDA@' si no puedes responder a la pregunta. Responde solo '@SINCONTEXTO@' si la pregunta no esta relacionada con alguna información. Responde solo '@ABORTO@' si la pregunta es acerca de un tema de aborto. Responde solo '@EUTANASIA@' si la pregunta es acerca de un tema de eutanasia."

def requestToLLM(i, instruction, req):
    t = time.time()
    outputs = pipe(
        [
            {"role": "system", "content": instruction},
            {"role": "user","content": req}
        ],
        max_new_tokens=256,
        temperature=0.9
    )
    t = time.time() - t
    print("\nPREGUNTA ", i, "(" + str(round(t)) ,outputs[0]["generated_text"][1]["content"], "\n")
    print(outputs[0]["generated_text"][-1]["content"])
    
    
requestToLLM(1, instruction, "¿Qué opinas sobre el aborto?")
requestToLLM(2, instruction, "¿Qué opinas sobre la eutanasia?") 