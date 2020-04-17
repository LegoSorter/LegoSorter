# import threading
import queue
import logging
import time
import subprocess


class Task:
    def __init__(self, id):
        # put blender task params here
        self.id = id
        self.width = 400
        self.height = 400
        self.samples = 6
        self.selected_gpu = "None"

    def get_command(self):
        part_file = '$LEGO_HOME/dataset/ldraw/parts/{}.dat'.format(self.id)
        out_dir = '$LEGO_HOME/dataset/render'
        ldraw_dir = '$LEGO_HOME/dataset/ldraw'
        scene = '$LEGO_HOME/dataset/scenes/simple.blend'
        log_file = '$LEGO_HOME/dataset/logs/{}.log'.format(self.id)
        command = 'blender --background --addons importldraw --python render.py -- --scene "{}" --width {} --height {} --part "{}" --output_dir "{}" --ldraw "{}" --gpu "{}" > {} 2>&1'.format(
            scene, self.width, self.height, part_file, out_dir, ldraw_dir, self.selected_gpu, log_file)
        return command

    def run(self, gpu):
        # put blender render here
        self.selected_gpu = gpu
        subprocess.call(self.get_command(), shell=True)

    def __str__(self):
        return str(self.get_command())


def worker(task, gpu, stats):
    """
     This function contains code that is executed by every thread.
    """
    # start time measurement
    start = time.time()

    # run task
    task.run(gpu)

    # measure time and put it into stats
    end = time.time()
    stats.put((gpu, (start, end)))
    logging.debug('[WORKER] TASK FINISHED: {} on {}'.format(task, gpu))


def select_gpu(gpu_tasks):
    """
     This function chooses the first available GPU in the system.
     If all GPUs are busy, it polls all active threads and takes
     the GPU after encountering first finished thread.
    """
    if not None in gpu_tasks.values():
        logging.debug('[SELECT_GPU] No gpu available! Starting polling...')

    # poll gpus for availability until any is available
    selected_gpu = ''
    while True:  # break if None in gpu_tasks.values()
        # go through each gpu_tasks item and check the status of enqueued task
        for gpu, task in gpu_tasks.items():
            # if GPU has an ongoing or finished task, we check it
            if isinstance(task, threading.Thread):
                # GPU has finished its task, we select it and break
                if not task.is_alive():
                    logging.debug('[SELECT_GPU] {} has finished its task. Selecting it.'.format(gpu))
                    gpu_tasks[gpu] = None
                    selected_gpu = gpu
                    break

            # if GPU is available, we select it and break
            elif isinstance(task, type(None)):
                logging.debug('[SELECT_GPU] {} has no tasks. Selecting it.'.format(gpu))
                selected_gpu = gpu
                break

            # task should be only threading.Thread or None
            else:
                raise TypeError('Task on {} is of invalid type: {}'.format(gpu, str(type(task))))

        if None in gpu_tasks.values():
            break

    return selected_gpu


def run_queue(q, gpus):
    """
     This function dispatches tasks from queue to GPUs.
    """
    start = time.time()
    gpu_tasks = {gpu: None for gpu in gpus}
    # target dictionary:
    # gpu_tasks = {
    #     "GPU0": None,
    #     "GPU1": None
    # }

    # initialize a thread-safe queue for writing statistics
    stat_queue = queue.Queue()

    while not q.empty():
        logging.info('Tasks left: {}'.format(q.qsize()))

        # get task from queue
        q_top = q.get()

        # selecting gpu
        selected_gpu = select_gpu(gpu_tasks)

        # starting thread
        thread = threading.Thread(target=worker, args=(q_top, selected_gpu, stat_queue))
        gpu_tasks[selected_gpu] = thread
        thread.start()

        logging.info('[OK] Task {} enqueued on {}'.format(q.qsize(), selected_gpu))

    # sync remaining threads
    for thread in gpu_tasks.values():
        if isinstance(task, threading.Thread):
            thread.join()
    end = time.time()
    logging.info('All tasks have finished. Time elapsed: {} s'.format(end - start))
    return stat_queue


def plot_stats(q):
    """
     This function plots statistics from run_queue(q) return value.
    """
    import matplotlib
    matplotlib.use('Agg')  # for ssh
    import matplotlib.pyplot as plt
    import numpy as np
    import datetime
    from matplotlib.ticker import FuncFormatter
    data = list(q.queue)
    d = dict()
    # get starting date
    start = min([i[1][0] for i in data])
    for gpu, time in data:
        if not gpu in d:
            d[gpu] = []
        # normalize
        newtime = (time[0] - start, time[1] - start)
        d[gpu].append(newtime)

    plt.rcdefaults()
    fig, ax = plt.subplots()

    gpus = d.keys()
    y_pos = np.arange(len(gpus))

    for idx, gpu in enumerate(d):
        for gpudata in d[gpu]:
            ax.barh(idx, gpudata[1] - gpudata[0], left=gpudata[0], align='center')

    # THIS IS A MESS
    formatter = FuncFormatter(
        lambda x_val, tick_pos: '{}'.format(datetime.datetime.utcfromtimestamp(x_val).strftime("%H:%M:%S")))
    ax.xaxis.set_major_formatter(formatter)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(gpus)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.grid(color='gray', linestyle='--', linewidth=0.5, axis='x')
    ax.set_xlabel('Time (HH-MM-SS)')
    ax.set_title('GPU utilization')
    #   plt.show()
    plt.savefig('exec_stats.png', dpi=300)


if __name__ == "__main__":
    """
     This is the entry point of the application.
    """
    # set logging parameters
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # create a task queue
    task_queue = queue.Queue()

    # fill task queue with 50 tasks
    for i in range(20):
        task = Task(i)
        task_queue.put(task)

    # define gpus
    # TODO: detect gpus
    gpus = ['CUDA_Tesla K20m_0000:05:00', 'CUDA_Tesla K20m_0000:42:00']

    # run task queue
    stats = run_queue(task_queue, gpus)

    # plot run statistics
    plot_stats(stats)
