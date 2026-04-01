from experiment_launcher import Launcher, is_local

# launcher options
CONDA_ENV = 'el'

LOCAL = is_local()
TEST = False
USE_GPU = True

# Number of seeds for each experiment configuration (added with add_experiment)
N_SEEDS_EXP_CONFIG = 10

# Number of experiments configurations to run in parallel.
# This is mostly used for running several configurations in the same GPU.
# If you only use the CPU, you can set this to 1.
N_EXPS_IN_PARALLEL = 5

# options only for slurm jobs
MEMORY_SINGLE_JOB = 1000
N_CORES_SINGLE_JOB = 2
# Ideally, you want to use less cpu cores if experiment configurations run in parallel.
# In LOCAL mode this is ignored and all cores will be used.
N_CPU_CORES = N_EXPS_IN_PARALLEL * N_CORES_SINGLE_JOB
MEMORY_PER_CPU_CORE = N_EXPS_IN_PARALLEL * MEMORY_SINGLE_JOB // N_CPU_CORES
PARTITION = 'amd2,amd'  # 'amd', 'rtx'
GRES = 'gpu:1' if USE_GPU else None  # gpu:rtx2080:1, gpu:rtx3080:1

# Instantiate the launcher
launcher = Launcher(
    exp_name='test_launcher',
    exp_file='test',
    # project_name='project01234',  # only for hrz cluster
    n_seeds=N_SEEDS_EXP_CONFIG,
    n_exps_in_parallel=N_EXPS_IN_PARALLEL,
    n_cores=N_CPU_CORES,
    memory_per_core=MEMORY_PER_CPU_CORE,
    days=2,
    hours=23,
    minutes=59,
    seconds=0,
    partition=PARTITION,
    gres=GRES,
    use_job_array_seeds=False,
    conda_env=CONDA_ENV,
    use_timestamp=True,
    compact_dirs=False
)

# Add the experiment configurations
tensor_sizes_l = [1000000 + i for i in range(5)]

# Optional arguments for Weights and Biases
wandb_options = dict(
    wandb_mode='disabled',  # "online", "offline" or "disabled"
    wandb_entity='joaocorreiacarvalho',
    wandb_project='test_experiment_launcher_config_files'
)

for tensor_size in tensor_sizes_l:
    launcher.add_experiment(
        # A subdirectory will be created for parameters with a trailing double underscore.
        tensor_size__=tensor_size,

        debug=False,

        **wandb_options,
        wandb_group=f'test_group-el-{tensor_size}',
    )

# Run the experiments
launcher.run(LOCAL, TEST)
