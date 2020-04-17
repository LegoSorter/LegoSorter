import threading
import queue
import logging
import time


class Task:
    def __init__(self, id):
        # put blender task params here
        import numpy
        self.id = id
        self.wait_time = numpy.random.randint(1, 3)

    def run(self, gpu):
        # put blender render here
        time.sleep(self.wait_time)

    def __str__(self):
        return str(self.id)


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
    logging.debug(f'[WORKER] TASK FINISHED: {task} on {gpu}')


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
                    logging.debug(f'[SELECT_GPU] {gpu} has finished its task. Selecting it.')
                    gpu_tasks[gpu] = None
                    selected_gpu = gpu
                    break

            # if GPU is available, we select it and break
            elif isinstance(task, type(None)):
                logging.debug(f'[SELECT_GPU] {gpu} has no tasks. Selecting it.')
                selected_gpu = gpu
                break

            # task should be only threading.Thread or None
            else:
                raise TypeError(f'Task on {gpu} is of invalid type: {str(type(task))}')

        if None in gpu_tasks.values():
            break

    return selected_gpu


def run_queue(q, gpus):
    """
     This function dispatches tasks from queue to GPUs.
    """
    gpu_tasks = {gpu: None for gpu in gpus}
    # target dictionary:
    # gpu_tasks = {
    #     "GPU0": None,
    #     "GPU1": None
    # }

    # initialize a thread-safe queue for writing statistics
    stat_queue = queue.Queue()

    while not q.empty():
        logging.info(f'Tasks left: {q.qsize()}')

        # get task from queue
        q_top = q.get()

        # selecting gpu
        selected_gpu = select_gpu(gpu_tasks)

        # starting thread
        thread = threading.Thread(target=worker, args=(q_top, selected_gpu, stat_queue))
        gpu_tasks[selected_gpu] = thread
        thread.start()

        logging.info(f'[OK] Task {q_top} enqueued on {selected_gpu}')

    # sync remaining threads
    for thread in gpu_tasks.values():
        thread.join()
    logging.info('All tasks have finished.')
    return stat_queue


def plot_stats(q):
    """
     This function plots statistics from run_queue(q) return value.
    """
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
        lambda x_val, tick_pos: f'{datetime.datetime.utcfromtimestamp(x_val).strftime("%H:%M:%S")}')
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
    gpus = ['GPU0', 'GPU1', 'GPU2', 'GPU3']

    # run task queue
    stats = run_queue(task_queue, gpus)

    # plot run statistics
    plot_stats(stats)
