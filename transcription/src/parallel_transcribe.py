import argparse
import os
from pathlib import Path
import multiprocessing as mp
from typing import List
import math
import subprocess
import shutil


def split_files(files: List[Path], n_gpus: int) -> List[List[Path]]:
    """Split files into n_gpus roughly equal groups."""
    files_per_gpu = math.ceil(len(files) / n_gpus)
    return [files[i : i + files_per_gpu] for i in range(0, len(files), files_per_gpu)]


def process_gpu_batch(
    gpu_id: int, files: List[Path], model: str, output_dir: str
) -> None:
    """Process a batch of files on a specific GPU."""

    gpu_output_dir = f"{output_dir}_gpu{gpu_id}"
    gpu_transcripts_dir = f"./transcripts_gpu{gpu_id}"
    os.makedirs(gpu_output_dir, exist_ok=True)
    os.makedirs(gpu_transcripts_dir, exist_ok=True)

    files_str = " ".join(str(f) for f in files)

    cmd = (
        f"CUDA_VISIBLE_DEVICES={gpu_id} python cli.py "
        f"--files {files_str} "
        f"--model {model} "
        f"--output-dir {gpu_output_dir} "
        f"--transcripts-dir {gpu_transcripts_dir}"
    )

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error in GPU {gpu_id} batch: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Run parallel transcription across multiple GPUs"
    )
    parser.add_argument(
        "--n-gpus", type=int, required=True, help="Number of GPUs to use"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="./downloads",
        help="Directory containing input files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./downloads",
        help="Base directory for output files",
    )
    parser.add_argument(
        "--model", type=str, default="medium.en", help="Whisper model to use"
    )
    parser.add_argument(
        "--file-pattern", type=str, default="*.wav", help="Pattern to match input files"
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    files = list(input_dir.glob(args.file_pattern))

    if not files:
        print(f"No files found matching pattern {args.file_pattern} in {input_dir}")
        return

    print(f"Found {len(files)} files to process")

    file_batches = split_files(files, args.n_gpus)

    processes = []
    for gpu_id in range(args.n_gpus):
        if gpu_id < len(file_batches):
            p = mp.Process(
                target=process_gpu_batch,
                args=(gpu_id, file_batches[gpu_id], args.model, args.output_dir),
            )
            processes.append(p)
            p.start()
            print(
                f"Started process for GPU {gpu_id} with {len(file_batches[gpu_id])} files"
            )

    for p in processes:
        p.join()

    print("All processes completed")

    for gpu_id in range(args.n_gpus):
        gpu_transcripts_dir = Path(f"./transcripts_gpu{gpu_id}")
        if gpu_transcripts_dir.exists():

            os.makedirs("./transcripts", exist_ok=True)
            for transcript in gpu_transcripts_dir.glob("*"):
                shutil.copy2(transcript, "./transcripts/")
            print(f"Merged transcripts from GPU {gpu_id}")


if __name__ == "__main__":
    main()
