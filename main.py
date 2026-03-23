import argparse
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from datasets import DatasetDict
from divrag import DivRAG

file_lock = threading.Lock()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--llm_model",
        type=str,
        default="gpt-5-mini",
        help="LLM model name",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./results/diverge_results.txt",
        help="Output file path",
    )
    parser.add_argument(
        "--nums_answers",
        type=int,
        default=10,
        help="Number of answers per query",
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=25,
        help="Maximum parallel workers",
    )
    return parser.parse_args()


def run_one_query(qid, data, nums_answers, llm_model, outfile):
    query = data["prompt"]

    div = DivRAG(
        query=query,
        qid=qid,
        embed_model="text-embedding-3-small",
        llm_model=llm_model,
        max_generation_num=nums_answers,
    )

    results = div.run()

    cleaned_results = [
        res.replace("\n", " ").replace("\t", " ").strip()
        for res in results
    ]

    with file_lock:
        for i, res in enumerate(cleaned_results):
            outfile.write(f"{i+1}|{qid+1}:\t{res}\n")
        outfile.flush()

    return qid


async def run_all_queries_async(dataset, nums_answers, llm_model, outfile, max_workers):
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=max_workers)

    tasks = []
    for qid, data in enumerate(dataset):
        tasks.append(
            loop.run_in_executor(
                executor,
                run_one_query,
                qid,
                data,
                nums_answers,
                llm_model,
                outfile,
            )
        )

    await asyncio.gather(*tasks)


def main():
    args = parse_args()

    dataset = DatasetDict.load_from_disk(
        "./data/clan_diverge_dataset"
    )["train"].select(range(100))

    with open(args.output, "w", encoding="utf-8") as f:
        asyncio.run(
            run_all_queries_async(
                dataset=dataset,
                nums_answers=args.nums_answers,
                llm_model=args.llm_model,
                outfile=f,
                max_workers=args.max_workers,
            )
        )


if __name__ == "__main__":
    main()
