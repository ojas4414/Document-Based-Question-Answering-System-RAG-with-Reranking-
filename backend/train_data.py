import random

def build_training_set(chunks,queries):
    data=[]
    for q in queries:
        positive=random.choice(chunks)
        negative=random.choice(chunks)

        data.append((q,positive,1))
        data.append((q,negative,0))
    
    return data