"""Fine-tuning CLI for OpenAI models."""
import argparse
import json
from openai import OpenAI

def upload_file(client, file_path):
    """Upload training file."""
    with open(file_path, 'rb') as f:
        response = client.files.create(file=f, purpose='fine-tune')
    return response.id

def create_fine_tune(client, model, training_file, suffix=None):
    """Create fine-tuning job."""
    params = {
        "model": model,
        "training_file": training_file,
    }
    if suffix:
        params["suffix"] = suffix
    
    response = client.fine_tuning.jobs.create(**params)
    return response.id

def list_jobs(client, limit=10):
    """List fine-tuning jobs."""
    jobs = client.fine_tuning.jobs.list(limit=limit)
    return jobs.data

def retrieve_job(client, job_id):
    """Get fine-tuning job status."""
    return client.fine_tuning.jobs.retrieve(job_id)

def cancel_job(client, job_id):
    """Cancel fine-tuning job."""
    return client.fine_tuning.jobs.cancel(job_id)

def main():
    parser = argparse.ArgumentParser(description='OpenAI Fine-Tuning CLI')
    sub = parser.add_subparsers(dest='command', help='Commands')
    
    # Upload
    up = sub.add_parser('upload', help='Upload training file')
    up.add_argument('file', help='JSONL training file')
    
    # Create
    create = sub.add_parser('create', help='Create fine-tuning job')
    create.add_argument('--model', required=True, help='Base model')
    create.add_argument('--training-file', required=True, help='Training file ID')
    create.add_argument('--suffix', help='Model suffix')
    
    # List
    sub.add_parser('list', help='List jobs')
    
    # Status
    stat = sub.add_parser('status', help='Job status')
    stat.add_argument('job_id', help='Job ID')
    
    # Cancel
    canc = sub.add_parser('cancel', help='Cancel job')
    canc.add_argument('job_id', help='Job ID')
    
    args = parser.parse_args()
    
    client = OpenAI()
    
    if args.command == 'upload':
        file_id = upload_file(client, args.file)
        print(f"Uploaded: {file_id}")
    elif args.command == 'create':
        job_id = create_fine_tune(client, args.model, args.training_file, args.suffix)
        print(f"Job created: {job_id}")
    elif args.command == 'list':
        jobs = list_jobs(client)
        for j in jobs:
            print(f"{j.id} - {j.model} - {j.status}")
    elif args.command == 'status':
        job = retrieve_job(client, args.job_id)
        print(json.dumps(job.model_dump(), indent=2))
    elif args.command == 'cancel':
        result = cancel_job(client, args.job_id)
        print(f"Cancelled: {result.status}")

if __name__ == '__main__':
    main()
