try:
    import wandb

    WANDB_AVAILABLE = True
except:
    WANDB_AVAILABLE = False


if WANDB_AVAILABLE:
    from openai import FineTune, File
    import io
    import numpy as np
    import pandas as pd
    from pathlib import Path


class Logger:
    """
    Log fine-tune jobs to Weights & Biases
    """

    if not WANDB_AVAILABLE:
        print("Logging requires wandb to be installed. Run `pip install wandb`.")
    else:
        _wandb_api = False
        _logged_in = False

    @classmethod
    def log(
        cls,
        id=None,
        n_jobs=10,
        project="GPT-3",
        entity=None,
        force=False,
        **kwargs_wandb_init,
    ):
        """
        Log a fine-tune jobs to Weights & Biases.
        :param id: The id of the fine-tune job (optional)
        :param n_jobs: Number of most recent fine-tune jobs to log when an id is not provided
        :param project: Name of the project where you're sending runs. By default, it is "GPT-3".
        :param entity: Username or team name where you're sending runs. By default, your default entity is used, which is usually your username.
        :param force: Forces logging and overwrite existing wandb run of the same finetune job.
        """

        if not WANDB_AVAILABLE:
            return

        if id:
            fine_tune = FineTune.retrieve(id=id)
            fine_tune.pop("events", None)
            fine_tunes = [fine_tune]

        else:
            # get list of fine_tune to log
            fine_tunes = FineTune.list()
            if not fine_tunes or fine_tunes.get("data") is None:
                print("No fine-tune jobs have been retrieved")
                return
            fine_tunes = fine_tunes["data"][-n_jobs:]

        # log starting from oldest fine_tune
        for fine_tune in fine_tunes:
            cls._log_fine_tune(fine_tune, project, entity, force, **kwargs_wandb_init)
        return "Command completed successfully"

    @classmethod
    def _log_fine_tune(cls, fine_tune, project, entity, force, **kwargs_wandb_init):
        fine_tune_id = fine_tune.get("id")
        status = fine_tune.get("status")

        # check run completed successfully
        if status != "succeeded":
            print(
                f'Fine-tune job {fine_tune_id} has the status "{status}" and will not be logged'
            )

        # check run has not been logged already
        run_path = f"{project}/{fine_tune_id}"
        if entity is not None:
            run_path = f"{entity}/{run_path}"
        wandb_run = cls._get_wandb_run(run_path)
        if wandb_run:
            wandb_status = wandb_run.summary.get("status")
            if wandb_status == "succeeded":
                print(
                    f"Fine-tune job {fine_tune_id} has already been logged successfully at {wandb_run.url}"
                )
                if not force:
                    print(
                        'Use "--force" in the CLI or "force=True" in python if you want to overwrite previous run'
                    )
            if wandb_status != "succeeded" or force:
                print(
                    f"A new wandb run will be created for fine-tune job {fine_tune_id} and previous run will be overwritten"
                )
            else:
                return

        # retrieve results
        results_id = fine_tune["result_files"][0]["id"]
        results = File.download(id=results_id).decode("utf-8")

        # start a wandb run
        wandb.init(
            job_type="finetune",
            config=fine_tune,
            project=project,
            entity=entity,
            name=fine_tune_id,
            id=fine_tune_id,
            **kwargs_wandb_init,
        )

        # log results
        df_results = pd.read_csv(io.StringIO(results))
        for _, row in df_results.iterrows():
            metrics = {k: v for k, v in row.items() if not np.isnan(v)}
            step = metrics.pop("step")
            if step is not None:
                step = int(step)
            wandb.log(metrics, step=step)
        fine_tuned_model = fine_tune.get("fine_tuned_model")
        if fine_tuned_model is not None:
            wandb.summary["fine_tuned_model"] = fine_tuned_model

        # training/validation files
        cls._log_artifacts(fine_tune)

        # mark run as complete
        wandb.summary["status"] = "succeeded"

        wandb.finish()

    @classmethod
    def _ensure_logged_in(cls):
        if not cls._logged_in:
            if wandb.login():
                cls._logged_in = True
            else:
                raise Exception("You need to log in to wandb")

    @classmethod
    def _get_wandb_run(cls, run_path):
        cls._ensure_logged_in()
        try:
            if cls._wandb_api is None:
                cls._wandb_api = wandb.Api()
            return cls._wandb_api.run(run_path)
        except Exception as e:
            return False

    @classmethod
    def _log_artifacts(cls, fine_tune):
        training_file = (
            fine_tune["training_files"][0] if fine_tune.get("training_files") else None
        )
        validation_file = (
            fine_tune["validation_files"][0]
            if fine_tune.get("validation_files")
            else None
        )
        for file, prefix in ((training_file, "train"), (validation_file, "valid")):
            cls._log_artifact(file, prefix)

    @classmethod
    def _log_artifact(cls, file, prefix):
        file_id = file["id"]
        filename = Path(file["filename"]).name
        stem = Path(file["filename"]).stem

        # get file content
        try:
            file_content = File.download(id=file_id).decode("utf-8")
        except:
            print(
                f"File {file_id} could not be retrieved. Make sure you are allowed to download training/validation files"
            )
            return
        artifact = wandb.Artifact(f"{prefix}-{filename}", type=prefix, metadata=file)
        with artifact.new_file(filename, mode="w") as f:
            f.write(file_content)

        # create a Table
        try:
            table = cls._make_table(file_content)
            artifact.add(table, stem)
        except:
            print(f"File {file_id} could not be read as a valid JSON file")

        wandb.run.log_artifact(artifact, aliases=[file_id, "latest"])

    @classmethod
    def _make_table(cls, file_content):
        df = pd.read_json(io.StringIO(file_content), orient="records", lines=True)
        return wandb.Table(dataframe=df)
