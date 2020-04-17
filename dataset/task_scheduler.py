import threading
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
        self.shift = 0.6
        self.selected_gpu = "None"

    def get_command(self):
        part_file = '$LEGO_HOME/dataset/ldraw/parts/{}.dat'.format(self.id)
        out_dir = '$LEGO_HOME/dataset/render'
        ldraw_dir = '$LEGO_HOME/dataset/ldraw'
        scene = '$LEGO_HOME/dataset/scenes/simple.blend'
        log_file = '$LEGO_HOME/dataset/logs/{}.log'.format(self.id)
        command = 'blender --background --addons importldraw --python render.py -- --scene "{}" --width {} --height {} --shift {} --part "{}" --output_dir "{}" --ldraw "{}" --gpu "{}" > {} 2>&1'.format(
            scene, self.width, self.height, self.shift, part_file, out_dir, ldraw_dir, self.selected_gpu, log_file)
        return command

    def run(self, gpu):
        # blender render runs here
        self.selected_gpu = gpu
        subprocess.call(self.get_command(), shell=True)  # TODO: change to subprocess.run with newer python

    def __str__(self):
        return str('Render {}.dat, {}x{}, {} samples, {} shift'.format(self.id, self.width, self.height, self.samples,
                                                                       self.shift))


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


def select_gpu(gpu_threads):
    """
     This function chooses the first available GPU in the system.
     If all GPUs are busy, it polls all active threads and takes
     the GPU after encountering first finished thread.
    """
    if not None in gpu_threads.values():
        logging.debug('[SELECT_GPU] No gpu available! Starting polling...')

    # poll gpus for availability until any is available
    selected_gpu = ''
    while True:  # break if None in gpu_threads.values()
        # go through each gpu_tasks item and check the status of enqueued task
        for gpu, thread in gpu_threads.items():
            # if GPU has a thread, we check it
            if isinstance(thread, threading.Thread):
                # GPU has finished its task, we select it and break
                if not thread.is_alive():
                    logging.debug('[SELECT_GPU] {} has finished its task. Selecting it.'.format(gpu))
                    gpu_threads[gpu] = None
                    selected_gpu = gpu
                    break

            # if GPU is available, we select it and break
            elif isinstance(thread, type(None)):
                logging.debug('[SELECT_GPU] {} has no tasks. Selecting it.'.format(gpu))
                selected_gpu = gpu
                break

            # thread should be only threading.Thread or None
            else:
                raise TypeError('Task on {} is of invalid type: {}'.format(gpu, str(type(thread))))

        if None in gpu_threads.values():
            break

    return selected_gpu


def run_queue(q, gpus):
    """
     This function dispatches tasks from queue to GPUs.
    """
    start = time.time()
    gpu_threads = {gpu: None for gpu in gpus}
    # target dictionary:
    # gpu_threads = {
    #     "GPU0": None,
    #     "GPU1": None
    # }

    # initialize a thread-safe queue for writing statistics
    stat_queue = queue.Queue()

    while not q.empty():
        logging.info('Tasks left in queue: {}'.format(q.qsize()))

        # get task from queue
        top_task = q.get()

        # selecting gpu
        selected_gpu = select_gpu(gpu_threads)

        # starting thread
        thread = threading.Thread(target=worker, args=(top_task, selected_gpu, stat_queue))
        gpu_threads[selected_gpu] = thread
        thread.start()

        logging.info('[OK] Task "{}" enqueued on {}'.format(task, selected_gpu))

    logging.info('All tasks have been dispatched, waiting for completion...')
    # sync remaining threads
    while True:
        if not any(isinstance(t, threading.Thread) and t.is_alive() for t in gpu_threads.values()):
            break
        #    thread.join() doesnt work for some reason on python 3.4

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
    for i in range(1, 11):
        task = Task(i)
        task_queue.put(task)

    # define gpus
    # TODO: detect gpus
    gpus = ['CUDA_Tesla K20m_0000:05:00', 'CUDA_Tesla K20m_0000:42:00']

    # run task queue
    stats = run_queue(task_queue, gpus)

    # plot run statistics
    plot_stats(stats)
