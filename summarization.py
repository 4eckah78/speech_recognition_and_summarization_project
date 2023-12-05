
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


def summarization(text):
    path = "IlyaGusev/rugpt3medium_sum_gazeta" # '' #path of local model 

    tokenizer = AutoTokenizer.from_pretrained(path)
    model = AutoModelForCausalLM.from_pretrained(path)

    text_tokens = tokenizer(
    text,
    max_length=1200,
    add_special_tokens=False,
    padding=False,
    truncation=True
    )["input_ids"]
    input_ids = text_tokens + [tokenizer.sep_token_id]
    input_ids = torch.LongTensor([input_ids])

    output_ids = model.generate(
    input_ids=input_ids,
    no_repeat_ngram_size=8
    )

    summary = tokenizer.decode(output_ids[0], skip_special_tokens=False)
    summary = summary.split(tokenizer.sep_token)[1]
    summary = summary.split(tokenizer.eos_token)[0]

    return summary