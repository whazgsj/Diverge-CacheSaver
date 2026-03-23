import sys
import asyncio

# Suppress the "pending task" message reported when asyncio shuts down
def silence_asyncio_shutdown():
    def custom_exception_handler(loop, context):
        pass
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(custom_exception_handler)

silence_asyncio_shutdown()

from divrag import DivRAG
import time

# Prompt
query = "Give me one tip less than 10 words about how to enhance my strength."
qid = 2
num_answers = 3

print("Prompt:", query)

# Initialize DIVERGE
div = DivRAG(
    query=query,
    qid=qid,
    embed_model="text-embedding-3-small",
    llm_model="gpt-5-mini",
    max_generation_num=num_answers,
    retrieval_chunk_size=512,
    debug=True,
)

# Run
results = div.run()
print(f"QID: {qid}")
print("RESULTS:", results)

# Save results
with open(f"./results/demo_output_q{qid}_run{time.time_ns()}.txt", "w") as f:
    for i, res in enumerate(results, 1):
        clean = res.replace("\n", " ").replace("\t", " ").strip()
        f.write(f"{i}|{qid+1}:\t{clean}\n")