import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

path = 'cointegrated/rut5-base-absum' # "" # скачать и поменять 

#tokenizer.save_pretrained("path")
#model.save_pretrained("path")

model = T5ForConditionalGeneration.from_pretrained(path)
tokenizer = T5Tokenizer.from_pretrained(path)

def split_text(text, max_length=600):
    sentences = text.split('. ')
    parts = []
    current_part = ''
    
    for sentence in sentences:
        if len(current_part) + len(sentence) + 2 <= max_length:
            current_part += sentence + '. '
        else:
            parts.append(current_part[:-1])  
            current_part = sentence + '. '
  
    if current_part:
        parts.append(current_part[:-1])   
    return parts

def summarization(text, n_words=None, compression=None,
    max_length=600, num_beams=3, do_sample=False, repetition_penalty=10.0, 
    **kwargs
):
    result = ''
    texts = split_text(text, max_length)
    for chunk in texts:
      if n_words:
          chunk = '[{}] '.format(n_words) + chunk
      elif compression:
          chunk = '[{0:.1g}] '.format(compression) + chunk
      x = tokenizer(chunk, return_tensors='pt', padding=True).to(model.device)
      with torch.inference_mode():
          out = model.generate(
              **x, 
              max_length=max_length, num_beams=num_beams, 
              do_sample=do_sample, repetition_penalty=repetition_penalty, 
              **kwargs
         )
      result = result + tokenizer.decode(out[0], skip_special_tokens=True) + ' '        
    
    return result