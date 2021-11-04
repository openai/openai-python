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


class Logger:
    if not WANDB_AVAILABLE:
        print("Logging requires wandb to be installed. Run `pip install wandb`.")
    else:
        _wandb_api = wandb.Api()
        _logged_in = False

    @classmethod
    def log(
        cls,
        id=None,
        n_jobs=10,
        project="GPT-3",
        entity=None,
        **kwargs_wandb_init,
    ):
        # TODO: add docstring

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
            cls._log_fine_tune(fine_tune, project, entity, **kwargs_wandb_init)
        return "Command completed successfully"

    @classmethod
    def _log_fine_tune(cls, fine_tune, project, entity, **kwargs_wandb_init):
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
        if cls._get_wandb_run(run_path):
            print(
                f"Fine-tune job {fine_tune_id} has already been logged at {wandb_run.url}"
            )
            return
            # TODO: add a "force" argument

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

        # TODO: retrieve training/validation files if not already present
        # TODO: mark the run as successful so we can overwrite it in case it did not log properly
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
            return cls._wandb_api.run(run_path)
        except Exception as e:
            return False
