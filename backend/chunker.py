def chunk_text(
      text:str,
      size: int=400,
      overlap: int =80
):
    words=text.split()
    chunks=[]
    start=0

    while start <len(words):
        end= start+ size  
        chunk_words= words[start:end]
        chunk=" ".join(chunk_words)
        chunks.append(chunk)

        start= end -overlap
        if start<0:
            start=0
    
    return chunks
    